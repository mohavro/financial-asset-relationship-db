/**
 * Unit tests for the API client library.
 * Tests all API methods, error handling, and configuration.
 */

import axios from 'axios'
import { api } from '../api'

// Mock axios
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client', () => {
  let mockAxiosInstance: any

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks()

    // Create a mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    }

    // Mock axios.create to return our mock instance
    mockedAxios.create = jest.fn(() => mockAxiosInstance)
  })

  describe('Configuration', () => {
    it('should create axios instance with correct base URL', () => {
      // Re-import to trigger initialization
      jest.isolateModules(() => {
        require('../api')
      })

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: expect.any(String),
          headers: {
            'Content-Type': 'application/json',
          },
        })
      )
    })

    it('should use environment variable for API URL', () => {
      const customUrl = 'https://api.example.com'
      process.env.NEXT_PUBLIC_API_URL = customUrl

      jest.isolateModules(() => {
        require('../api')
      })

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: customUrl,
        })
      )
    })
  })

  describe('healthCheck', () => {
    it('should call health endpoint and return data', async () => {
      const mockData = { status: 'healthy' }
      mockAxiosInstance.get.mockResolvedValue({ data: mockData })

      const result = await api.healthCheck()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/health')
      expect(result).toEqual(mockData)
    })

    it('should handle errors from health check', async () => {
      const error = new Error('Network error')
      mockAxiosInstance.get.mockRejectedValue(error)

      await expect(api.healthCheck()).rejects.toThrow('Network error')
    })
  })

  describe('getAssets', () => {
    it('should fetch all assets without params', async () => {
      const mockAssets = [
        { id: '1', symbol: 'AAPL', name: 'Apple Inc.' },
        { id: '2', symbol: 'MSFT', name: 'Microsoft' },
      ]
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets })

      const result = await api.getAssets()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', { params: undefined })
      expect(result).toEqual(mockAssets)
    })

    it('should fetch assets with asset_class filter', async () => {
      const mockAssets = [{ id: '1', symbol: 'AAPL', asset_class: 'EQUITY' }]
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets })

      const result = await api.getAssets({ asset_class: 'EQUITY' })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY' },
      })
      expect(result).toEqual(mockAssets)
    })

    it('should fetch assets with sector filter', async () => {
      const mockAssets = [{ id: '1', symbol: 'AAPL', sector: 'Technology' }]
      mockAxiosInstance.get.mockResolvedValue({ data: mockAssets })

      const result = await api.getAssets({ sector: 'Technology' })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { sector: 'Technology' },
      })
      expect(result).toEqual(mockAssets)
    })

    it('should fetch assets with multiple filters', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: [] })

      await api.getAssets({ asset_class: 'EQUITY', sector: 'Technology' })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets', {
        params: { asset_class: 'EQUITY', sector: 'Technology' },
      })
    })
  })

  describe('getAssetDetail', () => {
    it('should fetch asset detail by ID', async () => {
      const mockAsset = { id: 'AAPL', symbol: 'AAPL', name: 'Apple Inc.' }
      mockAxiosInstance.get.mockResolvedValue({ data: mockAsset })

      const result = await api.getAssetDetail('AAPL')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/AAPL')
      expect(result).toEqual(mockAsset)
    })

    it('should handle 404 for non-existent asset', async () => {
      const error = { response: { status: 404 } }
      mockAxiosInstance.get.mockRejectedValue(error)

      await expect(api.getAssetDetail('INVALID')).rejects.toEqual(error)
    })
  })

  describe('getAssetRelationships', () => {
    it('should fetch relationships for an asset', async () => {
      const mockRelationships = [
        { source_id: 'AAPL', target_id: 'MSFT', relationship_type: 'same_sector' },
      ]
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships })

      const result = await api.getAssetRelationships('AAPL')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/assets/AAPL/relationships')
      expect(result).toEqual(mockRelationships)
    })
  })

  describe('getAllRelationships', () => {
    it('should fetch all relationships', async () => {
      const mockRelationships = [
        { source_id: 'AAPL', target_id: 'MSFT', relationship_type: 'same_sector' },
      ]
      mockAxiosInstance.get.mockResolvedValue({ data: mockRelationships })

      const result = await api.getAllRelationships()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/relationships')
      expect(result).toEqual(mockRelationships)
    })
  })

  describe('getMetrics', () => {
    it('should fetch network metrics', async () => {
      const mockMetrics = {
        total_assets: 10,
        total_relationships: 20,
        asset_classes: { EQUITY: 5, BOND: 5 },
        avg_degree: 2.0,
        max_degree: 5,
        network_density: 0.4,
      }
      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics })

      const result = await api.getMetrics()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/metrics')
      expect(result).toEqual(mockMetrics)
    })
  })

  describe('getVisualizationData', () => {
    it('should fetch visualization data', async () => {
      const mockVizData = {
        nodes: [{ id: 'AAPL', x: 1, y: 2, z: 3 }],
        edges: [{ source: 'AAPL', target: 'MSFT' }],
      }
      mockAxiosInstance.get.mockResolvedValue({ data: mockVizData })

      const result = await api.getVisualizationData()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/visualization')
      expect(result).toEqual(mockVizData)
    })
  })

  describe('getAssetClasses', () => {
    it('should fetch available asset classes', async () => {
      const mockClasses = { asset_classes: ['EQUITY', 'BOND', 'COMMODITY', 'CURRENCY'] }
      mockAxiosInstance.get.mockResolvedValue({ data: mockClasses })

      const result = await api.getAssetClasses()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/asset-classes')
      expect(result).toEqual(mockClasses)
    })
  })

  describe('getSectors', () => {
    it('should fetch available sectors', async () => {
      const mockSectors = { sectors: ['Technology', 'Finance', 'Energy'] }
      mockAxiosInstance.get.mockResolvedValue({ data: mockSectors })

      const result = await api.getSectors()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/sectors')
      expect(result).toEqual(mockSectors)
    })
  })

  describe('Error Handling', () => {
    it('should propagate network errors', async () => {
      const networkError = new Error('Network Error')
      mockAxiosInstance.get.mockRejectedValue(networkError)

      await expect(api.getAssets()).rejects.toThrow('Network Error')
    })

    it('should propagate HTTP errors', async () => {
      const httpError = {
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      }
      mockAxiosInstance.get.mockRejectedValue(httpError)

      await expect(api.getMetrics()).rejects.toEqual(httpError)
    })
  })
})