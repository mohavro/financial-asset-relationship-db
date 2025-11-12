/**
 * Comprehensive unit tests for NetworkVisualization component.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NetworkVisualization from '../../app/components/NetworkVisualization';
import type { VisualizationData } from '../../app/types/api';

jest.mock('react-plotly.js', () => {
  return function MockPlot({ data }: { data: unknown }) {
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
      {
        id: 'ASSET_2',
        name: 'Microsoft Corp.',
        symbol: 'MSFT',
        asset_class: 'EQUITY',
        x: 2.5,
        y: 3.3,
        z: 1.2,
        color: '#ff7f0e',
        size: 12,
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

  it('should show empty data message when nodes or edges are missing', () => {
    render(<NetworkVisualization data={{ nodes: [], edges: [] }} />);
    expect(screen.getByText('Visualization data is missing nodes or edges.')).toBeInTheDocument();
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
    expect(screen.getByText('No visualization data available.')).toBeInTheDocument();
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
    expect(screen.getByText('Visualization data is missing nodes or edges.')).toBeInTheDocument();
  });

  it('should show a helpful message when dataset is too large', () => {
    const bigData: VisualizationData = {
      nodes: Array.from({ length: 600 }, (_, index) => ({
        id: `NODE_${index}`,
        name: `Node ${index}`,
        symbol: `SYM${index}`,
        asset_class: 'EQUITY',
        x: Math.random(),
        y: Math.random(),
        z: Math.random(),
        color: '#000000',
        size: 5,
      })),
      edges: Array.from({ length: 2001 }, (_, index) => ({
        source: 'NODE_0',
        target: `NODE_${index % 599 + 1}`,
        relationship_type: 'TEST',
        strength: 0.5,
      })),
    };

    render(<NetworkVisualization data={bigData} />);

    expect(
      screen.getByText(/Visualization is unavailable because the dataset is too large/)
    ).toBeInTheDocument();
  });
});
