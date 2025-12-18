"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Trophy, Medal, Award, Crown, Star } from 'lucide-react'

interface ContributorRecognition {
  contributor: string
  recognition_level: string
  priority_score: number
  submission_order: number
  badge_count: number
  qualified_submissions: number
}

interface RecognitionStatistics {
  total_contributors: number
  total_badges_awarded: number
  recognition_level_distribution: { [key: string]: number }
  badge_distribution: { [key: string]: number }
  pioneer_count: number
  category_pioneers: number
}

interface LegacyContributor {
  contributor: string
  submission_order: number
  first_contribution: string
  recognition_level: string
  legacy_status: string
  historical_significance: string
}

export default function RecognitionPage() {
  const [leaderboard, setLeaderboard] = useState<ContributorRecognition[]>([])
  const [statistics, setStatistics] = useState<RecognitionStatistics | null>(null)
  const [legacyContributors, setLegacyContributors] = useState<LegacyContributor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRecognitionData()
  }, [])

  const loadRecognitionData = async () => {
    try {
      const [leaderboardRes, statsRes, legacyRes] = await Promise.all([
        fetch('/api/recognition/leaderboard?limit=50'),
        fetch('/api/recognition/statistics'),
        fetch('/api/recognition/legacy-contributors?limit=10')
      ])

      if (leaderboardRes.ok) {
        const data = await leaderboardRes.json()
        setLeaderboard(data.leaderboard || [])
      }

      if (statsRes.ok) {
        const data = await statsRes.json()
        setStatistics(data)
      }

      if (legacyRes.ok) {
        const data = await legacyRes.json()
        setLegacyContributors(data.legacy_contributors || [])
      }
    } catch (error) {
      console.error('Failed to load recognition data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecognitionIcon = (level: string) => {
    switch (level) {
      case 'legendary_pioneer': return <Crown className="w-5 h-5 text-yellow-500" />
      case 'epic_founder': return <Trophy className="w-5 h-5 text-purple-500" />
      case 'master_contributor': return <Medal className="w-5 h-5 text-blue-500" />
      case 'recognized_contributor': return <Award className="w-5 h-5 text-green-500" />
      default: return <Star className="w-5 h-5 text-gray-500" />
    }
  }

  const getRecognitionColor = (level: string) => {
    switch (level) {
      case 'legendary_pioneer': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'epic_founder': return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'master_contributor': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'recognized_contributor': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatContributorId = (id: string) => {
    return `${id.slice(0, 6)}...${id.slice(-4)}`
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">"I Was Here First" Recognition</h1>
          <p className="text-gray-600">
            Celebrating early contributors to Syntheverse with priority recognition, enhanced visibility, and legacy status per Blueprint §1.4.
          </p>
        </div>

        {/* Statistics Overview */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Total Contributors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics.total_contributors}</div>
                <p className="text-sm text-gray-600">Recognized participants</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Badges Awarded</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics.total_badges_awarded}</div>
                <p className="text-sm text-gray-600">Achievement recognitions</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Pioneer Count</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics.pioneer_count}</div>
                <p className="text-sm text-gray-600">First 10 contributors</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Category Pioneers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics.category_pioneers}</div>
                <p className="text-sm text-gray-600">First in research areas</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recognition Leaderboard */}
          <Card>
            <CardHeader>
              <CardTitle>Recognition Leaderboard</CardTitle>
              <CardDescription>
                Top contributors ranked by priority score, combining early participation, badges, and activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {leaderboard.slice(0, 20).map((contributor, index) => (
                  <div key={contributor.contributor} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-lg w-6">#{index + 1}</span>
                        {getRecognitionIcon(contributor.recognition_level)}
                      </div>
                      <div>
                        <div className="font-medium">{formatContributorId(contributor.contributor)}</div>
                        <div className="text-sm text-gray-600">
                          {contributor.qualified_submissions} submissions • {contributor.badge_count} badges
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getRecognitionColor(contributor.recognition_level)}>
                        {contributor.recognition_level.replace('_', ' ')}
                      </Badge>
                      <div className="text-sm text-gray-600 mt-1">
                        Priority: {contributor.priority_score}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Legacy Contributors */}
          <Card>
            <CardHeader>
              <CardTitle>Legacy Contributors</CardTitle>
              <CardDescription>
                Celebrating the earliest Syntheverse participants who established the foundation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {legacyContributors.map((contributor) => (
                  <div key={contributor.contributor} className="border-l-4 border-yellow-400 pl-4 py-2">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Crown className="w-5 h-5 text-yellow-500" />
                        <span className="font-bold">#{contributor.submission_order}</span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {contributor.legacy_status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600 mb-1">
                      {formatContributorId(contributor.contributor)}
                    </div>
                    <div className="text-xs text-gray-500">
                      First contribution: {new Date(contributor.first_contribution).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-gray-500 italic">
                      {contributor.historical_significance}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recognition Levels */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Recognition Levels</CardTitle>
            <CardDescription>
              Understanding the different levels of recognition and their associated benefits
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Crown className="w-5 h-5 text-yellow-500" />
                  <span className="font-bold">Legendary Pioneer</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">First 10 contributors with maximum recognition</p>
                <ul className="text-xs space-y-1">
                  <li>• 5x visibility multiplier</li>
                  <li>• Permanent pioneer badge</li>
                  <li>• Strategic decision access</li>
                </ul>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Trophy className="w-5 h-5 text-purple-500" />
                  <span className="font-bold">Epic Founder</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Early contributors within first month</p>
                <ul className="text-xs space-y-1">
                  <li>• 3x visibility multiplier</li>
                  <li>• Founder recognition badge</li>
                  <li>• Early feature access</li>
                </ul>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Medal className="w-5 h-5 text-blue-500" />
                  <span className="font-bold">Master Contributor</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Multiple badges and high activity</p>
                <ul className="text-xs space-y-1">
                  <li>• 2x visibility multiplier</li>
                  <li>• Community spotlight</li>
                  <li>• Mentorship opportunities</li>
                </ul>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-5 h-5 text-green-500" />
                  <span className="font-bold">Recognized Contributor</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Single badge achievement</p>
                <ul className="text-xs space-y-1">
                  <li>• 1.5x visibility multiplier</li>
                  <li>• Recognition badge</li>
                  <li>• Community features</li>
                </ul>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="w-5 h-5 text-gray-500" />
                  <span className="font-bold">Active Contributor</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Consistent participation (3+ submissions)</p>
                <ul className="text-xs space-y-1">
                  <li>• Activity recognition</li>
                  <li>• Minor visibility boost</li>
                  <li>• Community benefits</li>
                </ul>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-5 h-5 bg-gray-300 rounded-full flex items-center justify-center text-xs">•</span>
                  <span className="font-bold">Valued Contributor</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Basic community participation</p>
                <ul className="text-xs space-y-1">
                  <li>• Basic recognition</li>
                  <li>• Standard community access</li>
                  <li>• Foundation benefits</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">About Recognition System</h3>
          <p className="text-sm text-gray-700">
            The "I Was Here First" recognition system honors early Syntheverse contributors with enhanced visibility,
            priority access, and legacy status. Recognition levels are determined by submission order, badge achievements,
            and ongoing participation per Blueprint §1.4 specifications.
          </p>
        </div>
      </div>
    </div>
  )
}
