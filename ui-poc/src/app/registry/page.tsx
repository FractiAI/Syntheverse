'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api, type Contribution } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { formatDate, truncateHash } from '@/lib/utils'
import { FileText, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

const COLORS = {
  gold: '#FCD34D',
  silver: '#94A3B8',
  copper: '#CD7F32',
}

function MetalIndicator({ metals }: { metals: string[] }) {
  return (
    <div className="flex gap-1">
      {metals.map((metal) => (
        <div
          key={metal}
          className="w-3 h-3 rounded-full"
          style={{
            backgroundColor: COLORS[metal as keyof typeof COLORS] || '#888',
          }}
          title={metal.charAt(0).toUpperCase() + metal.slice(1)}
        />
      ))}
    </div>
  )
}

export default function RegistryPage() {
  const router = useRouter()
  const [contributions, setContributions] = useState<Contribution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadContributions()
  }, [])

  async function loadContributions() {
    try {
      setLoading(true)
      // Get all contributions, sorted by creation date (append-only chronological order)
      const data = await api.getContributions()
      // Sort by created_at descending (newest first)
      const sorted = [...data].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      setContributions(sorted)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load registry')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading registry...</div>
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
        <h1 className="text-3xl font-bold">Contribution Registry</h1>
        <p className="text-muted-foreground mt-2">
          Append-only chronological log of all contributions
        </p>
      </div>

      {/* Registry Timeline */}
      <div className="space-y-4">
        {contributions.map((contribution, index) => (
          <Card
            key={contribution.submission_hash}
            className="hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => router.push(`/submission/${contribution.submission_hash}`)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1 space-y-3">
                  <div className="flex items-start space-x-4">
                    {/* Registry Index */}
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-muted flex items-center justify-center font-mono text-sm font-semibold">
                      #{contributions.length - index}
                    </div>

                    {/* Content */}
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold">{contribution.title}</h3>
                        <MetalIndicator metals={contribution.metals} />
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${
                            contribution.status === 'qualified'
                              ? 'bg-green-100 text-green-800'
                              : contribution.status === 'unqualified'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {contribution.status}
                        </span>
                      </div>

                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <span className="font-mono">
                          {truncateHash(contribution.submission_hash, 8)}
                        </span>
                        <span>•</span>
                        <span className="font-mono">
                          {truncateHash(contribution.contributor, 8)}
                        </span>
                        <span>•</span>
                        <span>{formatDate(contribution.created_at)}</span>
                      </div>

                      {contribution.metadata?.pod_score && (
                        <div className="text-sm">
                          <span className="font-medium">PoC Score: </span>
                          <span>{contribution.metadata.pod_score.toFixed(0)}</span>
                        </div>
                      )}

                      {contribution.text_content && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {contribution.text_content.slice(0, 200)}...
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <Button variant="ghost" size="icon" className="flex-shrink-0">
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {contributions.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No contributions in registry yet</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Registry Stats */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{contributions.length}</p>
              <p className="text-sm text-muted-foreground">Total Entries</p>
            </div>
            <div>
              <p className="text-2xl font-bold">
                {contributions.filter((c) => c.status === 'qualified').length}
              </p>
              <p className="text-sm text-muted-foreground">Qualified</p>
            </div>
            <div>
              <p className="text-2xl font-bold">
                {new Set(contributions.map((c) => c.contributor)).size}
              </p>
              <p className="text-sm text-muted-foreground">Unique Contributors</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
