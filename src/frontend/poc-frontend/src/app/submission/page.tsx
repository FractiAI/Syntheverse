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

      setSuccess(`Contribution submitted! Hash: ${result.submission_hash.slice(0, 16)}...`)

      // Redirect to submission detail after a short delay
      setTimeout(() => {
        router.push(`/submission/${result.submission_hash}`)
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit contribution')
    } finally {
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
              <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-800">
                {success}
              </div>
            )}

            <Button type="submit" disabled={loading || (!hasFile && !hasTextContent)} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing PDF...
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
