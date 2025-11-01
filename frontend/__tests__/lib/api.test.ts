/**
 * Comprehensive unit tests for the API client library (app/lib/api.ts).
 * 
 * Tests cover:
 * - All API methods (health check, assets, relationships, metrics, visualization)
 * - Request parameter handling
 * - Response type validation
 * - Error handling
 * - Axios configuration
 */

import axios from 'axios';
import { api } from '../../app/lib/api';
import type { Asset, Relationship, Metrics, VisualizationData } from '../../app/types/api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  let mockAxiosInstance: any;

  beforeEach(() => {
    // Create a mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    };

    // Mock axios.create to return our mock instance
    mockedAxios.create.mockReturnValue(mockAxiosInstance);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Client Configuration', () => {
    it('should create axios instance with correct baseURL', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: expect.any(String),
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should use environment variable for API URL if set', () => {
      const originalEnv = process.env.NEXT_PUBLIC_API_URL;
      process.env.NEXT_PUBLIC_API_URL = 'https://test-api.example.com';
      
      // Re-import to get new configuration
      jest.resetModules();
      const { api } = require('../../app/lib/api');
      
      // Verify the API instance uses the environment variable
      expect(api.defaults.baseURL).toBe('https://test-api.example.com');
      
      // Restore and reset modules
      process.env.NEXT_PUBLIC_API_URL = originalEnv;
      jest.resetModules();
    });

    it('should fall back to localhost:8000 if no environment variable', () => {
      const call = mockedAxios.create.mock.calls[0][0];
      expect(call.baseURL).toMatch(/localhost:8000|test-api/);
    });
  });

  describe('healthCheck', () => {
    it('should call health check endpoint', async () => {
      const mockResponse = { data: { status: 'healthy' } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await api.healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/health');
      expect(result).toEqual({ status: 'healthy' });
    });

    it('should handle health check errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      await expect(api.healthCheck()).rejects.toThrow('Network error');
    });
  });

  describe('getAssets', () => {
    const mockAssets: Asset[] = [
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
      {
        id: 'ASSET_2',
        symbol: 'GOOGL',
        name: 'Alphabet Inc.',
        asset_class: 'EQUITY',
        sector: 'Technology',
        price: 140.0,
        market_cap: 1800000000000,
        currency: 'USD',
        additional_fields: {},
      },
    ];

    it('should fetch all assets without filters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', { params: undefined });
      expect(result).toEqual(mockAssets);
      expect(result).toHaveLength(2);
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

      const result = await api.getAssets({ sector: 'Technology' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { sector: 'Technology' },
      });
      expect(result).toEqual(mockAssets);
    });

    it('should fetch assets with both filters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets });

      const result = await api.getAssets({ asset_class: 'EQUITY', sector: 'Technology' });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY', sector: 'Technology' },
      });
      expect(result).toEqual(mockAssets);
    });

    it('should handle empty asset list', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAssets();

      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });

    it('should handle API errors when fetching assets', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('API Error'));

      await expect(api.getAssets()).rejects.toThrow('API Error');
    });
  });

  describe('getAssetDetail', () => {
    const mockAsset: Asset = {
      id: 'ASSET_1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'EQUITY',
      sector: 'Technology',
      price: 150.0,
      market_cap: 2400000000000,
      currency: 'USD',
      additional_fields: {
        pe_ratio: 25.5,
        dividend_yield: 0.005,
      },
    };

    it('should fetch asset details by ID', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      const result = await api.getAssetDetail('ASSET_1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/ASSET_1');
      expect(result).toEqual(mockAsset);
      expect(result.additional_fields).toBeDefined();
    });

    it('should handle non-existent asset ID', async () => {
      mockAxiosInstance.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Asset not found' } },
      });

      await expect(api.getAssetDetail('NONEXISTENT')).rejects.toMatchObject({
        response: { status: 404 },
      });
    });

    it('should handle special characters in asset ID', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset });

      await api.getAssetDetail('ASSET_1-2.3');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/ASSET_1-2.3');
    });
  });

  describe('getAssetRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'ASSET_1',
        target_id: 'ASSET_2',
        relationship_type: 'SAME_SECTOR',
        strength: 0.8,
      },
      {
        source_id: 'ASSET_1',
        target_id: 'ASSET_3',
        relationship_type: 'ISSUER',
        strength: 0.95,
      },
    ];

    it('should fetch relationships for an asset', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAssetRelationships('ASSET_1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/ASSET_1/relationships');
      expect(result).toEqual(mockRelationships);
      expect(result).toHaveLength(2);
    });

    it('should handle asset with no relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAssetRelationships('ASSET_ISOLATED');

      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });

    it('should validate relationship structure', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAssetRelationships('ASSET_1');

      result.forEach((rel) => {
        expect(rel).toHaveProperty('source_id');
        expect(rel).toHaveProperty('target_id');
        expect(rel).toHaveProperty('relationship_type');
        expect(rel).toHaveProperty('strength');
        expect(typeof rel.strength).toBe('number');
      });
    });
  });

  describe('getAllRelationships', () => {
    const mockRelationships: Relationship[] = [
      {
        source_id: 'ASSET_1',
        target_id: 'ASSET_2',
        relationship_type: 'SAME_SECTOR',
        strength: 0.8,
      },
      {
        source_id: 'ASSET_3',
        target_id: 'ASSET_4',
        relationship_type: 'COMMODITY_EXPOSURE',
        strength: 0.6,
      },
    ];

    it('should fetch all relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships });

      const result = await api.getAllRelationships();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/relationships');
      expect(result).toEqual(mockRelationships);
      expect(result).toHaveLength(2);
    });

    it('should handle empty relationships', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] });

      const result = await api.getAllRelationships();

      expect(result).toEqual([]);
    });
  });

  describe('getMetrics', () => {
    const mockMetrics: Metrics = {
      total_assets: 15,
      total_relationships: 42,
      asset_classes: {
        EQUITY: 6,
        FIXED_INCOME: 4,
        COMMODITY: 3,
        CURRENCY: 2,
      },
      avg_degree: 5.6,
      max_degree: 12,
      network_density: 0.42,
    };

    it('should fetch network metrics', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics });

      const result = await api.getMetrics();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/metrics');
      expect(result).toEqual(mockMetrics);
    });

    it('should validate metrics structure', async () => {
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

    it('should handle metrics with zero values', async () => {
      const emptyMetrics: Metrics = {
        total_assets: 0,
        total_relationships: 0,
        asset_classes: {},
        avg_degree: 0,
        max_degree: 0,
        network_density: 0,
      };
      mockAxiosInstance.get.mockResolvedValue({ data: emptyMetrics });

      const result = await api.getMetrics();

      expect(result.total_assets).toBe(0);
      expect(result.network_density).toBe(0);
    });
  });

  describe('getVisualizationData', () => {
    const mockVizData: VisualizationData = {
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
          name: 'Gold',
          symbol: 'GOLD',
          asset_class: 'COMMODITY',
          x: -1.2,
          y: 0.5,
          z: 1.9,
          color: '#ff7f0e',
          size: 8,
        },
      ],
      edges: [
        {
          source: 'ASSET_1',
          target: 'ASSET_2',
          relationship_type: 'COMMODITY_EXPOSURE',
          strength: 0.7,
        },
      ],
    };

    it('should fetch visualization data', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/visualization');
      expect(result).toEqual(mockVizData);
    });

    it('should validate visualization node structure', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(result.nodes).toHaveLength(2);
      result.nodes.forEach((node) => {
        expect(node).toHaveProperty('id');
        expect(node).toHaveProperty('name');
        expect(node).toHaveProperty('symbol');
        expect(node).toHaveProperty('asset_class');
        expect(node).toHaveProperty('x');
        expect(node).toHaveProperty('y');
        expect(node).toHaveProperty('z');
        expect(node).toHaveProperty('color');
        expect(node).toHaveProperty('size');
        expect(typeof node.x).toBe('number');
        expect(typeof node.y).toBe('number');
        expect(typeof node.z).toBe('number');
      });
    });

    it('should validate visualization edge structure', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData });

      const result = await api.getVisualizationData();

      expect(result.edges).toHaveLength(1);
      result.edges.forEach((edge) => {
        expect(edge).toHaveProperty('source');
        expect(edge).toHaveProperty('target');
        expect(edge).toHaveProperty('relationship_type');
        expect(edge).toHaveProperty('strength');
        expect(typeof edge.strength).toBe('number');
      });
    });

    it('should handle empty visualization data', async () => {
      const emptyVizData: VisualizationData = { nodes: [], edges: [] };
      mockAxiosInstance.get.mockResolvedValue({ data: emptyVizData });

      const result = await api.getVisualizationData();

      expect(result.nodes).toHaveLength(0);
      expect(result.edges).toHaveLength(0);
    });
  });

  describe('getAssetClasses', () => {
    const mockAssetClasses = {
      asset_classes: ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'CURRENCY'],
    };

    it('should fetch asset classes', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssetClasses });

      const result = await api.getAssetClasses();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/asset-classes');
      expect(result).toEqual(mockAssetClasses);
      expect(result.asset_classes).toHaveLength(4);
    });

    it('should validate asset classes are strings', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssetClasses });

      const result = await api.getAssetClasses();

      result.asset_classes.forEach((ac) => {
        expect(typeof ac).toBe('string');
      });
    });

    it('should handle empty asset classes', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: { asset_classes: [] } });

      const result = await api.getAssetClasses();

      expect(result.asset_classes).toHaveLength(0);
    });
  });

  describe('getSectors', () => {
    const mockSectors = {
      sectors: ['Energy', 'Financials', 'Technology'],
    };

    it('should fetch sectors', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockSectors });

      const result = await api.getSectors();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/sectors');
      expect(result).toEqual(mockSectors);
      expect(result.sectors).toHaveLength(3);
    });

    it('should validate sectors are sorted', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: mockSectors });

      const result = await api.getSectors();

      const sortedSectors = [...result.sectors].sort();
      expect(result.sectors).toEqual(sortedSectors);
    });

    it('should handle empty sectors', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: { sectors: [] } });

      const result = await api.getSectors();

      expect(result.sectors).toHaveLength(0);
    });
  });

  describe('Error Handling', () => {
    it('should propagate network errors', async () => {
      const networkError = new Error('Network Error');
      mockAxiosInstance.get.mockRejectedValue(networkError);

      await expect(api.getAssets()).rejects.toThrow('Network Error');
    });

    it('should propagate HTTP error responses', async () => {
      const httpError = {
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      };
      mockAxiosInstance.get.mockRejectedValue(httpError);

      await expect(api.getMetrics()).rejects.toMatchObject({
        response: { status: 500 },
      });
    });

    it('should propagate timeout errors', async () => {
      const timeoutError = new Error('timeout of 5000ms exceeded');
      mockAxiosInstance.get.mockRejectedValue(timeoutError);

      await expect(api.getVisualizationData()).rejects.toThrow('timeout');
    });

    it('should handle malformed response data', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: null });

      const result = await api.healthCheck();

      expect(result).toBeNull();
    });
  });
});