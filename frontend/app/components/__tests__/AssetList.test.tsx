/**
 * Comprehensive unit tests for the AssetList component.
 * 
 * Tests cover:
 * - Component rendering and loading states
 * - Asset data display and formatting
 * - Filter functionality (asset class and sector)
 * - API integration and error handling
 * - User interactions and callbacks
 * - Edge cases and empty states
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AssetList from '../AssetList';
import { api } from '../../lib/api';
import type { Asset } from '../../types/api';

// Mock the API
jest.mock('../../lib/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('AssetList Component', () => {
  const mockAssets: Asset[] = [
    {
      id: 'TEST_AAPL',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 150.00,
      market_cap: 2.4e12,
      currency: 'USD',
      additional_fields: {},
    },
    {
      id: 'TEST_MSFT',
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 300.00,
      market_cap: 2.2e12,
      currency: 'USD',
      additional_fields: {},
    },
    {
      id: 'TEST_BOND',
      symbol: 'AAPL_BOND',
      name: 'Apple Corporate Bond',
      asset_class: 'FIXED_INCOME',
      sector: 'Technology',
      price: 1000.00,
      market_cap: undefined,
      currency: 'USD',
      additional_fields: {},
    },
  ];

  const mockAssetClasses = {
    asset_classes: ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'CURRENCY'],
  };

  const mockSectors = {
    sectors: ['Technology', 'Finance', 'Healthcare', 'Energy'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedApi.getAssets.mockResolvedValue(mockAssets);
    mockedApi.getAssetClasses.mockResolvedValue(mockAssetClasses);
    mockedApi.getSectors.mockResolvedValue(mockSectors);
  });

  describe('Initial Rendering', () => {
    it('should render loading state initially', () => {
      render(<AssetList />);
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should load and display assets after loading', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
        expect(screen.getByText('MSFT')).toBeInTheDocument();
        expect(screen.getByText('AAPL_BOND')).toBeInTheDocument();
      });
    });

    it('should display asset names', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
        expect(screen.getByText('Microsoft Corporation')).toBeInTheDocument();
        expect(screen.getByText('Apple Corporate Bond')).toBeInTheDocument();
      });
    });

    it('should call API methods on mount', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalled();
        expect(mockedApi.getAssetClasses).toHaveBeenCalled();
        expect(mockedApi.getSectors).toHaveBeenCalled();
      });
    });
  });

  describe('Asset Display', () => {
    it('should display asset symbols correctly', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const symbols = ['AAPL', 'MSFT', 'AAPL_BOND'];
        symbols.forEach(symbol => {
          expect(screen.getByText(symbol)).toBeInTheDocument();
        });
      });
    });

    it('should display asset classes', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const equityElements = screen.getAllByText('EQUITY');
        expect(equityElements.length).toBeGreaterThan(0);
        expect(screen.getByText('FIXED_INCOME')).toBeInTheDocument();
      });
    });

    it('should display sectors', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const techElements = screen.getAllByText('Technology');
        expect(techElements.length).toBeGreaterThan(0);
      });
    });

    it('should format prices correctly', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText(/USD 150\.00/)).toBeInTheDocument();
        expect(screen.getByText(/USD 300\.00/)).toBeInTheDocument();
        expect(screen.getByText(/USD 1000\.00/)).toBeInTheDocument();
      });
    });

    it('should format market cap in billions', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText(/\$2400\.00B/)).toBeInTheDocument();
        expect(screen.getByText(/\$2200\.00B/)).toBeInTheDocument();
      });
    });

    it('should display N/A for undefined market cap', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const naElements = screen.getAllByText('N/A');
        expect(naElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Filter Functionality', () => {
    it('should render filter dropdowns', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Asset Class/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Sector/i)).toBeInTheDocument();
      });
    });

    it('should populate asset class dropdown', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const assetClassSelect = screen.getByLabelText(/Asset Class/i);
        expect(assetClassSelect).toBeInTheDocument();
        
        // Check for "All Classes" option
        expect(screen.getByText('All Classes')).toBeInTheDocument();
      });
    });

    it('should populate sector dropdown', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const sectorSelect = screen.getByLabelText(/Sector/i);
        expect(sectorSelect).toBeInTheDocument();
        
        // Check for "All Sectors" option
        expect(screen.getByText('All Sectors')).toBeInTheDocument();
      });
    });

    it('should filter assets by asset class', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const assetClassSelect = screen.getByLabelText(/Asset Class/i);
      fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledWith({ asset_class: 'EQUITY', sector: '' });
      });
    });

    it('should filter assets by sector', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const sectorSelect = screen.getByLabelText(/Sector/i);
      fireEvent.change(sectorSelect, { target: { value: 'Finance' } });

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledWith({ asset_class: '', sector: 'Finance' });
      });
    });

    it('should apply both filters simultaneously', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const assetClassSelect = screen.getByLabelText(/Asset Class/i);
      const sectorSelect = screen.getByLabelText(/Sector/i);

      fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });
      fireEvent.change(sectorSelect, { target: { value: 'Technology' } });

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledWith({
          asset_class: 'EQUITY',
          sector: 'Technology',
        });
      });
    });

    it('should reset to all assets when filter is cleared', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const assetClassSelect = screen.getByLabelText(/Asset Class/i);
      
      // Apply filter
      fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });
      
      // Clear filter
      fireEvent.change(assetClassSelect, { target: { value: '' } });

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledWith({ asset_class: '', sector: '' });
      });
    });
  });

  describe('Empty States', () => {
    it('should display "No assets found" when no data', async () => {
      mockedApi.getAssets.mockResolvedValue([]);
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('No assets found')).toBeInTheDocument();
      });
    });

    it('should handle empty asset classes', async () => {
      mockedApi.getAssetClasses.mockResolvedValue({ asset_classes: [] });
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('All Classes')).toBeInTheDocument();
      });
    });

    it('should handle empty sectors', async () => {
      mockedApi.getSectors.mockResolvedValue({ sectors: [] });
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('All Sectors')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockedApi.getAssets.mockRejectedValue(new Error('API Error'));
      
      render(<AssetList />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error loading assets:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it('should handle metadata loading errors', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockedApi.getAssetClasses.mockRejectedValue(new Error('Metadata Error'));
      
      render(<AssetList />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error loading metadata:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it('should still display assets if metadata fails', async () => {
      mockedApi.getAssetClasses.mockRejectedValue(new Error('Metadata Error'));
      mockedApi.getSectors.mockRejectedValue(new Error('Metadata Error'));
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });
    });
  });

  describe('Table Structure', () => {
    it('should render table headers', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('Symbol')).toBeInTheDocument();
        expect(screen.getByText('Name')).toBeInTheDocument();
        expect(screen.getByText('Class')).toBeInTheDocument();
        expect(screen.getByText('Sector')).toBeInTheDocument();
        expect(screen.getByText('Price')).toBeInTheDocument();
        expect(screen.getByText('Market Cap')).toBeInTheDocument();
      });
    });

    it('should render table rows for each asset', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const rows = screen.getAllByRole('row');
        // Header row + 3 asset rows
        expect(rows.length).toBe(4);
      });
    });

    it('should apply hover styles to rows', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const rows = screen.getAllByRole('row');
        const dataRows = rows.slice(1); // Skip header row
        
        dataRows.forEach(row => {
          expect(row).toHaveClass('hover:bg-gray-50');
        });
      });
    });
  });

  describe('Data Formatting Edge Cases', () => {
    it('should handle zero market cap', async () => {
      const assetsWithZeroMarketCap: Asset[] = [
        {
          ...mockAssets[0],
          market_cap: 0,
        },
      ];
      mockedApi.getAssets.mockResolvedValue(assetsWithZeroMarketCap);
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('$0.00B')).toBeInTheDocument();
      });
    });

    it('should handle very large market caps', async () => {
      const assetsWithLargeMarketCap: Asset[] = [
        {
          ...mockAssets[0],
          market_cap: 5.5e12,
        },
      ];
      mockedApi.getAssets.mockResolvedValue(assetsWithLargeMarketCap);
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('$5500.00B')).toBeInTheDocument();
      });
    });

    it('should handle small prices with correct precision', async () => {
      const assetsWithSmallPrice: Asset[] = [
        {
          ...mockAssets[0],
          price: 0.01,
        },
      ];
      mockedApi.getAssets.mockResolvedValue(assetsWithSmallPrice);
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText(/USD 0\.01/)).toBeInTheDocument();
      });
    });

    it('should handle different currencies', async () => {
      const assetsWithDifferentCurrency: Asset[] = [
        {
          ...mockAssets[0],
          currency: 'EUR',
        },
      ];
      mockedApi.getAssets.mockResolvedValue(assetsWithDifferentCurrency);
      
      render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText(/EUR 150\.00/)).toBeInTheDocument();
      });
    });
  });

  describe('Component Lifecycle', () => {
    it('should reload assets when filter changes', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledTimes(1);
      });

      const assetClassSelect = screen.getByLabelText(/Asset Class/i);
      fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });

      await waitFor(() => {
        expect(mockedApi.getAssets).toHaveBeenCalledTimes(2);
      });
    });

    it('should only load metadata once', async () => {
      render(<AssetList />);

      await waitFor(() => {
        expect(mockedApi.getAssetClasses).toHaveBeenCalledTimes(1);
        expect(mockedApi.getSectors).toHaveBeenCalledTimes(1);
      });

      // Change filter - metadata should not reload
      const assetClassSelect = screen.getByLabelText(/Asset Class/i);
      fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });

      await waitFor(() => {
        expect(mockedApi.getAssetClasses).toHaveBeenCalledTimes(1);
        expect(mockedApi.getSectors).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible form labels', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const assetClassLabel = screen.getByLabelText(/Asset Class/i);
        const sectorLabel = screen.getByLabelText(/Sector/i);
        
        expect(assetClassLabel).toBeInTheDocument();
        expect(sectorLabel).toBeInTheDocument();
      });
    });

    it('should have semantic table structure', async () => {
      render(<AssetList />);

      await waitFor(() => {
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
        
        const headers = screen.getAllByRole('columnheader');
        expect(headers.length).toBe(6);
      });
    });
  });

  describe('Performance', () => {
    it('should use useCallback for loadAssets', async () => {
      const { rerender } = render(<AssetList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const initialCallCount = mockedApi.getAssets.mock.calls.length;

      // Rerender without prop changes
      rerender(<AssetList />);

      // Should not trigger additional API calls
      expect(mockedApi.getAssets.mock.calls.length).toBe(initialCallCount);
    });
  });
});