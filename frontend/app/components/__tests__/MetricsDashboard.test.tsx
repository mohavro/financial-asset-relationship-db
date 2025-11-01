/**
 * Comprehensive unit tests for the MetricsDashboard component.
 * 
 * Tests cover:
 * - Metrics display and formatting
 * - Number formatting and precision
 * - Percentage calculations
 * - Asset class breakdown rendering
 * - Edge cases and boundary values
 * - Styling and layout
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MetricsDashboard from '../MetricsDashboard';
import type { Metrics } from '../../types/api';

describe('MetricsDashboard Component', () => {
  const mockMetrics: Metrics = {
    total_assets: 50,
    total_relationships: 120,
    asset_classes: {
      EQUITY: 25,
      FIXED_INCOME: 15,
      COMMODITY: 7,
      CURRENCY: 3,
    },
    avg_degree: 4.8,
    max_degree: 12,
    network_density: 0.096,
  };

  describe('Basic Rendering', () => {
    it('should render all metric cards', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);

      expect(screen.getByText('Total Assets')).toBeInTheDocument();
      expect(screen.getByText('Total Relationships')).toBeInTheDocument();
      expect(screen.getByText('Network Density')).toBeInTheDocument();
      expect(screen.getByText('Average Degree')).toBeInTheDocument();
      expect(screen.getByText('Max Degree')).toBeInTheDocument();
      expect(screen.getByText('Asset Classes')).toBeInTheDocument();
    });

    it('should display total assets correctly', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('50')).toBeInTheDocument();
    });

    it('should display total relationships correctly', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('120')).toBeInTheDocument();
    });

    it('should display max degree correctly', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('12')).toBeInTheDocument();
    });
  });

  describe('Number Formatting', () => {
    it('should format average degree with 2 decimal places', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('4.80')).toBeInTheDocument();
    });

    it('should format network density as percentage with 2 decimal places', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('9.60%')).toBeInTheDocument();
    });

    it('should handle zero average degree', () => {
      const metricsWithZero = { ...mockMetrics, avg_degree: 0 };
      render(<MetricsDashboard metrics={metricsWithZero} />);
      expect(screen.getByText('0.00')).toBeInTheDocument();
    });

    it('should handle very small network density', () => {
      const metricsWithSmallDensity = { ...mockMetrics, network_density: 0.001 };
      render(<MetricsDashboard metrics={metricsWithSmallDensity} />);
      expect(screen.getByText('0.10%')).toBeInTheDocument();
    });

    it('should handle 100% network density', () => {
      const metricsWithFullDensity = { ...mockMetrics, network_density: 1.0 };
      render(<MetricsDashboard metrics={metricsWithFullDensity} />);
      expect(screen.getByText('100.00%')).toBeInTheDocument();
    });

    it('should handle large numbers for total assets', () => {
      const metricsWithLargeNumbers = { ...mockMetrics, total_assets: 10000 };
      render(<MetricsDashboard metrics={metricsWithLargeNumbers} />);
      expect(screen.getByText('10000')).toBeInTheDocument();
    });
  });

  describe('Asset Classes Display', () => {
    it('should display all asset classes', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);

      expect(screen.getByText('EQUITY:')).toBeInTheDocument();
      expect(screen.getByText('FIXED_INCOME:')).toBeInTheDocument();
      expect(screen.getByText('COMMODITY:')).toBeInTheDocument();
      expect(screen.getByText('CURRENCY:')).toBeInTheDocument();
    });

    it('should display correct counts for each asset class', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);

      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('7')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('should handle empty asset classes', () => {
      const metricsWithNoAssetClasses = { ...mockMetrics, asset_classes: {} };
      const { container } = render(<MetricsDashboard metrics={metricsWithNoAssetClasses} />);
      
      // Asset Classes card should still render but with no items
      expect(screen.getByText('Asset Classes')).toBeInTheDocument();
      
      // Should not have any asset class items
      const assetClassCard = container.querySelector('.space-y-1');
      expect(assetClassCard?.children.length).toBe(0);
    });

    it('should handle single asset class', () => {
      const metricsWithSingleClass = {
        ...mockMetrics,
        asset_classes: { EQUITY: 50 },
      };
      render(<MetricsDashboard metrics={metricsWithSingleClass} />);

      expect(screen.getByText('EQUITY:')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
    });

    it('should handle zero count asset classes', () => {
      const metricsWithZeroCounts = {
        ...mockMetrics,
        asset_classes: {
          EQUITY: 0,
          FIXED_INCOME: 0,
        },
      };
      render(<MetricsDashboard metrics={metricsWithZeroCounts} />);

      const zeroCounts = screen.getAllByText('0');
      expect(zeroCounts.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Grid Layout', () => {
    it('should render in grid layout', () => {
      const { container } = render(<MetricsDashboard metrics={mockMetrics} />);
      const grid = container.firstChild;
      
      expect(grid).toHaveClass('grid');
      expect(grid).toHaveClass('grid-cols-1');
      expect(grid).toHaveClass('md:grid-cols-2');
      expect(grid).toHaveClass('lg:grid-cols-3');
    });

    it('should render 6 metric cards', () => {
      const { container } = render(<MetricsDashboard metrics={mockMetrics} />);
      const cards = container.querySelectorAll('.bg-white.rounded-lg.shadow-md');
      expect(cards.length).toBe(6);
    });
  });

  describe('Styling', () => {
    it('should apply correct color to total assets', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const totalAssetsValue = screen.getByText('50');
      expect(totalAssetsValue).toHaveClass('text-blue-600');
    });

    it('should apply correct color to total relationships', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const totalRelationshipsValue = screen.getByText('120');
      expect(totalRelationshipsValue).toHaveClass('text-green-600');
    });

    it('should apply correct color to network density', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const networkDensityValue = screen.getByText('9.60%');
      expect(networkDensityValue).toHaveClass('text-purple-600');
    });

    it('should apply correct color to average degree', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const avgDegreeValue = screen.getByText('4.80');
      expect(avgDegreeValue).toHaveClass('text-orange-600');
    });

    it('should apply correct color to max degree', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const maxDegreeValue = screen.getByText('12');
      expect(maxDegreeValue).toHaveClass('text-red-600');
    });
  });

  describe('Edge Cases', () => {
    it('should handle metrics with all zeros', () => {
      const zeroMetrics: Metrics = {
        total_assets: 0,
        total_relationships: 0,
        asset_classes: {},
        avg_degree: 0,
        max_degree: 0,
        network_density: 0,
      };
      render(<MetricsDashboard metrics={zeroMetrics} />);

      expect(screen.getByText('0.00')).toBeInTheDocument(); // avg_degree
      expect(screen.getByText('0.00%')).toBeInTheDocument(); // network_density
    });

    it('should handle very large average degree', () => {
      const metricsWithLargeDegree = { ...mockMetrics, avg_degree: 999.99 };
      render(<MetricsDashboard metrics={metricsWithLargeDegree} />);
      expect(screen.getByText('999.99')).toBeInTheDocument();
    });

    it('should handle fractional average degree', () => {
      const metricsWithFractionalDegree = { ...mockMetrics, avg_degree: 2.345678 };
      render(<MetricsDashboard metrics={metricsWithFractionalDegree} />);
      expect(screen.getByText('2.35')).toBeInTheDocument();
    });

    it('should handle network density rounding edge cases', () => {
      const metricsWithRounding = { ...mockMetrics, network_density: 0.09995 };
      render(<MetricsDashboard metrics={metricsWithRounding} />);
      // Should round to 10.00%
      expect(screen.getByText('10.00%')).toBeInTheDocument();
    });
  });

  describe('Prop Changes', () => {
    it('should update when metrics change', () => {
      const { rerender } = render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('50')).toBeInTheDocument();

      const newMetrics = { ...mockMetrics, total_assets: 100 };
      rerender(<MetricsDashboard metrics={newMetrics} />);
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('should update network density display when changed', () => {
      const { rerender } = render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('9.60%')).toBeInTheDocument();

      const newMetrics = { ...mockMetrics, network_density: 0.5 };
      rerender(<MetricsDashboard metrics={newMetrics} />);
      expect(screen.getByText('50.00%')).toBeInTheDocument();
    });

    it('should update asset classes when changed', () => {
      const { rerender } = render(<MetricsDashboard metrics={mockMetrics} />);
      expect(screen.getByText('EQUITY:')).toBeInTheDocument();

      const newMetrics = {
        ...mockMetrics,
        asset_classes: { BOND: 10 },
      };
      rerender(<MetricsDashboard metrics={newMetrics} />);
      expect(screen.getByText('BOND:')).toBeInTheDocument();
    });
  });

  describe('Typography', () => {
    it('should use correct font sizes for titles', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const titles = screen.getAllByText(/Total Assets|Total Relationships|Network Density|Average Degree|Max Degree|Asset Classes/);
      
      titles.forEach(title => {
        expect(title).toHaveClass('text-lg');
        expect(title).toHaveClass('font-semibold');
      });
    });

    it('should use correct font sizes for values', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      const totalAssets = screen.getByText('50');
      
      expect(totalAssets).toHaveClass('text-3xl');
      expect(totalAssets).toHaveClass('font-bold');
    });
  });

  describe('Accessibility', () => {
    it('should have proper semantic structure', () => {
      const { container } = render(<MetricsDashboard metrics={mockMetrics} />);
      
      // Check for heading elements
      const headings = container.querySelectorAll('h3');
      expect(headings.length).toBe(6);
    });

    it('should have readable contrast', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      
      // Check that text colors are applied
      const totalAssets = screen.getByText('50');
      expect(totalAssets).toHaveClass('text-blue-600');
      
      // Blue-600 has good contrast on white background
    });
  });

  describe('Asset Classes Formatting', () => {
    it('should render asset class names with colon', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      
      expect(screen.getByText('EQUITY:')).toBeInTheDocument();
      expect(screen.getByText('FIXED_INCOME:')).toBeInTheDocument();
    });

    it('should separate class name and count', () => {
      const { container } = render(<MetricsDashboard metrics={mockMetrics} />);
      
      // Each asset class should be in a flex container with space-between
      const assetClassItems = container.querySelectorAll('.flex.justify-between');
      expect(assetClassItems.length).toBeGreaterThan(0);
    });

    it('should apply correct styling to asset class counts', () => {
      render(<MetricsDashboard metrics={mockMetrics} />);
      
      const count = screen.getByText('25');
      expect(count).toHaveClass('font-semibold');
      expect(count).toHaveClass('text-gray-800');
    });
  });
});