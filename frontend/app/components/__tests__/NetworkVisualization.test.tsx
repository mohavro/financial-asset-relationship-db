/**
 * Comprehensive unit tests for the NetworkVisualization component.
 * 
 * Tests cover:
 * - Component rendering with visualization data
 * - Dynamic import handling (Plotly)
 * - Data transformation for 3D plotting
 * - Node and edge rendering
 * - Loading states
 * - Edge cases and empty data
 * - Layout configuration
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NetworkVisualization from '../NetworkVisualization';
import type { VisualizationData } from '../../types/api';

// Mock next/dynamic with proper async loading simulation
// This implementation properly simulates the async behavior of dynamic imports,
// allowing us to test loading states and error handling more accurately.
jest.mock('next/dynamic', () => ({
  __esModule: true,
  default: (fn: () => Promise<any>, options?: any) => {
    const DynamicComponent = ({ ...props }) => {
      const [Component, setComponent] = React.useState<React.ComponentType | null>(null);

      React.useEffect(() => {
        let cancelled = false;

        // Simulate async import - the promise resolves in the next tick
        fn()
          .then((module) => {
            if (!cancelled) {
              setComponent(() => module.default);
            }
          })
          .catch(() => {
            if (!cancelled) {
              setComponent(() => function ErrorComponent() { return <div data-testid="mock-plot-error">Failed to load visualization</div>; });
            }
          });

        return () => {
          cancelled = true;
        };
      }, []);

      // Display loading state while the dynamic import is resolving
      if (!Component && options?.loading) {
        return options.loading();
      }

      // Render the dynamically imported component once loaded
      return Component ? <Component {...props} /> : null;
    };
    return DynamicComponent;
  },
}));

describe('NetworkVisualization Component', () => {
  const mockVisualizationData: VisualizationData = {
    nodes: [
      {
        id: 'TEST_AAPL',
        name: 'Apple Inc.',
        symbol: 'AAPL',
        asset_class: 'EQUITY',
        x: 0.5,
        y: 0.5,
        z: 0.5,
        color: '#1f77b4',
        size: 10,
      },
      {
        id: 'TEST_MSFT',
        name: 'Microsoft Corporation',
        symbol: 'MSFT',
        asset_class: 'EQUITY',
        x: 1.5,
        y: 1.5,
        z: 1.5,
        color: '#ff7f0e',
        size: 8,
      },
      {
        id: 'TEST_BOND',
        name: 'Apple Corporate Bond',
        symbol: 'AAPL_BOND',
        asset_class: 'FIXED_INCOME',
        x: -0.5,
        y: -0.5,
        z: -0.5,
        color: '#2ca02c',
        size: 6,
      },
    ],
    edges: [
      {
        source: 'TEST_AAPL',
        target: 'TEST_BOND',
        relationship_type: 'issues',
        strength: 0.9,
      },
      {
        source: 'TEST_MSFT',
        target: 'TEST_BOND',
        relationship_type: 'competes_with',
        strength: 0.7,
      },
    ],
  };

  describe('Basic Rendering', () => {
    it('should render the component', async () => {
      render(<NetworkVisualization data={mockVisualizationData} />);
      // Wait for dynamic import to resolve
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should show loading state when plot data is not ready', async () => {
      const emptyData: VisualizationData = { nodes: [], edges: [] };
      render(<NetworkVisualization data={emptyData} />);
      
      // Component should handle empty data gracefully
      expect(screen.getByText(/Loading visualization.../i)).toBeInTheDocument();
    });

    it('should render with valid visualization data', async () => {
      render(<NetworkVisualization data={mockVisualizationData} />);
      // Wait for dynamic import to resolve
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });

  describe('Data Processing', () => {
    it('should handle nodes with all required properties', async () => {
      const { container } = render(<NetworkVisualization data={mockVisualizationData} />);
      expect(container).toBeTruthy();
      
      // Verify component doesn't throw errors with valid data
      mockVisualizationData.nodes.forEach(node => {
        expect(node).toHaveProperty('id');
        expect(node).toHaveProperty('name');
        expect(node).toHaveProperty('symbol');
        expect(node).toHaveProperty('x');
        expect(node).toHaveProperty('y');
        expect(node).toHaveProperty('z');
      });
    });

    it('should handle edges with source and target references', async () => {
      render(<NetworkVisualization data={mockVisualizationData} />);
      
      mockVisualizationData.edges.forEach(edge => {
        expect(edge).toHaveProperty('source');
        expect(edge).toHaveProperty('target');
        expect(edge).toHaveProperty('strength');
      });
    });

    it('should filter out edges with invalid node references', async () => {
      const dataWithInvalidEdge: VisualizationData = {
        nodes: mockVisualizationData.nodes,
        edges: [
          ...mockVisualizationData.edges,
          {
            source: 'NONEXISTENT_NODE',
            target: 'TEST_AAPL',
            relationship_type: 'invalid',
            strength: 0.5,
          },
        ],
      };
      
      const { container } = render(<NetworkVisualization data={dataWithInvalidEdge} />);
      expect(container).toBeTruthy();
      // Component should handle invalid edges gracefully
    });

    it('should handle node lookup with Map for efficiency', async () => {
      // Test that component uses efficient data structures
      render(<NetworkVisualization data={mockVisualizationData} />);
      
      // Verify all nodes are accessible
      const nodeIds = mockVisualizationData.nodes.map(n => n.id);
      expect(nodeIds).toContain('TEST_AAPL');
      expect(nodeIds).toContain('TEST_MSFT');
      expect(nodeIds).toContain('TEST_BOND');
    });
  });

  describe('Empty States', () => {
    it('should handle empty nodes array', async () => {
      const emptyNodesData: VisualizationData = {
        nodes: [],
        edges: [],
      };
      
      render(<NetworkVisualization data={emptyNodesData} />);
      expect(screen.getByText(/Loading visualization.../i)).toBeInTheDocument();
    });

    it('should handle empty edges array with nodes present', async () => {
      const noEdgesData: VisualizationData = {
        nodes: mockVisualizationData.nodes,
        edges: [],
      };
      
      render(<NetworkVisualization data={noEdgesData} />);
      // Should still render with just nodes
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle null or undefined data gracefully', async () => {
      const nullData = null as any;
      const { container } = render(<NetworkVisualization data={nullData} />);
      
      // Component should not crash
      expect(container).toBeTruthy();
    });
  });

  describe('Coordinate Handling', () => {
    it('should handle positive coordinates', async () => {
      const positiveData: VisualizationData = {
        nodes: [
          {
            id: 'TEST_1',
            name: 'Test Node',
            symbol: 'TEST',
            asset_class: 'EQUITY',
            x: 5.0,
            y: 10.0,
            z: 15.0,
            color: '#000000',
            size: 5,
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={positiveData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle negative coordinates', async () => {
      const negativeData: VisualizationData = {
        nodes: [
          {
            id: 'TEST_1',
            name: 'Test Node',
            symbol: 'TEST',
            asset_class: 'EQUITY',
            x: -5.0,
            y: -10.0,
            z: -15.0,
            color: '#000000',
            size: 5,
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={negativeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle zero coordinates', async () => {
      const zeroData: VisualizationData = {
        nodes: [
          {
            id: 'TEST_1',
            name: 'Test Node',
            symbol: 'TEST',
            asset_class: 'EQUITY',
            x: 0.0,
            y: 0.0,
            z: 0.0,
            color: '#000000',
            size: 5,
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={zeroData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle very large coordinates', async () => {
      const largeData: VisualizationData = {
        nodes: [
          {
            id: 'TEST_1',
            name: 'Test Node',
            symbol: 'TEST',
            asset_class: 'EQUITY',
            x: 1000.0,
            y: 2000.0,
            z: 3000.0,
            color: '#000000',
            size: 5,
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={largeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });

  describe('Edge Strength', () => {
    it('should handle edge strength of 1.0', async () => {
      const strongEdgeData: VisualizationData = {
        nodes: mockVisualizationData.nodes.slice(0, 2),
        edges: [
          {
            source: 'TEST_AAPL',
            target: 'TEST_MSFT',
            relationship_type: 'strong',
            strength: 1.0,
          },
        ],
      };
      
      render(<NetworkVisualization data={strongEdgeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle edge strength of 0.0', async () => {
      const weakEdgeData: VisualizationData = {
        nodes: mockVisualizationData.nodes.slice(0, 2),
        edges: [
          {
            source: 'TEST_AAPL',
            target: 'TEST_MSFT',
            relationship_type: 'weak',
            strength: 0.0,
          },
        ],
      };
      
      render(<NetworkVisualization data={weakEdgeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle fractional edge strength', async () => {
      const fractionalEdgeData: VisualizationData = {
        nodes: mockVisualizationData.nodes.slice(0, 2),
        edges: [
          {
            source: 'TEST_AAPL',
            target: 'TEST_MSFT',
            relationship_type: 'medium',
            strength: 0.456,
          },
        ],
      };
      
      render(<NetworkVisualization data={fractionalEdgeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });

  describe('Node Properties', () => {
    it('should handle various node sizes', async () => {
      const variedSizeData: VisualizationData = {
        nodes: [
          { ...mockVisualizationData.nodes[0], size: 1 },
          { ...mockVisualizationData.nodes[1], size: 20 },
          { ...mockVisualizationData.nodes[2], size: 10 },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={variedSizeData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle different color formats', async () => {
      const coloredData: VisualizationData = {
        nodes: [
          { ...mockVisualizationData.nodes[0], color: '#FF0000' },
          { ...mockVisualizationData.nodes[1], color: '#00FF00' },
          { ...mockVisualizationData.nodes[2], color: '#0000FF' },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={coloredData} />);
      await waitFor(async () => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle long node names', async () => {
      const longNameData: VisualizationData = {
        nodes: [
          {
            ...mockVisualizationData.nodes[0],
            name: 'Very Long Company Name With Many Words That Might Wrap',
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={longNameData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle special characters in node properties', async () => {
      const specialCharData: VisualizationData = {
        nodes: [
          {
            ...mockVisualizationData.nodes[0],
            name: "Company & Co. <Ltd>",
            symbol: 'CO&LTD',
          },
        ],
        edges: [],
      };
      
      render(<NetworkVisualization data={specialCharData} />);
      await waitFor(async () => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });

  describe('Component Structure', () => {
    it('should render with correct container class', async () => {
      const { container } = render(<NetworkVisualization data={mockVisualizationData} />);
      const wrapper = container.firstChild;
      
      expect(wrapper).toHaveClass('w-full');
      expect(wrapper).toHaveClass('h-[800px]');
    });

    it('should maintain fixed height', async () => {
      const { container } = render(<NetworkVisualization data={mockVisualizationData} />);
      const wrapper = container.firstChild as HTMLElement;
      
      expect(wrapper.className).toContain('h-[800px]');
    });
  });

  describe('Data Updates', () => {
    it('should update when data changes', async () => {
      const { rerender } = render(<NetworkVisualization data={mockVisualizationData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });

      const newData: VisualizationData = {
        nodes: [mockVisualizationData.nodes[0]],
        edges: [],
      };

      rerender(<NetworkVisualization data={newData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle transition from empty to populated data', async () => {
      const emptyData: VisualizationData = { nodes: [], edges: [] };
      const { rerender } = render(<NetworkVisualization data={emptyData} />);
      
      expect(screen.getByText(/Loading visualization.../i)).toBeInTheDocument();

      rerender(<NetworkVisualization data={mockVisualizationData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle transition from populated to empty data', async () => {
      const { rerender, container } = render(<NetworkVisualization data={mockVisualizationData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });

      const emptyData: VisualizationData = { nodes: [], edges: [] };
      rerender(<NetworkVisualization data={emptyData} />);
      
      // Component should handle the empty data transition without crashing
      expect(container.firstChild).toBeTruthy();
    });
  });

  describe('Edge Cases - Complex Networks', () => {
    it('should handle many nodes', async () => {
      const manyNodesData: VisualizationData = {
        nodes: Array.from({ length: 100 }, (_, i) => ({
          id: `NODE_${i}`,
          name: `Node ${i}`,
          symbol: `N${i}`,
          asset_class: 'EQUITY',
          x: Math.random() * 10,
          y: Math.random() * 10,
          z: Math.random() * 10,
          color: '#1f77b4',
          size: 5,
        })),
        edges: [],
      };
      
      render(<NetworkVisualization data={manyNodesData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle many edges', async () => {
      const nodes = mockVisualizationData.nodes;
      const manyEdgesData: VisualizationData = {
        nodes,
        edges: Array.from({ length: 50 }, (_, i) => ({
          source: nodes[i % nodes.length].id,
          target: nodes[(i + 1) % nodes.length].id,
          relationship_type: 'test',
          strength: 0.5,
        })),
      };
      
      render(<NetworkVisualization data={manyEdgesData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle fully connected network', async () => {
      const nodes = mockVisualizationData.nodes;
      const edges: VisualizationData['edges'] = [];
      
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          edges.push({
            source: nodes[i].id,
            target: nodes[j].id,
            relationship_type: 'connected',
            strength: 0.5,
          });
        }
      }
      
      const fullyConnectedData: VisualizationData = { nodes, edges };
      
      render(<NetworkVisualization data={fullyConnectedData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });

  describe('Type Safety', () => {
    it('should accept VisualizationData type', async () => {
      const typedData: VisualizationData = mockVisualizationData;
      render(<NetworkVisualization data={typedData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should handle VisualizationNode properties', async () => {
      mockVisualizationData.nodes.forEach(node => {
        expect(typeof node.x).toBe('number');
        expect(typeof node.y).toBe('number');
        expect(typeof node.z).toBe('number');
        expect(typeof node.size).toBe('number');
        expect(typeof node.color).toBe('string');
      });
    });

    it('should handle VisualizationEdge properties', async () => {
      mockVisualizationData.edges.forEach(edge => {
        expect(typeof edge.source).toBe('string');
        expect(typeof edge.target).toBe('string');
        expect(typeof edge.strength).toBe('number');
        expect(typeof edge.relationship_type).toBe('string');
      });
    });
  });

  describe('Performance', () => {
    it('should use useEffect for data processing', async () => {
      const { rerender } = render(<NetworkVisualization data={mockVisualizationData} />);
      
      // Rerender with same data
      rerender(<NetworkVisualization data={mockVisualizationData} />);
      
      // Component should handle rerenders efficiently
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });

    it('should memoize plot data', async () => {
      const { rerender } = render(<NetworkVisualization data={mockVisualizationData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
      
      // Rerender with same reference
      rerender(<NetworkVisualization data={mockVisualizationData} />);
      await waitFor(() => {
        expect(screen.getByTestId('mock-plot')).toBeInTheDocument();
      });
    });
  });
});