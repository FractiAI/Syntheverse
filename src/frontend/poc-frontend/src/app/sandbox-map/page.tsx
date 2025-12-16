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

// Syntheverse Dimensions - Multi-layered knowledge structure
const SYNTHVERSE_DIMENSIONS = {
  // Fundamental Consciousness & Cognition
  awareness: { name: 'Awareness', color: '#8B5CF6', description: 'Consciousness and awareness systems' },
  cognition: { name: 'Cognition', color: '#06B6D4', description: 'Cognitive processes and intelligence' },

  // Biological & Chemical Foundations
  biology: { name: 'Biology', color: '#10B981', description: 'Biological systems and life processes' },
  chemistry: { name: 'Chemistry', color: '#F59E0B', description: 'Chemical interactions and reactions' },

  // Molecular & Atomic Scales
  molecules: { name: 'Molecules', color: '#EF4444', description: 'Molecular structures and interactions' },
  elements: { name: 'Elements', color: '#EC4899', description: 'Chemical elements and properties' },

  // Quantum & Physical Foundations
  quantum_elements: { name: 'Quantum Elements', color: '#7C3AED', description: 'Quantum-level elemental behavior' },
  quantum_physics: { name: 'Quantum Physics', color: '#3B82F6', description: 'Quantum mechanical principles' },
  physics: { name: 'Physics', color: '#1E40AF', description: 'Classical physics and mechanics' },

  // Knowledge & Application Layers
  research: { name: 'Research', color: '#059669', description: 'Scientific research and discovery' },
  engineering: { name: 'Engineering', color: '#DC2626', description: 'Technical design and implementation' },
  practice: { name: 'Practice', color: '#D97706', description: 'Applied practice and methodology' },

  // Societal & Economic Layers
  enterprise: { name: 'Enterprise', color: '#7C2D12', description: 'Business and organizational systems' },
  financier: { name: 'Financier', color: '#92400E', description: 'Financial and economic aspects' },
  contributor: { name: 'Contributor', color: '#365314', description: 'Knowledge contributors and creators' },
  user: { name: 'User', color: '#1E3A8A', description: 'End users and beneficiaries' }
}

