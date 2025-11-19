/**
 * Comprehensive tests for test-utils.ts
 * 
 * This test suite validates all mock data objects used across the frontend test suite,
 * ensuring they conform to the expected TypeScript interfaces and contain valid data.
 */

import {
  mockAssets,
  mockAsset,
  mockAssetClasses,
  mockSectors,
  mockRelationships,
  mockAllRelationships,
  mockMetrics,
  mockVisualizationData,
  mockVizData,
} from './test-utils';
import type { Asset, Relationship, Metrics, VisualizationData } from '../app/types/api';

describe('test-utils Mock Data Validation', () => {
  describe('mockAssets', () => {
    it('should be an array', () => {
      expect(Array.isArray(mockAssets)).toBe(true);
    });

    it('should contain at least one asset', () => {
      expect(mockAssets.length).toBeGreaterThan(0);
    });

    it('should have all required Asset properties', () => {
      mockAssets.forEach((asset, index) => {
        expect(asset).toHaveProperty('id');
        expect(asset).toHaveProperty('symbol');
        expect(asset).toHaveProperty('name');
        expect(asset).toHaveProperty('asset_class');
        expect(asset).toHaveProperty('sector');
        expect(asset).toHaveProperty('price');
        expect(asset).toHaveProperty('currency');
        expect(asset).toHaveProperty('additional_fields');
      });
    });

    it('should have valid string properties', () => {
      mockAssets.forEach((asset) => {
        expect(typeof asset.id).toBe('string');
        expect(asset.id).toBeTruthy();
        expect(typeof asset.symbol).toBe('string');
        expect(asset.symbol).toBeTruthy();
        expect(typeof asset.name).toBe('string');
        expect(asset.name).toBeTruthy();
        expect(typeof asset.asset_class).toBe('string');
        expect(asset.asset_class).toBeTruthy();
        expect(typeof asset.sector).toBe('string');
        expect(asset.sector).toBeTruthy();
        expect(typeof asset.currency).toBe('string');
        expect(asset.currency).toBeTruthy();
      });
    });

    it('should have valid numeric properties', () => {
      mockAssets.forEach((asset) => {
        expect(typeof asset.price).toBe('number');
        expect(asset.price).toBeGreaterThan(0);
        if (asset.market_cap !== undefined) {
          expect(typeof asset.market_cap).toBe('number');
          expect(asset.market_cap).toBeGreaterThan(0);
        }
      });
    });

    it('should have additional_fields as an object', () => {
      mockAssets.forEach((asset) => {
        expect(typeof asset.additional_fields).toBe('object');
        expect(asset.additional_fields).not.toBeNull();
      });
    });

    it('should have unique IDs', () => {
      const ids = mockAssets.map((asset) => asset.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have unique symbols', () => {
      const symbols = mockAssets.map((asset) => asset.symbol);
      const uniqueSymbols = new Set(symbols);
      expect(uniqueSymbols.size).toBe(symbols.length);
    });

    it('should have valid currency codes', () => {
      mockAssets.forEach((asset) => {
        expect(asset.currency).toMatch(/^[A-Z]{3}$/);
      });
    });
  });

  describe('mockAsset', () => {
    it('should be an object with all required properties', () => {
      expect(typeof mockAsset).toBe('object');
      expect(mockAsset).toHaveProperty('id');
      expect(mockAsset).toHaveProperty('symbol');
      expect(mockAsset).toHaveProperty('name');
      expect(mockAsset).toHaveProperty('asset_class');
      expect(mockAsset).toHaveProperty('sector');
      expect(mockAsset).toHaveProperty('price');
      expect(mockAsset).toHaveProperty('currency');
      expect(mockAsset).toHaveProperty('additional_fields');
    });

    it('should have valid data types', () => {
      expect(typeof mockAsset.id).toBe('string');
      expect(typeof mockAsset.symbol).toBe('string');
      expect(typeof mockAsset.name).toBe('string');
      expect(typeof mockAsset.asset_class).toBe('string');
      expect(typeof mockAsset.sector).toBe('string');
      expect(typeof mockAsset.price).toBe('number');
      expect(typeof mockAsset.currency).toBe('string');
      expect(typeof mockAsset.additional_fields).toBe('object');
    });

    it('should have valid additional_fields with expected properties', () => {
      expect(mockAsset.additional_fields).toHaveProperty('pe_ratio');
      expect(mockAsset.additional_fields).toHaveProperty('dividend_yield');
      expect(typeof mockAsset.additional_fields.pe_ratio).toBe('number');
      expect(typeof mockAsset.additional_fields.dividend_yield).toBe('number');
    });

    it('should have positive numeric values', () => {
      expect(mockAsset.price).toBeGreaterThan(0);
      expect(mockAsset.market_cap).toBeGreaterThan(0);
      expect(mockAsset.additional_fields.pe_ratio).toBeGreaterThan(0);
      expect(mockAsset.additional_fields.dividend_yield).toBeGreaterThanOrEqual(0);
    });

    it('should match one of the assets in mockAssets', () => {
      const matchingAsset = mockAssets.find((a) => a.id === mockAsset.id);
      expect(matchingAsset).toBeDefined();
      expect(matchingAsset?.symbol).toBe(mockAsset.symbol);
    });
  });

  describe('mockAssetClasses', () => {
    it('should have asset_classes property', () => {
      expect(mockAssetClasses).toHaveProperty('asset_classes');
    });

    it('should have asset_classes as an array', () => {
      expect(Array.isArray(mockAssetClasses.asset_classes)).toBe(true);
    });

    it('should contain valid asset class values', () => {
      const validClasses = ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'CURRENCY', 'ALTERNATIVE', 'REAL_ESTATE'];
      mockAssetClasses.asset_classes.forEach((assetClass) => {
        expect(typeof assetClass).toBe('string');
        expect(validClasses).toContain(assetClass);
      });
    });

    it('should have unique asset classes', () => {
      const uniqueClasses = new Set(mockAssetClasses.asset_classes);
      expect(uniqueClasses.size).toBe(mockAssetClasses.asset_classes.length);
    });

    it('should contain at least one asset class', () => {
      expect(mockAssetClasses.asset_classes.length).toBeGreaterThan(0);
    });

    it('should have all uppercase asset class names', () => {
      mockAssetClasses.asset_classes.forEach((assetClass) => {
        expect(assetClass).toBe(assetClass.toUpperCase());
      });
    });
  });

  describe('mockSectors', () => {
    it('should have sectors property', () => {
      expect(mockSectors).toHaveProperty('sectors');
    });

    it('should have sectors as an array', () => {
      expect(Array.isArray(mockSectors.sectors)).toBe(true);
    });

    it('should contain string values', () => {
      mockSectors.sectors.forEach((sector) => {
        expect(typeof sector).toBe('string');
        expect(sector).toBeTruthy();
      });
    });

    it('should have unique sectors', () => {
      const uniqueSectors = new Set(mockSectors.sectors);
      expect(uniqueSectors.size).toBe(mockSectors.sectors.length);
    });

    it('should contain at least one sector', () => {
      expect(mockSectors.sectors.length).toBeGreaterThan(0);
    });

    it('should have properly capitalized sector names', () => {
      mockSectors.sectors.forEach((sector) => {
        expect(sector[0]).toBe(sector[0].toUpperCase());
      });
    });
  });

  describe('mockRelationships', () => {
    it('should be an array', () => {
      expect(Array.isArray(mockRelationships)).toBe(true);
    });

    it('should contain at least one relationship', () => {
      expect(mockRelationships.length).toBeGreaterThan(0);
    });

    it('should have all required Relationship properties', () => {
      mockRelationships.forEach((rel) => {
        expect(rel).toHaveProperty('source_id');
        expect(rel).toHaveProperty('target_id');
        expect(rel).toHaveProperty('relationship_type');
        expect(rel).toHaveProperty('strength');
      });
    });

    it('should have valid string properties', () => {
      mockRelationships.forEach((rel) => {
        expect(typeof rel.source_id).toBe('string');
        expect(rel.source_id).toBeTruthy();
        expect(typeof rel.target_id).toBe('string');
        expect(rel.target_id).toBeTruthy();
        expect(typeof rel.relationship_type).toBe('string');
        expect(rel.relationship_type).toBeTruthy();
      });
    });

    it('should have valid strength values', () => {
      mockRelationships.forEach((rel) => {
        expect(typeof rel.strength).toBe('number');
        expect(rel.strength).toBeGreaterThan(0);
        expect(rel.strength).toBeLessThanOrEqual(1);
      });
    });

    it('should have different source and target IDs', () => {
      mockRelationships.forEach((rel) => {
        expect(rel.source_id).not.toBe(rel.target_id);
      });
    });

    it('should reference valid asset IDs from mockAssets', () => {
      const assetIds = mockAssets.map((a) => a.id);
      mockRelationships.forEach((rel) => {
        // At least one ID should be in mockAssets (some may reference ASSET_3, etc.)
        const sourceValid = assetIds.includes(rel.source_id) || rel.source_id.startsWith('ASSET_');
        const targetValid = assetIds.includes(rel.target_id) || rel.target_id.startsWith('ASSET_');
        expect(sourceValid).toBe(true);
        expect(targetValid).toBe(true);
      });
    });
  });

  describe('mockAllRelationships', () => {
    it('should be an array', () => {
      expect(Array.isArray(mockAllRelationships)).toBe(true);
    });

    it('should contain at least one relationship', () => {
      expect(mockAllRelationships.length).toBeGreaterThan(0);
    });

    it('should have all required Relationship properties', () => {
      mockAllRelationships.forEach((rel) => {
        expect(rel).toHaveProperty('source_id');
        expect(rel).toHaveProperty('target_id');
        expect(rel).toHaveProperty('relationship_type');
        expect(rel).toHaveProperty('strength');
      });
    });

    it('should have valid data types', () => {
      mockAllRelationships.forEach((rel) => {
        expect(typeof rel.source_id).toBe('string');
        expect(typeof rel.target_id).toBe('string');
        expect(typeof rel.relationship_type).toBe('string');
        expect(typeof rel.strength).toBe('number');
      });
    });

    it('should be different from mockRelationships', () => {
      expect(mockAllRelationships).not.toEqual(mockRelationships);
    });

    it('should have valid strength values between 0 and 1', () => {
      mockAllRelationships.forEach((rel) => {
        expect(rel.strength).toBeGreaterThan(0);
        expect(rel.strength).toBeLessThanOrEqual(1);
      });
    });
  });

  describe('mockMetrics', () => {
    it('should have all required Metrics properties', () => {
      expect(mockMetrics).toHaveProperty('total_assets');
      expect(mockMetrics).toHaveProperty('total_relationships');
      expect(mockMetrics).toHaveProperty('asset_classes');
      expect(mockMetrics).toHaveProperty('avg_degree');
      expect(mockMetrics).toHaveProperty('max_degree');
      expect(mockMetrics).toHaveProperty('network_density');
    });

    it('should have valid numeric properties', () => {
      expect(typeof mockMetrics.total_assets).toBe('number');
      expect(typeof mockMetrics.total_relationships).toBe('number');
      expect(typeof mockMetrics.avg_degree).toBe('number');
      expect(typeof mockMetrics.max_degree).toBe('number');
      expect(typeof mockMetrics.network_density).toBe('number');
    });

    it('should have positive counts', () => {
      expect(mockMetrics.total_assets).toBeGreaterThan(0);
      expect(mockMetrics.total_relationships).toBeGreaterThan(0);
    });

    it('should have valid network metrics', () => {
      expect(mockMetrics.avg_degree).toBeGreaterThan(0);
      expect(mockMetrics.max_degree).toBeGreaterThanOrEqual(mockMetrics.avg_degree);
      expect(mockMetrics.network_density).toBeGreaterThan(0);
      expect(mockMetrics.network_density).toBeLessThanOrEqual(1);
    });

    it('should have asset_classes as an object', () => {
      expect(typeof mockMetrics.asset_classes).toBe('object');
      expect(mockMetrics.asset_classes).not.toBeNull();
    });

    it('should have valid asset class counts', () => {
      Object.entries(mockMetrics.asset_classes).forEach(([key, value]) => {
        expect(typeof key).toBe('string');
        expect(typeof value).toBe('number');
        expect(value).toBeGreaterThan(0);
      });
    });

    it('should have asset class counts sum less than or equal to total assets', () => {
      const sum = Object.values(mockMetrics.asset_classes).reduce((a, b) => a + b, 0);
      expect(sum).toBeLessThanOrEqual(mockMetrics.total_assets);
    });

    it('should have realistic metric values', () => {
      expect(mockMetrics.avg_degree).toBeGreaterThan(0);
      expect(mockMetrics.avg_degree).toBeLessThan(mockMetrics.total_assets);
      expect(mockMetrics.max_degree).toBeLessThan(mockMetrics.total_assets);
    });
  });

  describe('mockVisualizationData', () => {
    it('should have nodes and edges properties', () => {
      expect(mockVisualizationData).toHaveProperty('nodes');
      expect(mockVisualizationData).toHaveProperty('edges');
    });

    it('should have nodes as an array', () => {
      expect(Array.isArray(mockVisualizationData.nodes)).toBe(true);
    });

    it('should have edges as an array', () => {
      expect(Array.isArray(mockVisualizationData.edges)).toBe(true);
    });

    it('should contain at least one node', () => {
      expect(mockVisualizationData.nodes.length).toBeGreaterThan(0);
    });

    it('should have nodes with all required properties', () => {
      mockVisualizationData.nodes.forEach((node) => {
        expect(node).toHaveProperty('id');
        expect(node).toHaveProperty('name');
        expect(node).toHaveProperty('symbol');
        expect(node).toHaveProperty('asset_class');
        expect(node).toHaveProperty('x');
        expect(node).toHaveProperty('y');
        expect(node).toHaveProperty('z');
        expect(node).toHaveProperty('color');
        expect(node).toHaveProperty('size');
      });
    });

    it('should have nodes with valid data types', () => {
      mockVisualizationData.nodes.forEach((node) => {
        expect(typeof node.id).toBe('string');
        expect(typeof node.name).toBe('string');
        expect(typeof node.symbol).toBe('string');
        expect(typeof node.asset_class).toBe('string');
        expect(typeof node.x).toBe('number');
        expect(typeof node.y).toBe('number');
        expect(typeof node.z).toBe('number');
        expect(typeof node.color).toBe('string');
        expect(typeof node.size).toBe('number');
      });
    });

    it('should have nodes with valid color hex codes', () => {
      mockVisualizationData.nodes.forEach((node) => {
        expect(node.color).toMatch(/^#[0-9a-fA-F]{6}$/);
      });
    });

    it('should have nodes with positive size values', () => {
      mockVisualizationData.nodes.forEach((node) => {
        expect(node.size).toBeGreaterThan(0);
      });
    });

    it('should have unique node IDs', () => {
      const ids = mockVisualizationData.nodes.map((n) => n.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have edges with all required properties', () => {
      mockVisualizationData.edges.forEach((edge) => {
        expect(edge).toHaveProperty('source');
        expect(edge).toHaveProperty('target');
        expect(edge).toHaveProperty('relationship_type');
        expect(edge).toHaveProperty('strength');
      });
    });

    it('should have edges with valid data types', () => {
      mockVisualizationData.edges.forEach((edge) => {
        expect(typeof edge.source).toBe('string');
        expect(typeof edge.target).toBe('string');
        expect(typeof edge.relationship_type).toBe('string');
        expect(typeof edge.strength).toBe('number');
      });
    });

    it('should have edges with valid strength values', () => {
      mockVisualizationData.edges.forEach((edge) => {
        expect(edge.strength).toBeGreaterThan(0);
        expect(edge.strength).toBeLessThanOrEqual(1);
      });
    });

    it('should have edges referencing existing nodes', () => {
      const nodeIds = mockVisualizationData.nodes.map((n) => n.id);
      mockVisualizationData.edges.forEach((edge) => {
        expect(nodeIds).toContain(edge.source);
        expect(nodeIds).toContain(edge.target);
      });
    });

    it('should have edges with different source and target', () => {
      mockVisualizationData.edges.forEach((edge) => {
        expect(edge.source).not.toBe(edge.target);
      });
    });
  });

  describe('mockVizData', () => {
    it('should have nodes and edges properties', () => {
      expect(mockVizData).toHaveProperty('nodes');
      expect(mockVizData).toHaveProperty('edges');
    });

    it('should be different from mockVisualizationData', () => {
      expect(mockVizData).not.toEqual(mockVisualizationData);
    });

    it('should have valid node structure', () => {
      mockVizData.nodes.forEach((node) => {
        expect(typeof node.id).toBe('string');
        expect(typeof node.name).toBe('string');
        expect(typeof node.symbol).toBe('string');
        expect(typeof node.asset_class).toBe('string');
        expect(typeof node.x).toBe('number');
        expect(typeof node.y).toBe('number');
        expect(typeof node.z).toBe('number');
        expect(typeof node.color).toBe('string');
        expect(typeof node.size).toBe('number');
      });
    });

    it('should have valid edge structure', () => {
      mockVizData.edges.forEach((edge) => {
        expect(typeof edge.source).toBe('string');
        expect(typeof edge.target).toBe('string');
        expect(typeof edge.relationship_type).toBe('string');
        expect(typeof edge.strength).toBe('number');
      });
    });

    it('should have edges referencing existing nodes', () => {
      const nodeIds = mockVizData.nodes.map((n) => n.id);
      mockVizData.edges.forEach((edge) => {
        expect(nodeIds).toContain(edge.source);
        expect(nodeIds).toContain(edge.target);
      });
    });

    it('should contain at least 2 nodes', () => {
      expect(mockVizData.nodes.length).toBeGreaterThanOrEqual(2);
    });

    it('should have nodes with different asset classes', () => {
      const assetClasses = mockVizData.nodes.map((n) => n.asset_class);
      const uniqueClasses = new Set(assetClasses);
      expect(uniqueClasses.size).toBeGreaterThan(1);
    });
  });

  describe('Mock Data Consistency', () => {
    it('should have consistent asset IDs across mock objects', () => {
      const assetIds = mockAssets.map((a) => a.id);
      expect(assetIds).toContain(mockAsset.id);
    });

    it('should have relationship types that are uppercase with underscores', () => {
      [...mockRelationships, ...mockAllRelationships].forEach((rel) => {
        expect(rel.relationship_type).toMatch(/^[A-Z_]+$/);
      });
    });

    it('should have visualization nodes matching assets', () => {
      const vizNodeIds = mockVisualizationData.nodes.map((n) => n.id);
      const assetIds = mockAssets.map((a) => a.id);
      vizNodeIds.forEach((id) => {
        expect(assetIds).toContain(id);
      });
    });

    it('should have consistent data types across all mocks', () => {
      // All asset IDs should follow the same pattern
      const allAssetIds = [
        ...mockAssets.map((a) => a.id),
        mockAsset.id,
        ...mockVisualizationData.nodes.map((n) => n.id),
        ...mockVizData.nodes.map((n) => n.id),
      ];
      allAssetIds.forEach((id) => {
        expect(id).toMatch(/^ASSET_\d+$/);
      });
    });
  });

  describe('Edge Cases and Boundaries', () => {
    it('should handle empty additional_fields gracefully', () => {
      const emptyFieldAsset = mockAssets.find((a) => Object.keys(a.additional_fields).length === 0);
      if (emptyFieldAsset) {
        expect(emptyFieldAsset.additional_fields).toEqual({});
      }
    });

    it('should have realistic financial values', () => {
      mockAssets.forEach((asset) => {
        if (asset.market_cap) {
          expect(asset.market_cap).toBeGreaterThan(1000000); // At least 1M
          expect(asset.market_cap).toBeLessThan(10000000000000); // Less than 10T
        }
        expect(asset.price).toBeGreaterThan(0);
        expect(asset.price).toBeLessThan(1000000); // Reasonable stock price
      });
    });

    it('should have network density within valid range', () => {
      expect(mockMetrics.network_density).toBeGreaterThanOrEqual(0);
      expect(mockMetrics.network_density).toBeLessThanOrEqual(1);
    });

    it('should have reasonable coordinate ranges for visualization', () => {
      [...mockVisualizationData.nodes, ...mockVizData.nodes].forEach((node) => {
        expect(Math.abs(node.x)).toBeLessThan(100);
        expect(Math.abs(node.y)).toBeLessThan(100);
        expect(Math.abs(node.z)).toBeLessThan(100);
      });
    });

    it('should have all required sectors in mockSectors', () => {
      expect(mockSectors.sectors.length).toBeGreaterThanOrEqual(3);
    });

    it('should have all required asset classes in mockAssetClasses', () => {
      expect(mockAssetClasses.asset_classes.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Type Conformance', () => {
    it('mockAssets should conform to Asset[]', () => {
      const assets: Asset[] = mockAssets;
      expect(assets).toBeDefined();
    });

    it('mockAsset should conform to Asset', () => {
      const asset: Asset = mockAsset;
      expect(asset).toBeDefined();
    });

    it('mockRelationships should conform to Relationship[]', () => {
      const relationships: Relationship[] = mockRelationships;
      expect(relationships).toBeDefined();
    });

    it('mockMetrics should conform to Metrics', () => {
      const metrics: Metrics = mockMetrics;
      expect(metrics).toBeDefined();
    });

    it('mockVisualizationData should conform to VisualizationData', () => {
      const vizData: VisualizationData = mockVisualizationData;
      expect(vizData).toBeDefined();
    });
  });
});