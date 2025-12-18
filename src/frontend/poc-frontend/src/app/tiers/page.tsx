"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface TierInfo {
  tier: string
  contribution_range: string
  contribution_amount: number
  synth_allocation: number
  benefits: {
    dashboard_access: boolean
    early_insight: boolean
    voting_rights: boolean
    advisory_access: boolean
    strategic_influence: boolean
    reserved_slots: boolean
  }
}

interface ContributorTier {
  tier: string
  contribution_amount: number
  synth_allocation: number
  registered_at: string
  benefits: {
    dashboard_access: boolean
    early_insight: boolean
    voting_rights: boolean
    advisory_access: boolean
    strategic_influence: boolean
    reserved_slots: boolean
  }
}

interface TierStatistics {
  total_contributions: number
  total_contributors: number
  tier_breakdown: {
    [key: string]: {
      count: number
      total_contributed: number
      benefits: any
    }
  }
  founders_allocation: {
    total: number
    used: number
    remaining: number
    utilization_percentage: number
  }
}

export default function TiersPage() {
  const [contributionAmount, setContributionAmount] = useState<string>('')
  const [eligibleTiers, setEligibleTiers] = useState<TierInfo[]>([])
  const [tierStatistics, setTierStatistics] = useState<TierStatistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  // Load tier statistics on mount
  useEffect(() => {
    loadTierStatistics()
  }, [])

  const loadTierStatistics = async () => {
    try {
      const response = await fetch('/api/tiers/statistics')
      if (response.ok) {
        const data = await response.json()
        setTierStatistics(data)
      }
    } catch (err) {
      console.error('Failed to load tier statistics:', err)
    }
  }

  const validateContribution = async () => {
    if (!contributionAmount || isNaN(Number(contributionAmount))) {
      setError('Please enter a valid contribution amount')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`/api/tiers/eligible?amount=${contributionAmount}`)
      if (response.ok) {
        const data = await response.json()
        setEligibleTiers(data.eligible_tiers || [])
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to validate contribution')
      }
    } catch (err) {
      setError('Failed to validate contribution')
      console.error('Validation error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatTokens = (amount: number) => {
    if (amount >= 1e12) {
      return `${(amount / 1e12).toFixed(2)}T SYNTH`
    } else if (amount >= 1e9) {
      return `${(amount / 1e9).toFixed(2)}B SYNTH`
    } else if (amount >= 1e6) {
      return `${(amount / 1e6).toFixed(2)}M SYNTH`
    } else {
      return `${amount.toLocaleString()} SYNTH`
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'copper': return 'bg-orange-500'
      case 'silver': return 'bg-gray-400'
      case 'gold': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getTierBadgeVariant = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'copper': return 'secondary'
      case 'silver': return 'outline'
      case 'gold': return 'default'
      default: return 'secondary'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Contributor Tiers</h1>
          <p className="text-gray-600">
            Join the Syntheverse ecosystem with financial contributions. Choose from Copper, Silver, or Gold tiers
            to support FractiAI Research and unlock exclusive benefits per Blueprint §4.2.
          </p>
        </div>

        {/* Tier Statistics */}
        {tierStatistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Total Contributors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{tierStatistics.total_contributors}</div>
                <p className="text-sm text-gray-600">
                  {formatCurrency(tierStatistics.total_contributions)} contributed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Founders Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {tierStatistics.founders_allocation.utilization_percentage.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">
                  {formatTokens(tierStatistics.founders_allocation.used)} / {formatTokens(tierStatistics.founders_allocation.total)} used
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Tier Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {Object.entries(tierStatistics.tier_breakdown).map(([tier, data]) => (
                    <div key={tier} className="flex justify-between text-sm">
                      <span className="capitalize">{tier}</span>
                      <span>{data.count} contributors</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Contribution Validator */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Check Tier Eligibility</CardTitle>
            <CardDescription>
              Enter a contribution amount to see which tiers you're eligible for and the SYNTH allocation you'll receive.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <Label htmlFor="contribution">Contribution Amount (USD)</Label>
                <Input
                  id="contribution"
                  type="number"
                  placeholder="Enter amount (e.g., 25000)"
                  value={contributionAmount}
                  onChange={(e) => setContributionAmount(e.target.value)}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={validateContribution} disabled={loading}>
                  {loading ? 'Checking...' : 'Check Eligibility'}
                </Button>
              </div>
            </div>

            {error && (
              <div className="text-red-600 mb-4 p-3 bg-red-50 rounded-md">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Eligible Tiers */}
        {eligibleTiers.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Eligible Tiers</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {eligibleTiers.map((tierInfo, index) => (
                <Card key={index} className="relative">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="capitalize flex items-center gap-2">
                        <Badge className={getTierColor(tierInfo.tier)}>
                          {tierInfo.tier}
                        </Badge>
                      </CardTitle>
                    </div>
                    <CardDescription>{tierInfo.contribution_range}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-gray-600">SYNTH Allocation</div>
                        <div className="font-semibold">{formatTokens(tierInfo.synth_allocation)}</div>
                      </div>

                      <div>
                        <div className="text-sm text-gray-600 mb-2">Benefits</div>
                        <div className="space-y-1 text-sm">
                          {tierInfo.benefits.dashboard_access && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Dashboard Access
                            </div>
                          )}
                          {tierInfo.benefits.early_insight && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Early Insights
                            </div>
                          )}
                          {tierInfo.benefits.voting_rights && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Voting Rights
                            </div>
                          )}
                          {tierInfo.benefits.advisory_access && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Advisory Access
                            </div>
                          )}
                          {tierInfo.benefits.strategic_influence && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Strategic Influence
                            </div>
                          )}
                          {tierInfo.benefits.reserved_slots && (
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Reserved Slots
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Tier Information */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Copper Tier */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Badge className="bg-orange-500">Copper</Badge>
                <span>$10K-$25K</span>
              </CardTitle>
              <CardDescription>Foundation tier for early supporters</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div>• Dashboard access</div>
                <div>• Early insights</div>
                <div>• 0.05-0.25% SYNTH allocation</div>
              </div>
            </CardContent>
          </Card>

          {/* Silver Tier */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Badge variant="outline">Silver</Badge>
                <span>$50K-$100K</span>
              </CardTitle>
              <CardDescription>Enhanced tier with voting rights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div>• All Copper benefits</div>
                <div>• Voting rights</div>
                <div>• Advisory access</div>
                <div>• 0.25-1% SYNTH allocation</div>
              </div>
            </CardContent>
          </Card>

          {/* Gold Tier */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Badge className="bg-yellow-500">Gold</Badge>
                <span>$250K-$500K</span>
              </CardTitle>
              <CardDescription>Premium tier with strategic influence</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div>• All Silver benefits</div>
                <div>• Strategic influence</div>
                <div>• Reserved slots</div>
                <div>• 1-3% SYNTH allocation</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">About Contributor Tiers</h3>
          <p className="text-sm text-gray-700">
            Financial contributions to Syntheverse tiers support the FractiAI Research Team and platform operations.
            All tiers receive SYNTH token allocations from the Founders' 5% offering. Benefits and allocations
            are designed per Blueprint §4.2 specifications.
          </p>
        </div>
      </div>
    </div>
  )
}
