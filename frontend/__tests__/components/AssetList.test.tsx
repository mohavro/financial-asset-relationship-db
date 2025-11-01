/**
 * Comprehensive unit tests for AssetList component.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AssetList from '../../app/components/AssetList';
import { api } from '../../app/lib/api';

jest.mock('../../app/lib/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('AssetList Component', () => {
  const mockAssets = [
    {
      id: 'ASSET_1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 150.0,
      market_cap: 2400000000000,
      currency: 'USD',
      additional_fields: {},
    },
  ];

  const mockAssetClasses = {
    asset_classes: ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'CURRENCY'],
  };

  const mockSectors = {
    sectors: ['Energy', 'Financials', 'Technology'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedApi.getAssets.mockResolvedValue(mockAssets);
    mockedApi.getAssetClasses.mockResolvedValue(mockAssetClasses);
    mockedApi.getSectors.mockResolvedValue(mockSectors);
  });

  it('should render filters section', async () => {
    render(<AssetList />);
    
    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });
  });

  it('should load and display assets', async () => {
    render(<AssetList />);
    
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    });
  });

  it('should filter by asset class', async () => {
    render(<AssetList />);
    
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const assetClassSelect = screen.getByLabelText(/Asset Class/i);
    fireEvent.change(assetClassSelect, { target: { value: 'EQUITY' } });

    await waitFor(() => {
      expect(mockedApi.getAssets).toHaveBeenCalledWith({ asset_class: 'EQUITY' });
    });
  });

  it('should display loading state', () => {
    render(<AssetList />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should handle empty assets', async () => {
    mockedApi.getAssets.mockResolvedValue([]);
    render(<AssetList />);
    
    await waitFor(() => {
      expect(screen.getByText('No assets found')).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    mockedApi.getAssets.mockRejectedValue(new Error('API Error'));

    render(<AssetList />);
    
    await waitFor(() => {
      expect(consoleError).toHaveBeenCalled();
    });

    consoleError.mockRestore();
  });
});