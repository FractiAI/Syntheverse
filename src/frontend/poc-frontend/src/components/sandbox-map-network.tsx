'use client'

import { useEffect, useRef, useState } from 'react'

// Import CSS statically
import 'vis-network/styles/vis-network.min.css'

interface SandboxMapNetworkProps {
  nodes: any[]
  edges: any[]
  onNodeClick?: (nodeId: string) => void
  onNodeDoubleClick?: (nodeId: string) => void
}

export default function SandboxMapNetwork({
  nodes,
  edges,
  onNodeClick,
  onNodeDoubleClick,
}: SandboxMapNetworkProps) {
  const networkRef = useRef<HTMLDivElement>(null)
  const networkInstanceRef = useRef<any>(null)
  const [networkLoaded, setNetworkLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Load vis-network dynamically if not already loaded
    const loadNetwork = async () => {
      try {
        if (typeof window !== 'undefined') {
          console.log('Loading vis-network...')
          const visNetwork = await import('vis-network/standalone')
          console.log('vis-network loaded successfully')
          setNetworkLoaded(true)
        }
      } catch (err) {
        console.error('Failed to load vis-network:', err)
        setError('Failed to load network visualization library')
      }
    }

    loadNetwork()
  }, [])

  useEffect(() => {
    // Only proceed if network is loaded and we have data
    console.log('Network component useEffect:', { networkLoaded, hasRef: !!networkRef.current, nodeCount: nodes.length })
    if (!networkLoaded || !networkRef.current) {
      console.log('Skipping network creation - not ready:', { networkLoaded, hasRef: !!networkRef.current })
      return
    }

    if (nodes.length === 0) {
      console.log('No nodes to display')
      return
    }

    const createNetwork = async () => {
      try {
        // Import vis-network dynamically
        const visNetwork = await import('vis-network/standalone')
        const Network = visNetwork.Network

        const data = { nodes, edges }

        const options = {
          nodes: {
            font: {
              size: 12,
            },
            borderWidth: 2,
            fixed: {
              x: true,
              y: true,
            },
          },
          edges: {
            smooth: {
              type: 'curvedCW',
              roundness: 0.2,
            },
            arrows: {
              to: {
                enabled: true,
                scaleFactor: 0.8,
                type: 'arrow',
              },
            },
            color: {
              inherit: false,
            },
          },
          physics: {
            enabled: false, // Disable physics for tree structure
            stabilization: false,
          },
          interaction: {
            hover: true,
            tooltipDelay: 100,
            zoomView: true,
            dragView: true,
            dragNodes: false, // Prevent dragging to maintain tree structure
          },
          layout: {
            hierarchical: {
              enabled: false, // We handle positioning manually
            },
          },
        }

        // Destroy existing network
        if (networkInstanceRef.current) {
          networkInstanceRef.current.destroy()
        }

        // Create new network
        console.log('Creating network with data:', { nodes: data.nodes.length, edges: data.edges.length })
        console.log('Network options:', options)
        console.log('Container element:', networkRef.current)

        const network = new Network(networkRef.current, data, options)
        networkInstanceRef.current = network
        console.log('Network created successfully')

        // Handle node click
        if (onNodeClick) {
          network.on('click', (params: any) => {
            if (params.nodes.length > 0) {
              onNodeClick(params.nodes[0] as string)
            }
          })
        }

        // Handle double click to navigate
        if (onNodeDoubleClick) {
          network.on('doubleClick', (params: any) => {
            if (params.nodes.length > 0) {
              onNodeDoubleClick(params.nodes[0] as string)
            }
          })
        }

        // Verify the network was created
        setTimeout(() => {
          console.log('Network verification:', {
            exists: !!networkInstanceRef.current,
            container: networkRef.current,
            canvas: networkRef.current?.querySelector('canvas')
          })
        }, 1000)

      } catch (error) {
        console.error('Error creating network:', error)
        setError('Failed to create network visualization')
      }
    }

    createNetwork()

    return () => {
      if (networkInstanceRef.current) {
        networkInstanceRef.current.destroy()
        networkInstanceRef.current = null
      }
    }
  }, [networkLoaded, nodes, edges, onNodeClick, onNodeDoubleClick])

  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-[600px] border rounded-lg bg-muted/50">
        <div className="text-center">
          <p className="text-destructive font-medium">Network Visualization Error</p>
          <p className="text-sm text-muted-foreground mt-2">{error}</p>
        </div>
      </div>
    )
  }

  if (!networkLoaded) {
    return (
      <div className="flex items-center justify-center w-full h-[600px] border rounded-lg bg-muted/50">
        <div className="text-muted-foreground">Loading network visualization...</div>
      </div>
    )
  }

  // Show basic data if network fails or for debugging
  if (error || nodes.length === 0) {
    return (
      <div className="w-full border rounded-lg p-8 text-center" style={{ height: '600px', backgroundColor: '#f8fafc' }}>
        {error ? (
          <div>
            <p className="text-red-600 font-medium">Network Error</p>
            <p className="text-sm text-gray-600 mt-2">{error}</p>
          </div>
        ) : (
          <div>
            <p className="text-gray-600 font-medium">No Data to Visualize</p>
            <p className="text-sm text-gray-500 mt-2">Submit contributions to see the network map</p>
          </div>
        )}
        {nodes.length > 0 && (
          <div className="mt-4 text-left max-w-md mx-auto">
            <p className="text-sm font-medium mb-2">Available Data:</p>
            <div className="bg-white p-3 rounded border text-xs">
              <p><strong>Nodes:</strong> {nodes.length}</p>
              <p><strong>Edges:</strong> {edges.length}</p>
              {nodes.slice(0, 3).map((node, i) => (
                <p key={i} className="truncate">• {node.label || node.id}</p>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      ref={networkRef}
      className="w-full border rounded-lg"
      style={{ height: '600px', minHeight: '600px', backgroundColor: '#f8fafc' }}
    />
  )
}
