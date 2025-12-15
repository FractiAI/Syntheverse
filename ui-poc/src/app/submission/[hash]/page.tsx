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
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null)
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
      const [contrib, evalResult] = await Promise.all([
        api.getContribution(hash),
        api.evaluateContribution(hash).catch(() => null), // Evaluation may not exist
      ])
      setContribution(contrib)
      setEvaluation(evalResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load submission')
    } finally {
      setLoading(false)
    }
  }

  async function handleEvaluate() {
    if (!hash) return
    try {
      setLoading(true)
      const result = await api.evaluateContribution(hash)
      setEvaluation(result)
      // Reload contribution to get updated status
      const contrib = await api.getContribution(hash)
      setContribution(contrib)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to evaluate')
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
  const evaluationData = evaluation?.evaluation

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
            {contribution.status !== 'evaluating' && contribution.status !== 'qualified' && (
              <CardDescription>
                <Button onClick={handleEvaluate} disabled={loading} className="mt-2">
                  {loading ? 'Evaluating...' : 'Evaluate Contribution'}
                </Button>
              </CardDescription>
            )}
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
                No evaluation available. Click "Evaluate Contribution" to start evaluation.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Allocations */}
      {evaluation?.allocations && evaluation.allocations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Token Allocations</CardTitle>
            <CardDescription>Multi-metal allocation breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {evaluation.allocations.map((allocation, idx) => (
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
              ))}
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
            <pre className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-lg max-h-96 overflow-y-auto">
              {contribution.text_content?.slice(0, 5000) || 'No content available'}
              {contribution.text_content && contribution.text_content.length > 5000 && '...'}
            </pre>
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
