'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { api, type Contribution, type EvaluationResult } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate, truncateHash, formatNumber } from '@/lib/utils'
import { ArrowLeft, FileText, Award, TrendingUp, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

const COLORS = {
  gold: '#FCD34D',
  silver: '#94A3B8',
  copper: '#CD7F32',
}

function MetalBadge({ metals }: { metals: string[] }) {
  return (
    <div className="flex gap-2">
      {metals.map((metal) => (
        <span
          key={metal}
          className="px-3 py-1 rounded-md text-sm font-medium"
          style={{
            backgroundColor: `${COLORS[metal as keyof typeof COLORS] || '#888'}20`,
            color: COLORS[metal as keyof typeof COLORS] || '#888',
            border: `1px solid ${COLORS[metal as keyof typeof COLORS] || '#888'}`,
          }}
        >
          {metal.charAt(0).toUpperCase() + metal.slice(1)}
        </span>
      ))}
    </div>
  )
}

function cleanTextFormatting(text: string): string {
  if (!text) return text

  // Handle PDF text where each word is on a separate line
  // Join words that were separated by newlines (but keep paragraph breaks)
  text = text.replace(/([a-zA-Z0-9,.;:!?'"])\n([a-zA-Z0-9])/g, '$1 $2')

  // Clean up remaining formatting
  text = text.replace(/ +/g, ' ')  // Multiple spaces to single
  text = text.replace(/\n\s*\n\s*\n+/g, '\n\n')  // Multiple newlines to double
  text = text.replace(/^\s+/gm, '')  // Remove line-start spaces
  text = text.replace(/\s+$/gm, '')  // Remove line-end spaces

  return text.trim()
}

async function handleRegisterPoC(submissionHash: string, contributor: string) {
  try {
    // Navigate to Synthechain registration page with pre-filled data
    const params = new URLSearchParams({
      hash: submissionHash,
      contributor: contributor
    })
    window.open(`http://localhost:5001/register?${params.toString()}`, '_blank')
  } catch (err) {
    console.error('Failed to open registration page:', err)
    alert('Failed to open registration page. Please try again.')
  }
}

function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { color: string; icon: React.ReactNode }> = {
    qualified: {
      color: 'bg-green-100 text-green-800 border-green-300',
      icon: <CheckCircle className="h-4 w-4" />,
    },
    unqualified: {
      color: 'bg-red-100 text-red-800 border-red-300',
      icon: <XCircle className="h-4 w-4" />,
    },
    evaluating: {
      color: 'bg-blue-100 text-blue-800 border-blue-300',
      icon: <TrendingUp className="h-4 w-4" />,
    },
    submitted: {
      color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      icon: <AlertCircle className="h-4 w-4" />,
    },
    draft: {
      color: 'bg-gray-100 text-gray-800 border-gray-300',
      icon: <FileText className="h-4 w-4" />,
    },
  }

  const config = statusConfig[status.toLowerCase()] || statusConfig.draft

  return (
    <span className={`px-3 py-1 rounded-md text-sm font-medium border flex items-center gap-2 ${config.color}`}>
      {config.icon}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function SubmissionDetailPage() {
  const params = useParams()
  const router = useRouter()
  const hash = params.hash as string

  const [contribution, setContribution] = useState<Contribution | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (hash) {
      loadData()
    }
  }, [hash])

  async function loadData() {
    try {
      setLoading(true)
      const contrib = await api.getContribution(hash)
      setContribution(contrib)
      // Evaluation data is stored in contribution metadata
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load submission')
    } finally {
      setLoading(false)
    }
  }


  if (loading && !contribution) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading submission...</div>
      </div>
    )
  }

  if (error && !contribution) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-destructive">Error: {error}</div>
      </div>
    )
  }

  if (!contribution) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Contribution not found</div>
      </div>
    )
  }

  const metadata = contribution.metadata || {}
  // Evaluation data is stored directly in metadata
  const evaluationData = metadata

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{contribution.title}</h1>
            <p className="text-muted-foreground mt-1">
              Submission Hash: <span className="font-mono text-sm">{truncateHash(hash, 12)}</span>
            </p>
          </div>
        </div>
        <StatusBadge status={contribution.status} />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Contributor</label>
              <p className="font-mono text-sm mt-1">{truncateHash(contribution.contributor, 12)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Content Hash</label>
              <p className="font-mono text-sm mt-1">{truncateHash(contribution.content_hash, 12)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Category</label>
              <p className="mt-1 capitalize">{contribution.category || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Metals</label>
              <div className="mt-2">
                <MetalBadge metals={contribution.metals} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Created</label>
              <p className="mt-1">{formatDate(contribution.created_at)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Updated</label>
              <p className="mt-1">{formatDate(contribution.updated_at)}</p>
            </div>
          </CardContent>
        </Card>

        {/* Evaluation Scores */}
        <Card>
          <CardHeader>
            <CardTitle>Evaluation Metrics</CardTitle>
            <CardDescription>
              Evaluation occurs automatically upon submission
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {evaluationData ? (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Coherence</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.coherence?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Density</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.density?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Redundancy</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.redundancy?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000 (lower is better)</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">PoC Score</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.pod_score?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                Evaluation in progress or not yet completed.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Allocations */}
      {contribution.status === 'qualified' && (
        <Card>
          <CardHeader>
            <CardTitle>Token Allocations</CardTitle>
            <CardDescription>
              {metadata.allocations && metadata.allocations.length > 0
                ? `Total: ${formatNumber(metadata.allocations.reduce((sum, alloc) => sum + alloc.allocation.reward, 0) / 1e12)}T across ${metadata.allocations.length} metal${metadata.allocations.length > 1 ? 's' : ''}`
                : `Tokens allocated for ${contribution.metals.length} qualified metal${contribution.metals.length > 1 ? 's' : ''}`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {metadata.allocations && metadata.allocations.length > 0 ? (
                metadata.allocations.map((allocation, idx) => (
                <div
                  key={idx}
                  className="border rounded-lg p-4"
                  style={{
                    borderColor: `${COLORS[allocation.metal as keyof typeof COLORS] || '#888'}40`,
                    backgroundColor: `${COLORS[allocation.metal as keyof typeof COLORS] || '#888'}10`,
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Award
                        className="h-5 w-5"
                        style={{ color: COLORS[allocation.metal as keyof typeof COLORS] }}
                      />
                      <div>
                        <p className="font-semibold capitalize">{allocation.metal}</p>
                        <p className="text-sm text-muted-foreground">
                          {allocation.tier} • {allocation.epoch}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">
                        {formatNumber(allocation.allocation.reward / 1e12)}T
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {allocation.allocation.tier_multiplier}x multiplier
                      </p>
                    </div>
                  </div>
                </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>Tokens have been allocated for this qualified contribution.</p>
                  <p className="text-sm mt-2">Detailed breakdown available for future submissions.</p>
                </div>
              )}

              {/* Register PoC Button */}
              <div className="mt-6 pt-4 border-t">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Register on Synthechain</h4>
                    <p className="text-sm text-muted-foreground">
                      Generate a certificate to permanently register this PoC on the blockchain
                    </p>
                  </div>
                  <Button
                    onClick={() => handleRegisterPoC(contribution.submission_hash, contribution.contributor)}
                    className="flex items-center space-x-2"
                  >
                    <Award className="h-4 w-4" />
                    <span>Register PoC</span>
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Content Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Content Preview</CardTitle>
          <CardDescription>First 5000 characters of contribution content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            <div className="font-mono text-sm bg-muted p-4 rounded-lg max-h-96 overflow-y-auto whitespace-pre-line">
              {contribution.text_content ? cleanTextFormatting(contribution.text_content).slice(0, 5000) : 'No content available'}
              {contribution.text_content && cleanTextFormatting(contribution.text_content).length > 5000 && '...'}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Evaluation Details */}
      {evaluationData && (
        <Card>
          <CardHeader>
            <CardTitle>Evaluation Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {evaluationData.tier_justification && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Tier Justification</label>
                <p className="mt-1 text-sm">{evaluationData.tier_justification}</p>
              </div>
            )}
            {evaluationData.redundancy_analysis && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Redundancy Analysis</label>
                <p className="mt-1 text-sm">{evaluationData.redundancy_analysis}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
