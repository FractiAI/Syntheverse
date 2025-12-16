'use client'

import { useEffect, useState } from 'react'
import { api, type ArchiveStatistics, type TokenomicsStatistics, type EpochInfo } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { formatNumber, formatDate } from '@/lib/utils'
import { Award, Users, FileText, TrendingUp, Coins } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = {
  gold: '#FCD34D',
  silver: '#94A3B8',
  copper: '#CD7F32',
}

export default function DashboardPage() {
  const [stats, setStats] = useState<ArchiveStatistics | null>(null)
  const [tokenomics, setTokenomics] = useState<TokenomicsStatistics | null>(null)
  const [epochInfo, setEpochInfo] = useState<EpochInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      setLoading(true)
      const [archiveStats, tokenStats, epoch] = await Promise.all([
        api.getArchiveStatistics(),
        api.getTokenomicsStatistics(),
        api.getEpochInfo(),
      ])
      setStats(archiveStats)
      setTokenomics(tokenStats)
      setEpochInfo(epoch)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading...</div>
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

  const statusData = stats
    ? Object.entries(stats.status_counts).map(([status, count]) => ({
        status: status.charAt(0).toUpperCase() + status.slice(1),
        count,
      }))
    : []

  const metalData = stats
    ? Object.entries(stats.metal_counts).map(([metal, count]) => ({
        name: metal.charAt(0).toUpperCase() + metal.slice(1),
        value: count,
        color: COLORS[metal as keyof typeof COLORS] || '#888',
      }))
    : []

  const epochData = epochInfo
    ? Object.entries(epochInfo.epochs).map(([epoch, data]) => ({
        epoch: epoch.charAt(0).toUpperCase() + epoch.slice(1),
        balance: data.balance / 1e12, // Convert to trillions
        distribution: data.distribution_percent,
      }))
    : []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Contributor Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of contributions, tokenomics, and system status
        </p>
        <div className="flex items-center space-x-4 mt-3">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium">Blockchain Active</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <span>Foundry + Anvil + Hardhat</span>
            <span>•</span>
            <span>Local Network</span>
          </div>
        </div>
      </div>

      {/* Blockchain Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">Blockchain Network</h3>
            <p className="text-sm text-muted-foreground">Syntheverse Blockmine Status</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-green-600">Online</span>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Network</p>
            <p className="font-mono">Anvil (Chain ID: 31337)</p>
          </div>
          <div>
            <p className="text-muted-foreground">Tech Stack</p>
            <p className="font-medium">Foundry + Anvil + Hardhat</p>
          </div>
          <div>
            <p className="text-muted-foreground">SYNTH Contract</p>
            <p className="font-mono text-xs">0x9fE4...6e0</p>
          </div>
          <div>
            <p className="text-muted-foreground">POC Registry</p>
            <p className="font-mono text-xs">0xCf7E...Fc9</p>
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Contributions</p>
              <p className="text-2xl font-bold mt-1">{stats?.total_contributions || 0}</p>
            </div>
            <FileText className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Contributors</p>
              <p className="text-2xl font-bold mt-1">{stats?.unique_contributors || 0}</p>
            </div>
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Distributed</p>
              <p className="text-2xl font-bold mt-1">
                {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : '0'}T
              </p>
            </div>
            <Coins className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Current Epoch</p>
              <p className="text-2xl font-bold mt-1 capitalize">
                {epochInfo?.current_epoch || 'N/A'}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Contribution Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="hsl(var(--primary))" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Metal Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={metalData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {metalData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Epoch Balances */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Epoch Distribution</h3>
        <div className="space-y-4">
          {epochData.map((epoch) => (
            <div key={epoch.epoch} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{epoch.epoch}</span>
                <span className="text-muted-foreground">
                  {formatNumber(epoch.balance)}T ({epoch.distribution.toFixed(2)}%)
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${epoch.distribution}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Last Updated */}
      {stats && (
        <div className="text-sm text-muted-foreground text-center">
          Last updated: {formatDate(stats.last_updated)}
        </div>
      )}
    </div>
  )
}
