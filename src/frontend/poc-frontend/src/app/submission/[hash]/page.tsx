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
    // Navigate to Syntheverse Blockmine registration page with pre-filled data
    const params = new URLSearchParams({
      hash: submissionHash,
      contributor: contributor
    })
    window.open(`http://localhost:5000/register?${params.toString()}`, '_blank')
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
      console.log('Loading data for hash:', hash)
      loadData()

      // Add a timeout to show error if loading takes too long
      const timeout = setTimeout(() => {
        if (!contribution) {
          console.error('Data loading timeout - API call may be failing')
          setError('Failed to load submission data. Check API connectivity.')
          setLoading(false)
        }
      }, 10000) // 10 second timeout

      // Poll for updates if evaluation is in progress
      const pollInterval = setInterval(async () => {
        if (contribution && (contribution.status === 'submitted' || contribution.status === 'evaluating')) {
          try {
            console.log('Polling for updates...')
            const updated = await api.getContribution(hash)
            console.log('Received update:', updated.status)
            setContribution(updated)
            // Stop polling if evaluation is complete
            if (updated.status !== 'submitted' && updated.status !== 'evaluating') {
              clearInterval(pollInterval)
              clearTimeout(timeout)
            }
          } catch (err) {
            console.error('Polling error:', err)
          }
        }
      }, 2000) // Poll every 2 seconds

      return () => {
        clearInterval(pollInterval)
        clearTimeout(timeout)
      }
    }
  }, [hash, contribution?.status])

  async function loadData() {
    try {
      console.log('Starting loadData for hash:', hash)
      setLoading(true)
      setError(null)

      // Try direct fetch first to test connectivity
      console.log('Testing direct API call...')
      const directResponse = await fetch(`http://localhost:5001/api/archive/contributions/${hash}`)
      if (!directResponse.ok) {
        throw new Error(`Direct API call failed: ${directResponse.status} ${directResponse.statusText}`)
      }
      const directData = await directResponse.json()
      console.log('Direct API call successful:', directData)
      console.log('Direct data status:', directData.status)
      console.log('Direct data metadata keys:', Object.keys(directData.metadata || {}))

      // Now try through the API client
      console.log('Trying API client...')
      const contrib = await api.getContribution(hash)
      console.log('API client successful:', contrib)
      console.log('Contribution status:', contrib.status)
      console.log('Contribution metadata keys:', Object.keys(contrib.metadata || {}))
      setContribution(contrib)
      // Evaluation data is stored in contribution metadata
    } catch (err) {
      console.error('loadData error:', err)
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
  // Check if evaluation data actually exists (has scores or grok response)
  const hasEvaluationData = evaluationData &&
    ((evaluationData.coherence !== null && evaluationData.coherence !== undefined) ||
     evaluationData.grok_raw_response ||
     (contribution.status === 'qualified' || contribution.status === 'unqualified'))

  // Debug logging
  console.log('Contribution status:', contribution.status)
  console.log('Has evaluation data:', hasEvaluationData)
  console.log('Metadata keys:', Object.keys(metadata))
  console.log('Has grok_raw_response:', !!evaluationData.grok_raw_response)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Button variant="outline" onClick={() => loadData()}>
            🔄 Refresh Data
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
              AI-powered evaluation using Grok with real-time reasoning
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {hasEvaluationData ? (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Coherence</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.coherence !== undefined ? evaluationData.coherence.toFixed(0) : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Density</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.density !== undefined ? evaluationData.density.toFixed(0) : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Redundancy</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.redundancy !== undefined ? evaluationData.redundancy.toFixed(0) : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000 (lower is better)</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">PoC Score</label>
                    <p className="text-2xl font-bold mt-1">
                      {evaluationData.pod_score !== undefined ? evaluationData.pod_score.toFixed(0) : 'N/A'}
                    </p>
                    <p className="text-xs text-muted-foreground">0-10000</p>
                  </div>
                </div>

                {/* Debug info */}
                <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">
                  <strong>Debug Info:</strong><br/>
                  Status: {contribution.status}<br/>
                  Has evaluationData: {hasEvaluationData ? 'true' : 'false'}<br/>
                  Metadata keys: {Object.keys(metadata).join(', ')}<br/>
                  Coherence: {evaluationData.coherence ?? 'undefined'}<br/>
                  Density: {evaluationData.density ?? 'undefined'}<br/>
                  Redundancy: {evaluationData.redundancy ?? 'undefined'}<br/>
                  PoC Score: {evaluationData.pod_score ?? 'undefined'}
                </div>

                {/* Grok AI Conversation */}
                {evaluationData.grok_raw_response && (
                  <div className="mt-6 pt-4 border-t">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <h4 className="text-sm font-medium">Grok AI Evaluation Conversation</h4>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-950/20 rounded-lg p-4">
                      <pre className="text-xs text-blue-900 dark:text-blue-100 whitespace-pre-wrap font-mono overflow-x-auto max-h-96 overflow-y-auto">
                        {evaluationData.grok_raw_response}
                      </pre>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      This is the raw response from Grok AI showing its evaluation reasoning and thought process.
                    </p>
                  </div>
                )}

                {/* Evaluation Progress */}
                {contribution.status === 'evaluating' && evaluationData.progress && (
                  <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                        {evaluationData.progress}
                      </span>
                    </div>
                  </div>
                )}
              </>
            ) : contribution.status === 'evaluating' ? (
              <div className="text-center py-8">
                <div className="flex items-center justify-center space-x-2 mb-4">
                  <TrendingUp className="h-5 w-5 text-blue-600 animate-pulse" />
                  <span className="text-muted-foreground">Evaluation in progress...</span>
                </div>
                {evaluationData.progress && (
                  <p className="text-sm text-blue-600 dark:text-blue-400">
                    {evaluationData.progress}
                  </p>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Evaluation not yet completed.</p>
                <p className="text-sm mt-1">Submit your contribution to trigger AI evaluation.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Blockchain Information */}
        <Card>
          <CardHeader>
            <CardTitle>Blockchain Information</CardTitle>
            <CardDescription>
              Syntheverse Blockmine - Foundry + Anvil + Hardhat
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Network</label>
                <p className="font-mono text-sm mt-1 flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Anvil Local (Chain ID: 31337)
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">SYNTH Token Contract</label>
                <p className="font-mono text-sm mt-1 break-all">
                  0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">POC Registry Contract</label>
                <p className="font-mono text-sm mt-1 break-all">
                  0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Registration Status</label>
                <p className="mt-1">
                  {contribution.status === 'qualified' ? (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Eligible for Registration
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Evaluation Required
                    </span>
                  )}
                </p>
              </div>
            </div>

            {hasEvaluationData && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium mb-2">Registration Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <label className="text-muted-foreground">Registration Fee</label>
                    <p className="font-medium">
                      {contribution.contributor_stats?.fee_required ? '$50.00 USD' : 'FREE (First 3)'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {contribution.contributor_stats?.free_submissions_remaining || 3} free submissions remaining
                    </p>
                  </div>
                  <div>
                    <label className="text-muted-foreground">Metals to Register</label>
                    <p className="font-medium">{contribution.metals?.join(', ') || 'None'}</p>
                  </div>
                  <div>
                    <label className="text-muted-foreground">Blockchain Tech Stack</label>
                    <p className="font-medium">Foundry + Anvil + Hardhat</p>
                  </div>
                </div>
              </div>
            )}

            <div className="border-t pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium">Grok AI Evaluation</h4>
                  <p className="text-xs text-muted-foreground">
                    Evaluation powered by Grok AI with real-time progress tracking
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-xs text-muted-foreground">AI-Powered</span>
                </div>
              </div>
            </div>
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
                    <h4 className="font-medium">Register on Syntheverse Blockmine</h4>
                    <p className="text-sm text-muted-foreground">
                      Submit to blockchain using Foundry + Anvil + Hardhat
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                        <span>Foundry</span>
                      </div>
                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                        <span>Anvil</span>
                      </div>
                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full"></div>
                        <span>Hardhat</span>
                      </div>
                    </div>
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
      {hasEvaluationData && (
        <Card>
          <CardHeader>
            <CardTitle>Evaluation Details</CardTitle>
            <CardDescription>
              Detailed analysis and justification from Grok AI evaluation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {evaluationData.tier_justification && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Tier Justification</label>
                <p className="mt-1 text-sm bg-green-50 dark:bg-green-950/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                  {evaluationData.tier_justification}
                </p>
              </div>
            )}
            {evaluationData.redundancy_analysis && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Redundancy Analysis</label>
                <p className="mt-1 text-sm bg-blue-50 dark:bg-blue-950/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
                  {evaluationData.redundancy_analysis}
                </p>
              </div>
            )}

            {/* Metal Assignments with Reasoning */}
            {contribution.metals && contribution.metals.length > 0 && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Metal Qualifications</label>
                <div className="mt-2 space-y-2">
                  {contribution.metals.map((metal) => (
                    <div
                      key={metal}
                      className="flex items-center space-x-3 p-3 rounded-lg border"
                      style={{
                        backgroundColor: `${COLORS[metal as keyof typeof COLORS] || '#888'}10`,
                        borderColor: `${COLORS[metal as keyof typeof COLORS] || '#888'}30`,
                      }}
                    >
                      <Award
                        className="h-5 w-5 flex-shrink-0"
                        style={{ color: COLORS[metal as keyof typeof COLORS] }}
                      />
                      <div className="flex-1">
                        <p className="font-medium capitalize text-sm">
                          {metal.charAt(0).toUpperCase() + metal.slice(1)} Metal
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {metal === 'gold' && 'Discovery/Scientific contribution'}
                          {metal === 'silver' && 'Technology contribution'}
                          {metal === 'copper' && 'Alignment contribution'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
