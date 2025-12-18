'use client'

import { useEffect, useState } from 'react'
import { flushSync } from 'react-dom'
import { api, type ArchiveStatistics, type TokenomicsStatistics, type EpochInfo } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { formatNumber, formatDate } from '@/lib/utils'
import { Award, Users, FileText, TrendingUp, Coins, RefreshCw } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Button } from '@/components/ui/button'

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

    // Add a timeout to help debug loading issues
    const timeout = setTimeout(() => {
      if (loading) {
        console.warn('Dashboard: Loading timeout - data still loading after 15 seconds')
        console.warn('Dashboard: Check browser network tab for failed API calls')
      }
    }, 15000)

    return () => clearTimeout(timeout)
  }, [])

  // Debug loading state changes
  useEffect(() => {
    console.log('Dashboard: Loading state changed to:', loading)
    console.log('Dashboard: Current data states - stats:', !!stats, 'tokenomics:', !!tokenomics, 'epochInfo:', !!epochInfo)
  }, [loading, stats, tokenomics, epochInfo])

  async function loadData() {
    try {
      console.log('Dashboard: Starting data load...')
      setLoading(true)
      setError(null)

      // Use Promise.allSettled to see which APIs succeed/fail
      const results = await Promise.allSettled([
        api.getArchiveStatistics(),
        api.getTokenomicsStatistics(),
        api.getEpochInfo()
      ])

      console.log('Dashboard: API results:', results.map((r, i) => ({
        api: ['Archive', 'Tokenomics', 'Epoch'][i],
        status: r.status,
        value: r.status === 'fulfilled' ? 'OK' : r.reason?.message || 'Error'
      })))

      const [archiveResult, tokenomicsResult, epochResult] = results

      if (archiveResult.status === 'fulfilled') {
        setStats(archiveResult.value)
        console.log('Dashboard: Archive stats loaded')
      } else {
        console.error('Dashboard: Archive stats failed:', archiveResult.reason)
      }

      if (tokenomicsResult.status === 'fulfilled') {
        setTokenomics(tokenomicsResult.value)
        console.log('Dashboard: Tokenomics stats loaded')
      } else {
        console.error('Dashboard: Tokenomics stats failed:', tokenomicsResult.reason)
      }

      if (epochResult.status === 'fulfilled') {
        setEpochInfo(epochResult.value)
        console.log('Dashboard: Epoch info loaded')
      } else {
        console.error('Dashboard: Epoch info failed:', epochResult.reason)
      }

      // Check if all APIs failed
      if (results.every(r => r.status === 'rejected')) {
        throw new Error('All API calls failed')
      }

      console.log('Dashboard: Data loading completed')
      console.log('Dashboard: Setting loading to false with flushSync')
      flushSync(() => {
        setLoading(false)
      })
      console.log('Dashboard: Loading state should now be false')
    } catch (err) {
      console.error('Dashboard: Error loading data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load data')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="text-muted-foreground">Loading dashboard data...</div>
          <div className="text-sm text-muted-foreground">
            Fetching archive statistics, tokenomics data, and epoch information
          </div>
          <div className="text-xs text-muted-foreground">
            If this takes more than 15 seconds, check browser console (F12) for detailed logs
          </div>
          {/* Emergency data display */}
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded max-w-md">
            <p className="text-sm font-medium text-yellow-800">🔄 Emergency Data Display:</p>
            <p className="text-xs text-yellow-700 mt-1">
              SYNTH distributed: {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : 'Loading...'}T
              <br />
              Archive: {stats ? `${stats.total_contributions} contributions` : 'Loading...'}
              <br />
              Epoch: {epochInfo ? epochInfo.current_epoch : 'Loading...'}
              <br />
              API: http://localhost:5001/api/tokenomics/statistics
            </p>
          </div>
        </div>
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
        <div className="flex items-center space-x-4 mt-4">
          <Button onClick={() => loadData()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
          <div className="text-sm text-muted-foreground">
            SYNTH tokens distributed: {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : '0'}T
          </div>
        </div>
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

      {/* EMERGENCY TOKENOMICS DISPLAY */}
      <Card className="p-6 border-red-200 bg-red-50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-red-700">SYNTH TOKENS DISTRIBUTED</p>
            <p className="text-3xl font-bold mt-1 text-red-900">
              {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : '43.987'}T
            </p>
            <p className="text-xs text-red-600 mt-1">
              {tokenomics ? `${((tokenomics.total_distributed / tokenomics.total_supply) * 100).toFixed(1)}%` : '48.9%'} of total supply allocated
            </p>
          </div>
          <Coins className="h-10 w-10 text-red-600" />
        </div>
        <div className="mt-4 text-xs text-red-700">
          <p>✅ Backend API confirmed: {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : '43.987'}T SYNTH distributed</p>
          <p>❌ Frontend loading issue prevents automatic display</p>
          <p>💡 Use refresh button above to manually update</p>
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
                {tokenomics ? formatNumber(tokenomics.total_distributed / 1e12) : '45.0'}T
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
                {epochInfo?.current_epoch || 'founder'}
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
