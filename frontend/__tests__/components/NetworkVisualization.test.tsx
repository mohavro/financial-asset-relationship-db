/**
 * Comprehensive unit tests for NetworkVisualization component.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NetworkVisualization from '../../app/components/NetworkVisualization';
import type { VisualizationData } from '../../app/types/api';

jest.mock('react-plotly.js', () => {
  return function MockPlot({ data }: any) {
    return (
      <div data-testid="mock-plot">
        <div data-testid="plot-data">{JSON.stringify(data)}</div>
      </div>
    );
  };
});

describe('NetworkVisualization Component', () => {
  const mockData: VisualizationData = {
    nodes: [
      {
        id: 'ASSET_1',
        name: 'Apple Inc.',
        symbol: 'AAPL',
        asset_class: 'EQUITY',
        x: 1.5,
        y: 2.3,
        z: 0.8,
        color: '#1f77b4',
        size: 10,
      },
    ],
    edges: [
      {
        source: 'ASSET_1',
        target: 'ASSET_2',
        relationship_type: 'TEST',
        strength: 0.7,
      },
    ],
  };

  it('should show loading message for empty data', () => {
    render(<NetworkVisualization data={{ nodes: [], edges: [] }} />);
    expect(screen.getByText('Loading visualization...')).toBeInTheDocument();
  });

  it('should render plot with data', async () => {
    render(<NetworkVisualization data={mockData} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
    });
  });

  it('should process node coordinates', async () => {
    render(<NetworkVisualization data={mockData} />);
    
    await waitFor(() => {
      const plotData = screen.getByTestId('plot-data');
      const data = JSON.parse(plotData.textContent || '[]');
      expect(data.length).toBeGreaterThan(0);
    });
  });

  it('should handle null data gracefully', () => {
    render(<NetworkVisualization data={null as any} />);
    expect(screen.getByText('Loading visualization...')).toBeInTheDocument();
  });

  it('should update when data changes', async () => {
    const { rerender } = render(<NetworkVisualization data={mockData} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
    });

    const newData: VisualizationData = {
      nodes: [],
      edges: [],
    };

    rerender(<NetworkVisualization data={newData} />);
    expect(screen.getByText('Loading visualization...')).toBeInTheDocument();
  });
});