'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, FileText, Loader2 } from 'lucide-react'

export default function SubmissionPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [grokResponse, setGrokResponse] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    title: '',
    contributor: '',
    category: 'scientific',
    textContent: '',
    file: null as File | null,
  })

  const hasFile = formData.file !== null
  const hasTextContent = formData.textContent.trim().length > 0

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setLoading(true)

    try {
      // Validate that we have either a file or text content
      if (!formData.file && !formData.textContent.trim()) {
        throw new Error('Please provide either a PDF file or text content')
      }

      // Generate submission hash
      const submissionHash = crypto.randomUUID().replace(/-/g, '')

      // Prepare submission data
      const submissionData: any = {
        submission_hash: submissionHash,
        title: formData.title,
        contributor: formData.contributor,
        category: formData.category,
      }

      // Include file if available
      if (formData.file) {
        submissionData.file = formData.file

        // Include additional text if provided
        if (formData.textContent.trim()) {
          submissionData.text_content = formData.textContent.trim()
        }
      } else {
        // No file, use text content
        submissionData.text_content = formData.textContent.trim()
      }

      // Submit contribution
      const result = await api.submitContribution(submissionData)

      setSuccess(`Contribution submitted! Waiting for evaluation... Hash: ${result.submission_hash.slice(0, 16)}...`)
      setLoading(false)
      setEvaluating(true)

      // Wait for evaluation to complete
      const maxWaitTime = 60000 // 60 seconds max wait
      const pollInterval = 2000 // Poll every 2 seconds
      const startTime = Date.now()

      const waitForEvaluation = async () => {
        try {
          const contribution = await api.getContribution(result.submission_hash)

          // Update progress display with actual evaluation status from metadata
          if (contribution.metadata?.progress) {
            setSuccess(`${success.split(' - ')[0]} - ${contribution.metadata.progress}`)
          }

          // If we have the raw Grok response, show it
          if (contribution.metadata?.grok_raw_response) {
            setGrokResponse(contribution.metadata.grok_raw_response)
          }

          // Check if evaluation is complete
          if (contribution.status !== 'submitted' && contribution.status !== 'evaluating') {
            // Evaluation complete, redirect to results
            router.push(`/submission/${result.submission_hash}`)
            return
          }

          // Continue waiting if not timed out (increased to 6 minutes to match API timeout + buffer)
          if (Date.now() - startTime < 360000) {
            setTimeout(waitForEvaluation, pollInterval)
          } else {
            // Timeout reached, show error but don't redirect
            setEvaluating(false)
            setError('Evaluation is taking longer than expected. Please check back later or contact support.')
          }
        } catch (err) {
          // On error, redirect anyway
          router.push(`/submission/${result.submission_hash}`)
        }
      }

      // Start waiting for evaluation
      setTimeout(waitForEvaluation, pollInterval)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit contribution')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Submit Contribution</h1>
        <p className="text-muted-foreground mt-2">
          Submit a new Proof of Contribution for evaluation
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Submit Contribution</CardTitle>
          <CardDescription>
            Upload a PDF file containing your contribution. Text will be automatically extracted and evaluated. Archive-first: All submissions are stored regardless of evaluation status.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium mb-2">
                Title *
              </label>
              <input
                id="title"
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border rounded-md"
                placeholder="Enter contribution title"
              />
            </div>

            <div>
              <label htmlFor="contributor" className="block text-sm font-medium mb-2">
                Contributor ID *
              </label>
              <input
                id="contributor"
                type="text"
                required
                value={formData.contributor}
                onChange={(e) => setFormData({ ...formData, contributor: e.target.value })}
                className="w-full px-4 py-2 border rounded-md font-mono"
                placeholder="contributor-001"
              />
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-medium mb-2">
                Category *
              </label>
              <select
                id="category"
                required
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border rounded-md"
              >
                <option value="scientific">Scientific (Gold)</option>
                <option value="tech">Technology (Silver)</option>
                <option value="alignment">Alignment (Copper)</option>
              </select>
              <p className="text-xs text-muted-foreground mt-1">
                Note: A contribution can contain multiple metals after evaluation
              </p>
            </div>

            <div>
              <label htmlFor="file" className="block text-sm font-medium mb-2">
                PDF File *
              </label>
              <div className="flex items-center space-x-4">
                <label
                  htmlFor="file"
                  className={`flex items-center space-x-2 px-4 py-2 border rounded-md cursor-pointer hover:bg-accent ${
                    hasFile ? 'bg-green-50 border-green-300' : ''
                  }`}
                >
                  <Upload className="h-4 w-4" />
                  <span>{hasFile ? 'PDF Selected' : 'Choose PDF'}</span>
                </label>
                <input
                  id="file"
                  type="file"
                  accept=".pdf"
                  required={!hasTextContent}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      file: e.target.files?.[0] || null,
                    })
                  }
                  className="hidden"
                />
                {formData.file && (
                  <span className="text-sm text-green-700 flex items-center space-x-2 font-medium">
                    <FileText className="h-4 w-4" />
                    <span>{formData.file.name}</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Upload a PDF file. Text will be automatically extracted from the PDF. Ensure your PDF contains selectable text.
              </p>
            </div>

            <div>
              <label htmlFor="textContent" className="block text-sm font-medium mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                id="textContent"
                value={formData.textContent}
                onChange={(e) => setFormData({ ...formData, textContent: e.target.value })}
                rows={6}
                className="w-full px-4 py-2 border rounded-md font-mono text-sm"
                placeholder="Optional: Add any additional notes, comments, or text that should supplement the PDF content..."
              />
              <p className="text-xs text-muted-foreground mt-1">
                {hasFile
                  ? `${formData.textContent.length} characters (supplements PDF)`
                  : `${formData.textContent.length} characters`}
              </p>
              {!hasFile && !hasTextContent && (
                <p className="text-xs text-red-600 mt-1">
                  Either a PDF file or text content is required
                </p>
              )}
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-800">
                {error}
              </div>
            )}

            {success && (
              <div className={`p-4 border rounded-md ${
                evaluating
                  ? 'bg-blue-50 border-blue-200 text-blue-800'
                  : 'bg-green-50 border-green-200 text-green-800'
              }`}>
                <div className="flex items-center space-x-2">
                  {evaluating && <Loader2 className="h-4 w-4 animate-spin" />}
                  <span>{success}</span>
                </div>
                {evaluating && (
                  <div className="text-sm mt-2 space-y-1">
                    <p className="opacity-75">
                      🤖 AI evaluation in progress with Grok. Please wait...
                    </p>
                    <div className="bg-blue-100 p-2 rounded text-xs font-mono">
                      Status: Communicating with Grok AI for detailed evaluation...
                    </div>
                    <div className="bg-green-50 p-2 rounded text-xs space-y-1">
                      <p className="font-medium">📋 Evaluation Progress:</p>
                      <div className="space-y-0.5 text-xs">
                        <p>• 🤖 Preparing evaluation data for Grok AI...</p>
                        <p>• 🔍 Analyzing archive for redundancy detection...</p>
                        <p>• 🔬 Grok is analyzing coherence, density, and redundancy...</p>
                        <p>• 📊 Extracting coherence, density, and redundancy scores...</p>
                        <p>• ⚖️ Determining contribution qualification and metal assignment...</p>
                        <p>• 💰 Calculating SYNTH token rewards based on evaluation scores...</p>
                      </div>
                    </div>

                    {grokResponse && (
                      <div className="bg-purple-50 p-3 rounded text-xs space-y-2 border border-purple-200">
                        <p className="font-medium text-purple-800">🤖 Grok AI Evaluation Response:</p>
                        <div className="bg-white p-2 rounded text-xs font-mono max-h-40 overflow-y-auto border">
                          <pre className="whitespace-pre-wrap text-gray-800">{grokResponse}</pre>
                        </div>
                        <p className="text-purple-600 italic">Processing scores from Grok's evaluation...</p>
                      </div>
                    )}
                    <p className="text-xs opacity-60">
                      This may take up to 5 minutes for complex content. The page will automatically redirect when evaluation is complete.
                    </p>
                  </div>
                )}
              </div>
            )}

            <Button type="submit" disabled={loading || evaluating || (!hasFile && !hasTextContent)} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing PDF...
                </>
              ) : evaluating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Evaluating with AI...
                </>
              ) : (
                'Submit PDF Contribution'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
