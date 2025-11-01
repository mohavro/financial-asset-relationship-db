/**
 * Comprehensive unit tests for the API client library.
 * 
 * Tests cover:
 * - All API endpoint methods
 * - Request parameter handling
 * - Response data validation
 * - Error handling and edge cases
 * - Axios configuration
 * - Type safety and return types
 */

import axios from 'axios';
import { api } from '../api';
import type { Asset, Relationship, Metrics, VisualizationData } from '../../types/api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  let mockAxiosInstance: any;

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Create mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    };
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance);
  });

  describe('Configuration', () => {
    it('should create axios instance with correct base URL from environment', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
      jest.isolateModules(() => {
        require('../api');
      });
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'https://api.example.com',
        })
      );
    });

    it('should use default base URL when environment variable is not set', () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      jest.isolateModules(() => {
        require('../api');
      });
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'http://localhost:8000',
        })
      );
    });

    it('should set correct headers', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });
  });

  describe('healthCheck', () => {
    it('should call health endpoint and return data', async () => {
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
        id: 'TEST_AAPL',
        symbol: 'AAPL',
        name: 'Apple Inc.',
        asset_class: 'EQUITY',
        sector: 'Technology',
        price: 150.00,
        market_cap: 2.4e12,
        currency: 'USD',
        additional_fields: { pe_ratio: 25.5 },
      },
      {
        id: 'TEST_BOND',
        symbol: 'AAPL_BOND',
        name: 'Apple Corporate Bond',
        asset_class: 'FIXED_INCOME',
        sector: 'Technology',
        price: 1000.00,
        currency: 'USD',
        additional_fields: { coupon_rate: 0.025 },
      },
    ];

    it('should fetch all assets without parameters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', { params: undefined });
      expect(result).toEqual(mockAssets);
      expect(result).toHaveLength(2);
    });

    it('should fetch assets filtered by asset class', async () => {
      const filteredAssets = mockAssets.filter(a => a.asset_class === 'EQUITY');
      mockAxiosInstance.get.mockResolvedValue({ data: filteredAssets });

      const result = await api.getAssets({ asset_class: 'EQUITY' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY' },
      });
      expect(result).toEqual(filteredAssets);
      expect(result).toHaveLength(1);
    });

    it('should fetch assets filtered by sector', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets({ sector: 'Technology' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { sector: 'Technology' },
      });
      expect(result).toEqual(mockAssets);
    });

    it('should fetch assets with both filters', async () => {
      const filteredAssets = [mockAssets[0]];
      mockAxiosInstance.get.mockResolvedValue({ data: filteredAssets });

      const result = await api.getAssets({
        asset_class: 'EQUITY',
        sector: 'Technology',
      });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY', sector: 'Technology' },
      });
      expect(result).toEqual(filteredAssets);
    });

    it('should return empty array when no assets match', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAssets({ sector: 'NonExistent' });

      expect(result).toEqual([]);
    });

    it('should handle errors when fetching assets', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('API Error'));

      await expect(api.getAssets()).rejects.toThrow('API Error');
    });
  });

  describe('getAssetDetail', () => {
    const mockAsset: Asset = {
      id: 'TEST_AAPL',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 150.00,
      market_cap: 2.4e12,
      currency: 'USD',
      additional_fields: {
        pe_ratio: 25.5,
        dividend_yield: 0.005,
        earnings_per_share: 5.89,
      },
    };

    it('should fetch asset detail by ID', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      const result = await api.getAssetDetail('TEST_AAPL');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/TEST_AAPL');
      expect(result).toEqual(mockAsset);
    });

    it('should handle asset not found', async () => {
      mockAxiosInstance.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Asset not found' } },
      });

      await expect(api.getAssetDetail('NONEXISTENT')).rejects.toMatchObject({
        response: expect.objectContaining({ status: 404 }),
      });
    });

    it('should handle special characters in asset ID', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      await api.getAssetDetail('TEST-ASSET_123');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/TEST-ASSET_123');
    });
  });

  describe('getAssetRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'TEST_AAPL',
        target_id: 'TEST_BOND',
        relationship_type: 'issues',
        strength: 0.9,
      },
      {
        source_id: 'TEST_AAPL',
        target_id: 'TEST_MSFT',
        relationship_type: 'competes_with',
        strength: 0.7,
      },
    ];

    it('should fetch relationships for an asset', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAssetRelationships('TEST_AAPL');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/TEST_AAPL/relationships');
      expect(result).toEqual(mockRelationships);
      expect(result).toHaveLength(2);
    });

    it('should return empty array for asset with no relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAssetRelationships('TEST_ISOLATED');

      expect(result).toEqual([]);
    });

    it('should handle errors when fetching relationships', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      await expect(api.getAssetRelationships('TEST_AAPL')).rejects.toThrow('Network error');
    });
  });

  describe('getAllRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'TEST_AAPL',
        target_id: 'TEST_BOND',
        relationship_type: 'issues',
        strength: 0.9,
      },
      {
        source_id: 'TEST_MSFT',
        target_id: 'TEST_BOND',
        relationship_type: 'issues',
        strength: 0.8,
      },
    ];

    it('should fetch all relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAllRelationships();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/relationships');
      expect(result).toEqual(mockRelationships);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no relationships exist', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAllRelationships();

      expect(result).toEqual([]);
    });
  });

  describe('getMetrics', () => {
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

    it('should fetch network metrics', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics });

      const result = await api.getMetrics();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/metrics');
      expect(result).toEqual(mockMetrics);
    });

    it('should return metrics with correct structure', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics });

      const result = await api.getMetrics();

      expect(result).toHaveProperty('total_assets');
      expect(result).toHaveProperty('total_relationships');
      expect(result).toHaveProperty('asset_classes');
      expect(result).toHaveProperty('avg_degree');
      expect(result).toHaveProperty('max_degree');
      expect(result).toHaveProperty('network_density');
      expect(typeof result.total_assets).toBe('number');
      expect(typeof result.asset_classes).toBe('object');
    });

    it('should handle metrics calculation errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Calculation failed'));

      await expect(api.getMetrics()).rejects.toThrow('Calculation failed');
    });
  });

  describe('getVisualizationData', () => {
    const mockVizData: VisualizationData = {
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
          id: 'TEST_BOND',
          name: 'Apple Bond',
          symbol: 'AAPL_BOND',
          asset_class: 'FIXED_INCOME',
          x: 1.5,
          y: 1.5,
          z: 1.5,
          color: '#ff7f0e',
          size: 8,
        },
      ],
      edges: [
        {
          source: 'TEST_AAPL',
          target: 'TEST_BOND',
          relationship_type: 'issues',
          strength: 0.9,
        },
      ],
    };

    it('should fetch visualization data', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/visualization');
      expect(result).toEqual(mockVizData);
    });

    it('should return data with nodes and edges', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(result.nodes).toHaveLength(2);
      expect(result.edges).toHaveLength(1);
      expect(result.nodes[0]).toHaveProperty('x');
      expect(result.nodes[0]).toHaveProperty('y');
      expect(result.nodes[0]).toHaveProperty('z');
    });

    it('should handle empty visualization data', async () => {
      mockAxiosInstance.get.mockResolvedValue({
        data: { nodes: [], edges: [] },
      });

      const result = await api.getVisualizationData();

      expect(result.nodes).toEqual([]);
      expect(result.edges).toEqual([]);
    });
  });

  describe('getAssetClasses', () => {
    it('should fetch asset classes', async () => {
      const mockData = {
        asset_classes: ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'CURRENCY'],
      };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getAssetClasses();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/asset-classes');
      expect(result).toEqual(mockData);
      expect(result.asset_classes).toHaveLength(4);
    });

    it('should return array of strings', async () => {
      const mockData = { asset_classes: ['EQUITY', 'BOND'] };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getAssetClasses();

      expect(Array.isArray(result.asset_classes)).toBe(true);
      result.asset_classes.forEach((ac) => {
        expect(typeof ac).toBe('string');
      });
    });
  });

  describe('getSectors', () => {
    it('should fetch sectors', async () => {
      const mockData = {
        sectors: ['Technology', 'Finance', 'Healthcare', 'Energy'],
      };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getSectors();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/sectors');
      expect(result).toEqual(mockData);
      expect(result.sectors).toHaveLength(4);
    });

    it('should return sorted sectors', async () => {
      const mockData = {
        sectors: ['Finance', 'Technology', 'Energy', 'Healthcare'],
      };
      mockAxiosInstance.get.mockResolvedValue({ data: mockData });

      const result = await api.getSectors();

      // The API should return sorted sectors
      const sorted = [...result.sectors].sort();
      expect(result.sectors).toEqual(sorted);
    });

    it('should handle empty sectors list', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: { sectors: [] } });

      const result = await api.getSectors();

      expect(result.sectors).toEqual([]);
    });
  });

  describe('Error Handling', () => {
    it('should propagate network errors', async () => {
      const networkError = new Error('Network Error');
      mockAxiosInstance.get.mockRejectedValue(networkError);

      await expect(api.getAssets()).rejects.toThrow('Network Error');
    });

    it('should propagate HTTP errors', async () => {
      const httpError = {
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      };
      mockAxiosInstance.get.mockRejectedValue(httpError);

      await expect(api.getMetrics()).rejects.toMatchObject(httpError);
    });

    it('should propagate timeout errors', async () => {
      const timeoutError = { code: 'ECONNABORTED', message: 'timeout exceeded' };
      mockAxiosInstance.get.mockRejectedValue(timeoutError);

      await expect(api.getVisualizationData()).rejects.toMatchObject(timeoutError);
    });
  });

  describe('Type Safety', () => {
    it('should maintain type safety for Asset responses', async () => {
      const mockAsset: Asset = {
        id: 'TEST',
        symbol: 'TEST',
        name: 'Test',
        asset_class: 'EQUITY',
        sector: 'Tech',
        price: 100,
        currency: 'USD',
        additional_fields: {},
      };
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      const result = await api.getAssetDetail('TEST');

      // TypeScript should enforce these properties exist
      expect(result.id).toBeDefined();
      expect(result.symbol).toBeDefined();
      expect(result.price).toBeDefined();
    });

    it('should maintain type safety for Metrics responses', async () => {
      const mockMetrics: Metrics = {
        total_assets: 10,
        total_relationships: 20,
        asset_classes: {},
        avg_degree: 2.0,
        max_degree: 5,
        network_density: 0.4,
      };
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics });

      const result = await api.getMetrics();

      // TypeScript should enforce numeric types
      expect(typeof result.total_assets).toBe('number');
      expect(typeof result.avg_degree).toBe('number');
      expect(typeof result.network_density).toBe('number');
    });
  });
});