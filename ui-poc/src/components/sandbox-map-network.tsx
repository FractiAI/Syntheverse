'use client'

import { useEffect, useRef } from 'react'
import { Network, Data, Options } from 'vis-network/standalone'
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
  const networkInstanceRef = useRef<Network | null>(null)

  useEffect(() => {
    if (!networkRef.current || nodes.length === 0) return

    const data: Data = { nodes, edges }

    const options: Options = {
      nodes: {
        font: {
          size: 12,
        },
        borderWidth: 2,
      },
      edges: {
        smooth: {
          type: 'continuous',
          roundness: 0.5,
        },
        arrows: {
          to: {
            enabled: false,
          },
        },
      },
      physics: {
        enabled: true,
        stabilization: {
          enabled: true,
          iterations: 200,
        },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.1,
          springLength: 200,
          springConstant: 0.04,
          damping: 0.09,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
      },
      layout: {
        improvedLayout: true,
      },
    }

    // Destroy existing network
    if (networkInstanceRef.current) {
      networkInstanceRef.current.destroy()
    }

    // Create new network
    const network = new Network(networkRef.current, data, options)
    networkInstanceRef.current = network

    // Handle node click
    if (onNodeClick) {
      network.on('click', (params) => {
        if (params.nodes.length > 0) {
          onNodeClick(params.nodes[0] as string)
        }
      })
    }

    // Handle double click to navigate
    if (onNodeDoubleClick) {
      network.on('doubleClick', (params) => {
        if (params.nodes.length > 0) {
          onNodeDoubleClick(params.nodes[0] as string)
        }
      })
    }

    return () => {
      if (networkInstanceRef.current) {
        networkInstanceRef.current.destroy()
        networkInstanceRef.current = null
      }
    }
  }, [nodes, edges, onNodeClick, onNodeDoubleClick])

  return (
    <div
      ref={networkRef}
      className="w-full"
      style={{ height: '600px', minHeight: '600px' }}
    />
  )
}
