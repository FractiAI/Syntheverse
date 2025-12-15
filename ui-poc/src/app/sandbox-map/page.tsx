'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { api, type SandboxMap } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate, truncateHash } from '@/lib/utils'
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'
import dynamic from 'next/dynamic'

// Dynamic import for vis-network to avoid SSR issues
const NetworkComponent = dynamic(() => import('@/components/sandbox-map-network'), {
  ssr: false,
})

const COLORS = {
  gold: '#FCD34D',
  silver: '#94A3B8',
  copper: '#CD7F32',
}

const OVERLAP_COLORS: Record<string, string> = {
  exact_duplicate: '#EF4444',
  high_redundancy: '#F97316',
  moderate_overlap: '#EAB308',
  related: '#84CC16',
  low_overlap: '#94A3B8',
}

const STATUS_COLORS: Record<string, string> = {
  qualified: '#10B981',
  unqualified: '#EF4444',
  evaluating: '#3B82F6',
  submitted: '#F59E0B',
  draft: '#6B7280',
  archived: '#9CA3AF',
}

export default function SandboxMapPage() {
  const router = useRouter()
  const networkInstanceRef = useRef<any>(null)
  
  const [mapData, setMapData] = useState<SandboxMap | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<'all' | 'exact_duplicate' | 'high_redundancy' | 'moderate_overlap' | 'related'>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterMetal, setFilterMetal] = useState<string>('all')
  const [networkData, setNetworkData] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] })

  useEffect(() => {
    loadMapData()
  }, [])

  useEffect(() => {
    if (mapData) {
      const processed = processNetworkData()
      setNetworkData(processed)
    }
  }, [mapData, filterType, filterStatus, filterMetal])

  async function loadMapData() {
    try {
      setLoading(true)
      const data = await api.getSandboxMap()
      setMapData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sandbox map')
    } finally {
      setLoading(false)
    }
  }

  function processNetworkData(): { nodes: any[]; edges: any[] } {
    if (!mapData) return { nodes: [], edges: [] }

    // Filter nodes
    let filteredNodes = [...mapData.nodes]
    if (filterStatus !== 'all') {
      filteredNodes = filteredNodes.filter(n => n.status === filterStatus)
    }
    if (filterMetal !== 'all') {
      filteredNodes = filteredNodes.filter(n => n.metals.includes(filterMetal))
    }

    // Filter edges based on filterType
    let filteredEdges = [...mapData.edges]
    if (filterType !== 'all') {
      filteredEdges = filteredEdges.filter(e => e.overlap_type === filterType)
    }
    
    // Only include edges where both nodes are in filtered nodes
    const nodeHashes = new Set(filteredNodes.map(n => n.submission_hash))
    filteredEdges = filteredEdges.filter(e => 
      nodeHashes.has(e.source_hash) && nodeHashes.has(e.target_hash)
    )

    // Create nodes
    const nodes = filteredNodes.map(node => {
      const primaryMetal = node.metals[0] || 'gold'
      const color = COLORS[primaryMetal as keyof typeof COLORS] || '#888'
      const statusColor = STATUS_COLORS[node.status] || '#6B7280'

      return {
        id: node.submission_hash,
        label: node.title.length > 30 ? node.title.slice(0, 30) + '...' : node.title,
        title: `${node.title}\nStatus: ${node.status}\nMetals: ${node.metals.join(', ')}\nContributor: ${truncateHash(node.contributor, 8)}`,
        color: {
          background: color,
          border: statusColor,
          highlight: {
            background: color,
            border: statusColor,
          },
        },
        borderWidth: 2,
        borderWidthSelected: 4,
        shape: node.metals.length > 1 ? 'diamond' : 'circle',
        size: node.metadata?.pod_score ? Math.max(10, Math.min(30, node.metadata.pod_score / 500)) : 15,
        font: {
          size: 12,
          color: '#1F2937',
        },
        metadata: {
          fullTitle: node.title,
          status: node.status,
          metals: node.metals,
          contributor: node.contributor,
          coherence: node.coherence,
          density: node.density,
          redundancy: node.redundancy,
        },
      }
    })

    // Create edges
    const edges = filteredEdges.map(edge => {
      const edgeColor = OVERLAP_COLORS[edge.overlap_type] || '#94A3B8'
      const width = edge.overlap_type === 'exact_duplicate' ? 4 :
                   edge.overlap_type === 'high_redundancy' ? 3 :
                   edge.overlap_type === 'moderate_overlap' ? 2 : 1

      return {
        from: edge.source_hash,
        to: edge.target_hash,
        color: {
          color: edgeColor,
          highlight: edgeColor,
          opacity: edge.overlap_type === 'related' ? 0.3 : 0.6,
        },
        width,
        title: `${edge.overlap_type.replace('_', ' ')}\nSimilarity: ${(edge.similarity_score * 100).toFixed(1)}%`,
        dashes: edge.overlap_type === 'related',
        metadata: {
          overlapType: edge.overlap_type,
          similarityScore: edge.similarity_score,
        },
      }
    })

    return { nodes, edges }
  }

  function handleZoomIn() {
    // Handled by NetworkComponent
  }

  function handleZoomOut() {
    // Handled by NetworkComponent
  }

  function handleReset() {
    // Handled by NetworkComponent
  }

  function handleNodeClick(nodeId: string) {
    setSelectedNode(nodeId)
  }

  function handleNodeDoubleClick(nodeId: string) {
    router.push(`/submission/${nodeId}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading sandbox map...</div>
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

  if (!mapData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">No map data available</div>
      </div>
    )
  }

  const selectedNodeData = mapData.nodes.find(n => n.submission_hash === selectedNode)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Syntheverse Sandbox Map</h1>
        <p className="text-muted-foreground mt-2">
          Visualize contributions and their relationships to maximize enrichment while minimizing overlap
        </p>
      </div>

      {/* Filters and Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Map Controls</CardTitle>
              <CardDescription>
                {mapData.metadata.total_nodes} nodes, {mapData.metadata.total_edges} edges
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={loadMapData}>
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Overlap Type</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as any)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Types</option>
                <option value="exact_duplicate">Exact Duplicates</option>
                <option value="high_redundancy">High Redundancy</option>
                <option value="moderate_overlap">Moderate Overlap</option>
                <option value="related">Related</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Statuses</option>
                <option value="qualified">Qualified</option>
                <option value="unqualified">Unqualified</option>
                <option value="evaluating">Evaluating</option>
                <option value="submitted">Submitted</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Metal</label>
              <select
                value={filterMetal}
                onChange={(e) => setFilterMetal(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Metals</option>
                <option value="gold">Gold</option>
                <option value="silver">Silver</option>
                <option value="copper">Copper</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="font-medium mb-2">Metals</p>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-[#FCD34D]" />
                  <span>Gold</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-[#94A3B8]" />
                  <span>Silver</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-[#CD7F32]" />
                  <span>Copper</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-gray-400" style={{ transform: 'rotate(45deg)' }} />
                  <span>Multi-metal</span>
                </div>
              </div>
            </div>
            <div>
              <p className="font-medium mb-2">Overlap Types</p>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#EF4444]" />
                  <span>Exact Duplicate</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#F97316]" />
                  <span>High Redundancy</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#EAB308]" />
                  <span>Moderate Overlap</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#84CC16]" style={{ 
                    backgroundImage: 'repeating-linear-gradient(to right, #84CC16 0, #84CC16 4px, transparent 4px, transparent 8px)'
                  }} />
                  <span>Related</span>
                </div>
              </div>
            </div>
            <div>
              <p className="font-medium mb-2">Node Shapes</p>
              <div className="space-y-1 text-xs">
                <div>Circle = Single metal</div>
                <div>Diamond = Multi-metal</div>
                <div>Size = PoC Score</div>
              </div>
            </div>
            <div>
              <p className="font-medium mb-2">Interaction</p>
              <div className="space-y-1 text-xs">
                <div>Click = Select node</div>
                <div>Double-click = View detail</div>
                <div>Drag = Pan</div>
                <div>Scroll = Zoom</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Network Visualization */}
      <Card>
        <CardContent className="p-0">
          <NetworkComponent
            nodes={networkData.nodes}
            edges={networkData.edges}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
          />
        </CardContent>
      </Card>

      {/* Selected Node Info */}
      {selectedNodeData && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Contribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Title</p>
                <p className="mt-1">{selectedNodeData.title}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Status</p>
                <p className="mt-1 capitalize">{selectedNodeData.status}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Metals</p>
                <p className="mt-1">{selectedNodeData.metals.join(', ')}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Contributor</p>
                <p className="mt-1 font-mono text-sm">{truncateHash(selectedNodeData.contributor, 8)}</p>
              </div>
            </div>
            <div className="mt-4">
              <Button onClick={() => router.push(`/submission/${selectedNode}`)}>
                View Full Details
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistics */}
      {mapData.statistics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-6">
              <p className="text-sm font-medium text-muted-foreground">Archive Statistics</p>
              <p className="text-2xl font-bold mt-2">
                {mapData.statistics.archive_stats?.total_contributions || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Total Contributions</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm font-medium text-muted-foreground">Unique Contributors</p>
              <p className="text-2xl font-bold mt-2">
                {mapData.statistics.archive_stats?.unique_contributors || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Active Contributors</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm font-medium text-muted-foreground">Metal Combinations</p>
              <p className="text-2xl font-bold mt-2">
                {Object.keys(mapData.statistics.metal_distribution?.metal_combinations || {}).length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Unique Combinations</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
