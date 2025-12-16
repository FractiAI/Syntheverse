// API client for PoC backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

export interface Contribution {
  submission_hash: string
  title: string
  contributor: string
  content_hash: string
  text_content: string
  status: string
  category?: string
  metals: string[]
  metadata: {
    coherence?: number
    density?: number
    redundancy?: number
    pod_score?: number
    [key: string]: any
  }
  created_at: string
  updated_at: string
}

export interface EvaluationResult {
  success: boolean
  submission_hash: string
  evaluation?: {
    coherence: number
    density: number
    redundancy: number
    metals: string[]
    pod_score: number
    tier_justification?: string
    redundancy_analysis?: string
    status: string
  }
  status: string
  qualified: boolean
  allocations?: Array<{
    metal: string
    epoch: string
    tier: string
    allocation: {
      reward: number
      tier_multiplier: number
      epoch_balance_before: number
      epoch_balance_after: number
    }
  }>
  redundancy_report?: any
  error?: string
}

export interface ArchiveStatistics {
  total_contributions: number
  status_counts: Record<string, number>
  metal_counts: Record<string, number>
  unique_contributors: number
  unique_content_hashes: number
  last_updated: string
}

export interface SandboxMap {
  nodes: Array<{
    submission_hash: string
    title: string
    contributor: string
    status: string
    metals: string[]
    coherence?: number
    density?: number
    redundancy?: number
    created_at?: string
  }>
  edges: Array<{
    source_hash: string
    target_hash: string
    similarity_score: number
    overlap_type: string
  }>
  metadata: {
    total_nodes: number
    total_edges: number
    generated_at: string
  }
  statistics?: any
}

export interface EpochInfo {
  current_epoch: string
  epochs: Record<string, {
    balance: number
    threshold: number
    distribution_amount: number
    distribution_percent: number
    available_tiers: string[]
  }>
}

export interface TokenomicsStatistics {
  total_supply: number
  total_distributed: number
  total_remaining: number
  epoch_balances: Record<string, number>
  current_epoch: string
  founder_halving_count: number
  total_coherence_density: number
  total_holders: number
  total_allocations: number
}

class PoCApi {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  private async fetch(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return response.json()
  }

  // Archive operations
  async getArchiveStatistics(): Promise<ArchiveStatistics> {
    return this.fetch('/api/archive/statistics')
  }

  async getContributions(params?: {
    status?: string
    contributor?: string
    metal?: string
  }): Promise<Contribution[]> {
    const query = new URLSearchParams(params as any).toString()
    return this.fetch(`/api/archive/contributions?${query}`)
  }

  async getContribution(submissionHash: string): Promise<Contribution> {
    return this.fetch(`/api/archive/contributions/${submissionHash}`)
  }

  // Submission operations
  async submitContribution(data: {
    submission_hash: string
    title: string
    contributor: string
    text_content?: string
    pdf_path?: string
    category?: string
    file?: File
  }): Promise<{ success: boolean; submission_hash: string }> {
    if (data.file) {
      // Use FormData for file uploads
      const formData = new FormData()
      formData.append('submission_hash', data.submission_hash)
      formData.append('title', data.title)
      formData.append('contributor', data.contributor)
      formData.append('category', data.category || 'scientific')
      if (data.text_content) {
        formData.append('text_content', data.text_content)
      }
      formData.append('file', data.file)

      const response = await fetch(`${this.baseUrl}/api/submit`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      return response.json()
    } else {
      // Use JSON for text-only submissions
      return this.fetch('/api/submit', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    }
  }

  async evaluateContribution(submissionHash: string): Promise<EvaluationResult> {
    return this.fetch(`/api/evaluate/${submissionHash}`, {
      method: 'POST',
    })
  }

  // Sandbox Map
  async getSandboxMap(): Promise<SandboxMap> {
    return this.fetch('/api/sandbox-map')
  }

  // Tokenomics
  async getEpochInfo(): Promise<EpochInfo> {
    return this.fetch('/api/tokenomics/epoch-info')
  }

  async getTokenomicsStatistics(): Promise<TokenomicsStatistics> {
    return this.fetch('/api/tokenomics/statistics')
  }
}

export const api = new PoCApi()
