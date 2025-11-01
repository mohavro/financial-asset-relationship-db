/**
 * Unit tests for API client library.
 * 
 * Tests cover:
 * - API client initialization
 * - All endpoint functions
 * - Error handling
 * - Request/response transformation
 */

import axios from 'axios';
import { api } from '../api';
import type { Asset, Relationship, Metrics, VisualizationData } from '../../types/api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  const mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);
  });

  describe('healthCheck', () => {
    it('should call health check endpoint', async () => {
      const mockResponse = { status: 'healthy', graph_initialized: true };
      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await api.healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/health');
      expect(result).toEqual(mockResponse);
    });

    it('should handle health check errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      await expect(api.healthCheck()).rejects.toThrow('Network error');
    });
  });

  describe('getAssets', () => {
    const mockAssets: Asset[] = [
      {
        id: 'TEST1',
        symbol: 'AAPL',
        name: 'Apple Inc.',
        asset_class: 'EQUITY',
        sector: 'Technology',
        price: 150.0,
        market_cap: 2.4e12,
        currency: 'USD',
        additional_fields: { pe_ratio: 25.5 },
      },
    ];

    it('should fetch all assets without filters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', { params: undefined });
      expect(result).toEqual(mockAssets);
    });

    it('should fetch assets with asset_class filter', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets({ asset_class: 'EQUITY' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY' },
      });
      expect(result).toEqual(mockAssets);
    });

    it('should fetch assets with sector filter', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      await api.getAssets({ sector: 'Technology' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { sector: 'Technology' },
      });
    });

    it('should fetch assets with multiple filters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      await api.getAssets({ asset_class: 'EQUITY', sector: 'Technology' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY', sector: 'Technology' },
      });
    });
  });

  describe('getAssetDetail', () => {
    const mockAsset: Asset = {
      id: 'TEST1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 150.0,
      market_cap: 2.4e12,
      currency: 'USD',
      additional_fields: {},
    };

    it('should fetch asset details', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      const result = await api.getAssetDetail('TEST1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/TEST1');
      expect(result).toEqual(mockAsset);
    });

    it('should handle not found errors', async () => {
      mockAxiosInstance.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Asset not found' } },
      });

      await expect(api.getAssetDetail('NONEXISTENT')).rejects.toThrow();
    });
  });

  describe('getAssetRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'TEST1',
        target_id: 'TEST2',
        relationship_type: 'same_sector',
        strength: 0.8,
      },
    ];

    it('should fetch asset relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAssetRelationships('TEST1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/TEST1/relationships');
      expect(result).toEqual(mockRelationships);
    });
  });

  describe('getAllRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'TEST1',
        target_id: 'TEST2',
        relationship_type: 'same_sector',
        strength: 0.8,
      },
    ];

    it('should fetch all relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAllRelationships();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/relationships');
      expect(result).toEqual(mockRelationships);
    });
  });

  describe('getMetrics', () => {
    const mockMetrics: Metrics = {
      total_assets: 10,
      total_relationships: 15,
      asset_classes: { EQUITY: 5, BOND: 3, COMMODITY: 2 },
      avg_degree: 3.0,
      max_degree: 5,
      network_density: 0.3,
    };

    it('should fetch metrics', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics });

      const result = await api.getMetrics();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/metrics');
      expect(result).toEqual(mockMetrics);
    });
  });

  describe('getVisualizationData', () => {
    const mockVizData: VisualizationData = {
      nodes: [
        {
          id: 'TEST1',
          name: 'Apple Inc.',
          symbol: 'AAPL',
          asset_class: 'EQUITY',
          x: 1.0,
          y: 2.0,
          z: 3.0,
          color: '#1f77b4',
          size: 10,
        },
      ],
      edges: [
        {
          source: 'TEST1',
          target: 'TEST2',
          relationship_type: 'same_sector',
          strength: 0.8,
        },
      ],
    };

    it('should fetch visualization data', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/visualization');
      expect(result).toEqual(mockVizData);
    });
  });

  describe('getAssetClasses', () => {
    it('should fetch available asset classes', async () => {
      const mockData = { asset_classes: ['EQUITY', 'BOND', 'COMMODITY', 'CURRENCY'] };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getAssetClasses();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/asset-classes');
      expect(result).toEqual(mockData);
    });
  });

  describe('getSectors', () => {
    it('should fetch available sectors', async () => {
      const mockData = { sectors: ['Technology', 'Energy', 'Finance'] };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getSectors();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/sectors');
      expect(result).toEqual(mockData);
    });
  });
});