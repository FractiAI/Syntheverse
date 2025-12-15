'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table'
import { api, type Contribution } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate, truncateHash } from '@/lib/utils'
import { ArrowUpDown, Search, FileText, ChevronLeft, ChevronRight } from 'lucide-react'

type ContributionTableData = Contribution & {
  metalString: string
  statusDisplay: string
}

const COLORS = {
  gold: '#FCD34D',
  silver: '#94A3B8',
  copper: '#CD7F32',
}

function MetalBadge({ metals }: { metals: string[] }) {
  return (
    <div className="flex gap-1">
      {metals.map((metal) => (
        <span
          key={metal}
          className="px-2 py-0.5 rounded text-xs font-medium"
          style={{
            backgroundColor: `${COLORS[metal as keyof typeof COLORS] || '#888'}20`,
            color: COLORS[metal as keyof typeof COLORS] || '#888',
          }}
        >
          {metal.charAt(0).toUpperCase() + metal.slice(1)}
        </span>
      ))}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const statusColors: Record<string, string> = {
    qualified: 'bg-green-100 text-green-800',
    unqualified: 'bg-red-100 text-red-800',
    evaluating: 'bg-blue-100 text-blue-800',
    submitted: 'bg-yellow-100 text-yellow-800',
    draft: 'bg-gray-100 text-gray-800',
    archived: 'bg-gray-100 text-gray-600',
  }

  return (
    <span
      className={`px-2 py-0.5 rounded text-xs font-medium ${
        statusColors[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
      }`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function ExplorerPage() {
  const router = useRouter()
  const [contributions, setContributions] = useState<Contribution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  useEffect(() => {
    loadContributions()
  }, [])

  async function loadContributions() {
    try {
      setLoading(true)
      const data = await api.getContributions()
      setContributions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contributions')
    } finally {
      setLoading(false)
    }
  }

  const tableData = useMemo<ContributionTableData[]>(
    () =>
      contributions.map((c) => ({
        ...c,
        metalString: c.metals.join(', '),
        statusDisplay: c.status,
      })),
    [contributions]
  )

  const columns = useMemo<ColumnDef<ContributionTableData>[]>(
    () => [
      {
        accessorKey: 'title',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-8 px-2"
          >
            Title
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => (
          <div
            className="font-medium cursor-pointer hover:underline"
            onClick={() => router.push(`/submission/${row.original.submission_hash}`)}
          >
            {row.getValue('title')}
          </div>
        ),
      },
      {
        accessorKey: 'contributor',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-8 px-2"
          >
            Contributor
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => (
          <div className="font-mono text-sm">{truncateHash(row.getValue('contributor'), 8)}</div>
        ),
      },
      {
        accessorKey: 'metals',
        header: 'Metals',
        cell: ({ row }) => <MetalBadge metals={row.original.metals} />,
        enableSorting: false,
      },
      {
        accessorKey: 'status',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-8 px-2"
          >
            Status
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => <StatusBadge status={row.getValue('status')} />,
      },
      {
        accessorKey: 'metadata.pod_score',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-8 px-2"
          >
            PoC Score
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const score = row.original.metadata?.pod_score
          return score ? score.toFixed(0) : '-'
        },
      },
      {
        accessorKey: 'created_at',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-8 px-2"
          >
            Created
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => formatDate(row.getValue('created_at')),
      },
    ],
    [router]
  )

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading contributions...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-destructive">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Submissions Explorer</h1>
        <p className="text-muted-foreground mt-2">
          Browse and search all contributions in the archive
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Contributions</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  value={globalFilter ?? ''}
                  onChange={(e) => setGlobalFilter(e.target.value)}
                  placeholder="Search contributions..."
                  className="pl-8 pr-4 py-2 border rounded-md w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="w-full">
              <thead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id} className="border-b">
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="h-12 px-4 text-left align-middle font-medium text-muted-foreground"
                      >
                        {header.isPlaceholder
                          ? null
                          : flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b transition-colors hover:bg-muted/50 cursor-pointer"
                    onClick={() => router.push(`/submission/${row.original.submission_hash}`)}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="p-4 align-middle">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-muted-foreground">
              Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
              {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                tableData.length
              )}{' '}
              of {tableData.length} contributions
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
