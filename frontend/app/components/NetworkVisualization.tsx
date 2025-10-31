'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import type { VisualizationData } from '../types/api';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

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

    // Create edge traces
    const edgeTraces = data.edges.map(edge => {
      const sourceNode = data.nodes.find(n => n.id === edge.source);
      const targetNode = data.nodes.find(n => n.id === edge.target);
      
      if (!sourceNode || !targetNode) return null;

      return {
        type: 'scatter3d',
        mode: 'lines',
        x: [sourceNode.x, targetNode.x],
        y: [sourceNode.y, targetNode.y],
        z: [sourceNode.z, targetNode.z],
        line: {
          color: `rgba(125, 125, 125, ${edge.strength})`,
          width: edge.strength * 3
        },
        hoverinfo: 'none',
        showlegend: false
      };
    }).filter(trace => trace !== null);

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
