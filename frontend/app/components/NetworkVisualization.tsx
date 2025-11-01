'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import type { VisualizationData } from '../types/api';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { 
  ssr: false,
  loading: () => <div className="text-center p-8">Loading visualization...</div>
});

interface NetworkVisualizationProps {
  data: VisualizationData;
}

export default function NetworkVisualization({ data }: NetworkVisualizationProps) {
  const [plotData, setPlotData] = useState<any[]>([]);

  useEffect(() => {
    if (!data || !data.nodes || !data.edges) return;

    // Create node trace
    const nodeTrace = {
      type: 'scatter3d',
      mode: 'markers+text',
      x: data.nodes.map(n => n.x),
      y: data.nodes.map(n => n.y),
      z: data.nodes.map(n => n.z),
      text: data.nodes.map(n => n.symbol),
      hovertext: data.nodes.map(n => `${n.name} (${n.symbol})<br>Class: ${n.asset_class}`),
      hoverinfo: 'text',
      marker: {
        size: data.nodes.map(n => n.size),
        color: data.nodes.map(n => n.color),
        line: {
          color: 'white',
          width: 0.5
        }
      },
      textposition: 'top center',
      textfont: {
        size: 8,
      }
    };

    // Create node lookup map for O(1) access
    const nodeMap = new Map(data.nodes.map(node => [node.id, node]));

    // Create edge traces with type predicate to filter nulls
    const edgeTraces = data.edges
      .map(edge => {
        const sourceNode = nodeMap.get(edge.source);
        const targetNode = nodeMap.get(edge.target);
        

        return {
          type: 'scatter3d' as const,
          mode: 'lines' as const,
          x: [sourceNode.x, targetNode.x],
          y: [sourceNode.y, targetNode.y],
          z: [sourceNode.z, targetNode.z],
          line: {
            color: `rgba(125, 125, 125, ${edge.strength})`,
            width: edge.strength * 3
          },
          hoverinfo: 'none' as const,
          showlegend: false
        };
      })
      .filter((trace): trace is NonNullable<typeof trace> => trace !== null);

    setPlotData([...edgeTraces, nodeTrace]);
  }, [data]);

  if (!plotData || plotData.length === 0) {
    return <div className="text-center p-8">Loading visualization...</div>;
  }

  return (
    <div className="w-full h-[800px]">
      <Plot
        data={plotData}
        layout={{
          title: '3D Asset Relationship Network',
          showlegend: false,
          scene: {
            xaxis: { showgrid: false, zeroline: false, showticklabels: false },
            yaxis: { showgrid: false, zeroline: false, showticklabels: false },
            zaxis: { showgrid: false, zeroline: false, showticklabels: false },
            camera: {
              eye: { x: 1.5, y: 1.5, z: 1.5 }
            }
          },
          hovermode: 'closest',
          margin: { l: 0, r: 0, b: 0, t: 40 },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)'
        }}
        config={{
          displayModeBar: true,
          displaylogo: false,
          responsive: true
        }}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