// Dimension mapping for papers
const PAPER_DIMENSIONS = {
  // Core Syntheverse paper
  'Syntheverse__A_Peer-to-Peer_Holographic_Coherence_System_The_Fundamental_Evolution_from_Proof-of-Work_to_Proof-of-Discovery_': [
    'awareness', 'cognition', 'research', 'enterprise', 'contributor'
  ],

  // HHF-AI paper
  'Syntheverse_HHF-AI__Hydrogen-Holographic_Fractal_Awareness_System': [
    'awareness', 'cognition', 'quantum_physics', 'engineering', 'practice'
  ],

  // Fractal Chemistry paper
  'Introducing_Fractal_Cognitive_Chemistry__From_Fractal_Awareness_to_Generative_and_AI_Awareness_through_the_Leo_Holographic_Symbolic_Framework_': [
    'chemistry', 'cognition', 'biology', 'quantum_physics', 'research'
  ],

  // RSI paper
  'Recursive_Sourced_Interference_RSI_in_the_HydrogenHolographic_Fractal_Sandbox_HHFS': [
    'quantum_elements', 'physics', 'molecules', 'engineering', 'practice'
  ],

  // Octave Harmonics paper
  'Octave_Harmonics_as_Empirical_Evidence_of_the_Hydrogen_Holographic_Fractal_Environment': [
    'quantum_physics', 'physics', 'elements', 'research', 'practice'
  ],

  // PoD paper
  'Syntheverse_PoD__Hydrogen-Holographic_Fractal_Consensus_for_Structural_Knowledge_Mining': [
    'cognition', 'engineering', 'practice', 'enterprise', 'contributor'
  ],

  // 10-1 Framework
  'The_10-1_Framework_Re-F': [
    'cognition', 'research', 'engineering', 'practice', 'enterprise'
  ],

  // Theory of Enough
  'Theory_of_Enough_Re-F': [
    'cognition', 'physics', 'research', 'financier', 'user'
  ]
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
  const [activeDimensions, setActiveDimensions] = useState<Set<string>>(new Set(['all']))

  useEffect(() => {
    loadMapData()
  }, [])

  useEffect(() => {
    if (mapData) {
      const processed = processNetworkData()
      console.log('Processed network data:', { nodes: processed.nodes.length, edges: processed.edges.length })
      setNetworkData(processed)
    }
  }, [mapData, filterType, filterStatus, filterMetal, activeDimensions])

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

    // Filter nodes - only show qualified submissions by default
    let filteredNodes = mapData.nodes.filter(n => n.status === 'qualified')
    if (filterStatus !== 'all') {
      filteredNodes = filteredNodes.filter(n => n.status === filterStatus)
    }
    if (filterMetal !== 'all') {
      filteredNodes = filteredNodes.filter(n => n.metals.includes(filterMetal))
    }

    // Outcast Hero's Arc - Narrative Knowledge Journey
    const heroesArc = {
      // Phase 1: The Outcast (Rejected/Controversial Ideas)
      outcast: [] as any[],

      // Phase 2: Call to Adventure (First Challenges/Explorations)
      call_to_adventure: [] as any[],

      // Phase 3: Trials & Tribulations (Building Evidence/Refinement)
      trials: [] as any[],

      // Phase 4: Transformation (Gaining Acceptance/Evolution)
      transformation: [] as any[],

      // Phase 5: Hero's Return (Fully Realized Concepts)
      heroes_return: [] as any[],
    }

    // Hero's Journey Structure - Narrative progression of ideas
    const narrativeArc = {
      // Phase 1: The Outcast - Radical, misunderstood, paradigm-shifting ideas
      outcast: [
        'Syntheverse__A_Peer-to-Peer_Holographic_Coherence_System_The_Fundamental_Evolution_from_Proof-of-Work_to_Proof-of-Discovery_'
      ],

      // Phase 2: Call to Adventure - First explorations of the radical concepts
      call_to_adventure: [
        'Introducing_Fractal_Cognitive_Chemistry__From_Fractal_Awareness_to_Generative_and_AI_Awareness_through_the_Leo_Holographic_Symbolic_Framework_',
        'Syntheverse_HHF-AI__Hydrogen-Holographic_Fractal_Awareness_System'
      ],

      // Phase 3: Trials & Tribulations - Building empirical evidence and facing challenges
      trials: [
        'Octave_Harmonics_as_Empirical_Evidence_of_the_Hydrogen_Holographic_Fractal_Environment',
        'Recursive_Sourced_Interference_RSI_in_the_HydrogenHolographic_Fractal_Sandbox_HHFS'
      ],

      // Phase 4: Transformation - Concepts evolve, gain traction, adapt to criticism
      transformation: [
        'Syntheverse_PoD__Hydrogen-Holographic_Fractal_Consensus_for_Structural_Knowledge_Mining'
      ],

      // Phase 5: Hero's Return - Fully matured concepts that transform the field
      heroes_return: [
        'The_10-1_Framework_Re-F',
        'Theory_of_Enough_Re-F'
      ]
    }

    // Categorize papers into hero's arc phases and assign dimensions
    filteredNodes.forEach(node => {
      const title = node.title
      let phase = 'heroes_return' // Default phase

      if (narrativeArc.outcast.some(idea => title.includes(idea.split('_')[0]))) {
        phase = 'outcast'
      } else if (narrativeArc.call_to_adventure.some(idea => title.includes(idea.split('_')[0]))) {
        phase = 'call_to_adventure'
      } else if (narrativeArc.trials.some(idea => title.includes(idea.split('_')[0]))) {
        phase = 'trials'
      } else if (narrativeArc.transformation.some(idea => title.includes(idea.split('_')[0]))) {
        phase = 'transformation'
      }

      // Assign dimensions to the node
      const nodeKey = Object.keys(PAPER_DIMENSIONS).find(key => title.includes(key.split('_')[0]))
      const dimensions = nodeKey ? PAPER_DIMENSIONS[nodeKey as keyof typeof PAPER_DIMENSIONS] : ['research']

      // Filter by active dimensions
      const showNode = activeDimensions.has('all') || dimensions.some(dim => activeDimensions.has(dim))

      if (showNode) {
        const nodeWithDimensions = { ...node, dimensions }
        heroesArc[phase as keyof typeof heroesArc].push(nodeWithDimensions)
      }
    })

    // Hero's Journey Layout - Narrative Progression
    const journeyLayout = {
      // Phase 1: Outcast (Leftmost, isolated)
      outcast: { x: -400, y: 50, spread: 100 },

      // Phase 2: Call to Adventure (Left-center, emerging)
      call_to_adventure: [
        { x: -200, y: -50 },
        { x: -200, y: 150 }
      ],

      // Phase 3: Trials (Center-left, challenging)
      trials: [
        { x: 0, y: -100 },
        { x: 0, y: 200 }
      ],

      // Phase 4: Transformation (Center-right, evolving)
      transformation: { x: 200, y: 50, spread: 120 },

      // Phase 5: Hero's Return (Rightmost, triumphant)
      heroes_return: [
        { x: 400, y: -50 },
        { x: 400, y: 150 }
      ]
    }

    // Hero's Arc Colors (Journey Theme)
    const journeyColors = {
      outcast: '#DC2626',       // Red (danger, rejection)
      call_to_adventure: '#EA580C', // Orange (adventure, excitement)
      trials: '#CA8A04',       // Yellow (challenge, growth)
      transformation: '#16A34A', // Green (change, acceptance)
      heroes_return: '#2563EB'  // Blue (victory, wisdom)
    }

    // Create hero's journey nodes
    const nodes: any[] = []

    // Add outcast nodes (Phase 1)
    heroesArc.outcast.forEach((node, index) => {
      const pos = journeyLayout.outcast
      const x = pos.x + (index - (heroesArc.outcast.length - 1) / 2) * (pos.spread / Math.max(1, heroesArc.outcast.length))
      const y = pos.y + (Math.random() - 0.5) * 30

      nodes.push(createJourneyNode(node, x, y, 'outcast', journeyColors.outcast))
    })

    // Add call to adventure nodes (Phase 2)
    heroesArc.call_to_adventure.forEach((node, index) => {
      const pos = journeyLayout.call_to_adventure[index] || journeyLayout.call_to_adventure[0]
      const x = pos.x + (Math.random() - 0.5) * 40
      const y = pos.y + (Math.random() - 0.5) * 40

      nodes.push(createJourneyNode(node, x, y, 'call_to_adventure', journeyColors.call_to_adventure))
    })

    // Add trials nodes (Phase 3)
    heroesArc.trials.forEach((node, index) => {
      const pos = journeyLayout.trials[index] || journeyLayout.trials[0]
      const x = pos.x + (Math.random() - 0.5) * 40
      const y = pos.y + (Math.random() - 0.5) * 40

      nodes.push(createJourneyNode(node, x, y, 'trials', journeyColors.trials))
    })

    // Add transformation nodes (Phase 4)
    heroesArc.transformation.forEach((node, index) => {
      const pos = journeyLayout.transformation
      const x = pos.x + (index - (heroesArc.transformation.length - 1) / 2) * (pos.spread / Math.max(1, heroesArc.transformation.length))
      const y = pos.y + (Math.random() - 0.5) * 30

      nodes.push(createJourneyNode(node, x, y, 'transformation', journeyColors.transformation))
    })

    // Add hero's return nodes (Phase 5)
    heroesArc.heroes_return.forEach((node, index) => {
      const pos = journeyLayout.heroes_return[index] || journeyLayout.heroes_return[0]
      const x = pos.x + (Math.random() - 0.5) * 40
      const y = pos.y + (Math.random() - 0.5) * 40

      nodes.push(createJourneyNode(node, x, y, 'heroes_return', journeyColors.heroes_return))
    })

    // Helper function to create journey nodes with dimensional awareness
    function createJourneyNode(node: any, x: number, y: number, phase: string, borderColor: string) {
      const primaryMetal = node.metals[0] || 'gold'
      const color = COLORS[primaryMetal as keyof typeof COLORS] || '#888'
      const statusColor = STATUS_COLORS[node.status] || '#6B7280'

      // Phase display names
      const phaseNames = {
        outcast: 'OUTCAST',
        call_to_adventure: 'CALL TO ADVENTURE',
        trials: 'TRIALS & TRIBULATIONS',
        transformation: 'TRANSFORMATION',
        heroes_return: 'HERO\'S RETURN'
      }

      // Dimension display names
      const dimensionNames = node.dimensions?.map((dim: string) =>
        SYNTHVERSE_DIMENSIONS[dim as keyof typeof SYNTHVERSE_DIMENSIONS]?.name || dim
      ).join(', ') || 'Research'

      return {
        id: node.submission_hash,
        label: node.title.length > 20 ? node.title.slice(0, 20) + '...' : node.title,
        title: `${node.title}\nPhase: ${phaseNames[phase as keyof typeof phaseNames]}\nDimensions: ${dimensionNames}\nStatus: ${node.status}\nMetals: ${node.metals.join(', ')}\nContributor: ${truncateHash(node.contributor, 8)}`,
        x: x,
        y: y,
        color: {
          background: color,
          border: borderColor,
          highlight: {
            background: color,
            border: borderColor,
          },
        },
        borderWidth: 4,
        borderWidthSelected: 6,
        shape: node.metals.length > 1 ? 'diamond' : 'circle',
        size: phase === 'outcast' ? 35 : phase === 'call_to_adventure' ? 30 : phase === 'trials' ? 28 : phase === 'transformation' ? 32 : 25,
        font: {
          size: phase === 'outcast' ? 13 : 11,
          color: '#1F2937',
          bold: phase === 'outcast' || phase === 'heroes_return',
        },
        metadata: {
          fullTitle: node.title,
          phase: phase,
          dimensions: node.dimensions || [],
          status: node.status,
          metals: node.metals,
          contributor: node.contributor,
          coherence: node.coherence,
          density: node.density,
          redundancy: node.redundancy,
        },
      }
    }

    // Create narrative progression edges (hero's journey)
    const edges: any[] = []

    // Define hero's journey connections (narrative progression)
    const journeyConnections = [
      // Outcast → Call to Adventure
      { from: heroesArc.outcast.map(n => n.submission_hash), to: heroesArc.call_to_adventure.map(n => n.submission_hash), type: 'emergence', color: '#EA580C' },

      // Call to Adventure → Trials
      { from: heroesArc.call_to_adventure.map(n => n.submission_hash), to: heroesArc.trials.map(n => n.submission_hash), type: 'challenge', color: '#CA8A04' },

      // Trials → Transformation
      { from: heroesArc.trials.map(n => n.submission_hash), to: heroesArc.transformation.map(n => n.submission_hash), type: 'evolution', color: '#16A34A' },

      // Transformation → Hero's Return
      { from: heroesArc.transformation.map(n => n.submission_hash), to: heroesArc.heroes_return.map(n => n.submission_hash), type: 'triumph', color: '#2563EB' },
    ]

    journeyConnections.forEach(conn => {
      if (Array.isArray(conn.from) && Array.isArray(conn.to)) {
        conn.from.forEach(from => {
          conn.to.forEach(to => {
            if (from && to) {
              edges.push({
                from: from,
                to: to,
                color: { color: conn.color, opacity: 0.8 },
                width: conn.type === 'emergence' ? 3 : conn.type === 'challenge' ? 3 : conn.type === 'evolution' ? 4 : 5,
                dashes: false,
                title: `${conn.type} in hero's journey`,
                arrows: {
                  to: { enabled: true, scaleFactor: 0.8 }
                }
              })
            }
          })
        })
      }
    })

    // Add dimensional relationship edges (cross-dimension connections)
    const allProcessedNodes = [
      ...heroesArc.outcast, ...heroesArc.call_to_adventure,
      ...heroesArc.trials, ...heroesArc.transformation, ...heroesArc.heroes_return
    ]

    allProcessedNodes.forEach(node => {
      const nodeDimensions = node.dimensions || []
      allProcessedNodes.forEach(otherNode => {
        if (node.submission_hash === otherNode.submission_hash) return

        const otherDimensions = otherNode.dimensions || []
        const sharedDimensions = nodeDimensions.filter((dim: string) => otherDimensions.includes(dim))

        if (sharedDimensions.length > 0) {
          edges.push({
            from: node.submission_hash,
            to: otherNode.submission_hash,
            color: { color: '#6366F1', opacity: 0.4 },
            width: Math.min(sharedDimensions.length * 2, 4),
            dashes: true,
            title: `Shared dimensions: ${sharedDimensions.map((d: string) =>
              SYNTHVERSE_DIMENSIONS[d as keyof typeof SYNTHVERSE_DIMENSIONS]?.name || d
            ).join(', ')}`,
            metadata: {
              type: 'dimensional',
              sharedDimensions: sharedDimensions,
            },
          })
        }
      })
    })

    // Add paper relationship edges (filtered)
    let filteredEdges = [...mapData.edges]
    if (filterType !== 'all') {
      filteredEdges = filteredEdges.filter(e => e.overlap_type === filterType)
    }

    const nodeHashes = new Set(filteredNodes.map(n => n.submission_hash))
    filteredEdges = filteredEdges.filter(e =>
      nodeHashes.has(e.source_hash) && nodeHashes.has(e.target_hash)
    )

    filteredEdges.forEach(edge => {
      const edgeColor = OVERLAP_COLORS[edge.overlap_type] || '#94A3B8'
      const width = edge.overlap_type === 'exact_duplicate' ? 4 :
                   edge.overlap_type === 'high_redundancy' ? 3 :
                   edge.overlap_type === 'moderate_overlap' ? 2 : 1

      edges.push({
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
      })
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

  function toggleDimension(dimension: string) {
    const newDimensions = new Set(activeDimensions)
    if (dimension === 'all') {
      if (newDimensions.has('all')) {
        newDimensions.clear()
      } else {
        newDimensions.clear()
        newDimensions.add('all')
      }
    } else {
      newDimensions.delete('all')
      if (newDimensions.has(dimension)) {
        newDimensions.delete(dimension)
      } else {
        newDimensions.add(dimension)
      }
      // If no dimensions selected, default to 'all'
      if (newDimensions.size === 0) {
        newDimensions.add('all')
      }
    }
    setActiveDimensions(newDimensions)
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
        <h1 className="text-3xl font-bold">🌌 Multi-Dimensional Knowledge Cosmos</h1>
        <p className="text-muted-foreground mt-2">
          Navigate qualified contributions across 16 knowledge dimensions - from quantum elements to enterprise systems, revealing the interconnected web of scientific discovery
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
              <label className="block text-sm font-medium mb-2">Status (Qualified Only)</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Qualified</option>
                <option value="qualified">Qualified</option>
              </select>
              <p className="text-xs text-muted-foreground mt-1">
                Only qualified contributions are shown in the map
              </p>
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

          {/* Dimension Filters */}
          <div className="mt-4 pt-4 border-t">
            <label className="block text-sm font-medium mb-3">Knowledge Dimensions</label>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              <button
                onClick={() => toggleDimension('all')}
                className={`px-3 py-2 text-xs rounded-md border transition-colors ${
                  activeDimensions.has('all')
                    ? 'bg-blue-100 border-blue-300 text-blue-800'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                All Dimensions
              </button>
              {Object.entries(SYNTHVERSE_DIMENSIONS).map(([key, dimension]) => (
                <button
                  key={key}
                  onClick={() => toggleDimension(key)}
                  className={`px-3 py-2 text-xs rounded-md border transition-colors ${
                    activeDimensions.has(key)
                      ? 'text-white border-transparent'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                  style={activeDimensions.has(key) ? {
                    backgroundColor: dimension.color,
                    borderColor: dimension.color
                  } : {}}
                  title={dimension.description}
                >
                  {dimension.name}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hero's Journey Legend */}
      <Card>
        <CardHeader>
          <CardTitle>🏆 Hero's Knowledge Journey</CardTitle>
          <CardDescription>The narrative arc of scientific discovery from outcast to hero</CardDescription>
        </CardHeader>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="font-medium mb-2">Journey Phases</p>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-4 border-[#DC2626]" />
                  <span>Outcast (Rejected Ideas)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-4 border-[#EA580C]" />
                  <span>Call to Adventure</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-4 border-[#CA8A04]" />
                  <span>Trials & Tribulations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-4 border-[#16A34A]" />
                  <span>Transformation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-4 border-[#2563EB]" />
                  <span>Hero's Return</span>
                </div>
              </div>
            </div>
            <div>
              <p className="font-medium mb-2">Narrative Progression</p>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#EA580C]" />
                  <span>Emergence (Phase 1→2)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#CA8A04]" />
                  <span>Challenge (Phase 2→3)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#16A34A]" />
                  <span>Evolution (Phase 3→4)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#2563EB]" />
                  <span>Triumph (Phase 4→5)</span>
                </div>
              </div>
            </div>
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
              <p className="font-medium mb-2">Paper Relationships</p>
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
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-0.5 bg-[#6366F1]" style={{
                    backgroundImage: 'repeating-linear-gradient(to right, #6366F1 0, #6366F1 4px, transparent 4px, transparent 8px)'
                  }} />
                  <span>Shared Dimensions</span>
                </div>
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
