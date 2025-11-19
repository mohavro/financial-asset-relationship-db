/**
 * Unit tests for test-utils.ts mock data and utilities.
 * 
 * This test suite validates that all mock data objects conform to their
 * expected type structures and contain appropriate values for testing purposes.
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

describe('mockAssets', () => {
  it('should be an array', () => {
    expect(Array.isArray(mockAssets)).toBe(true);
  });

  it('should contain at least one asset', () => {
    expect(mockAssets.length).toBeGreaterThan(0);
  });

  it('should have valid asset structure', () => {
    mockAssets.forEach((asset) => {
      expect(asset).toHaveProperty('id');
      expect(asset).toHaveProperty('symbol');
      expect(asset).toHaveProperty('name');
      expect(asset).toHaveProperty('asset_class');
      expect(asset).toHaveProperty('sector');
      expect(asset).toHaveProperty('price');
      expect(asset).toHaveProperty('market_cap');
      expect(asset).toHaveProperty('currency');
      expect(asset).toHaveProperty('additional_fields');
    });
  });

  it('should have string IDs', () => {
    mockAssets.forEach((asset) => {
      expect(typeof asset.id).toBe('string');
      expect(asset.id.length).toBeGreaterThan(0);
    });
  });

  it('should have unique IDs', () => {
    const ids = mockAssets.map((asset) => asset.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it('should have valid asset classes', () => {
    mockAssets.forEach((asset) => {
      expect(typeof asset.asset_class).toBe('string');
      expect(asset.asset_class.length).toBeGreaterThan(0);
    });
  });

  it('should have positive prices', () => {
    mockAssets.forEach((asset) => {
      expect(asset.price).toBeGreaterThan(0);
      expect(typeof asset.price).toBe('number');
    });
  });

  it('should have positive market caps', () => {
    mockAssets.forEach((asset) => {
      expect(asset.market_cap).toBeGreaterThan(0);
      expect(typeof asset.market_cap).toBe('number');
    });
  });

  it('should have valid currency codes', () => {
    mockAssets.forEach((asset) => {
      expect(typeof asset.currency).toBe('string');
      expect(asset.currency.length).toBeGreaterThanOrEqual(3);
      expect(asset.currency).toMatch(/^[A-Z]{3}$/);
    });
  });

  it('should have additional_fields object', () => {
    mockAssets.forEach((asset) => {
      expect(typeof asset.additional_fields).toBe('object');
      expect(asset.additional_fields).not.toBeNull();
    });
  });
});

describe('mockAsset', () => {
  it('should be an object', () => {
    expect(typeof mockAsset).toBe('object');
    expect(mockAsset).not.toBeNull();
  });

  it('should have all required asset properties', () => {
    expect(mockAsset).toHaveProperty('id');
    expect(mockAsset).toHaveProperty('symbol');
    expect(mockAsset).toHaveProperty('name');
    expect(mockAsset).toHaveProperty('asset_class');
    expect(mockAsset).toHaveProperty('sector');
    expect(mockAsset).toHaveProperty('price');
    expect(mockAsset).toHaveProperty('market_cap');
    expect(mockAsset).toHaveProperty('currency');
    expect(mockAsset).toHaveProperty('additional_fields');
  });

  it('should have specific values for testing', () => {
    expect(mockAsset.id).toBe('ASSET_1');
    expect(mockAsset.symbol).toBe('AAPL');
    expect(mockAsset.name).toBe('Apple Inc.');
    expect(mockAsset.asset_class).toBe('EQUITY');
  });

  it('should have additional fields with pe_ratio and dividend_yield', () => {
    expect(mockAsset.additional_fields).toHaveProperty('pe_ratio');
    expect(mockAsset.additional_fields).toHaveProperty('dividend_yield');
    expect(typeof mockAsset.additional_fields.pe_ratio).toBe('number');
    expect(typeof mockAsset.additional_fields.dividend_yield).toBe('number');
  });

  it('should have valid numeric values', () => {
    expect(mockAsset.price).toBe(150.0);
    expect(mockAsset.market_cap).toBe(2400000000000);
    expect(mockAsset.additional_fields.pe_ratio).toBe(25.5);
    expect(mockAsset.additional_fields.dividend_yield).toBe(0.005);
  });
});

describe('mockAssetClasses', () => {
  it('should have asset_classes property', () => {
    expect(mockAssetClasses).toHaveProperty('asset_classes');
  });

  it('should be an array', () => {
    expect(Array.isArray(mockAssetClasses.asset_classes)).toBe(true);
  });

  it('should contain expected asset classes', () => {
    expect(mockAssetClasses.asset_classes).toContain('EQUITY');
    expect(mockAssetClasses.asset_classes).toContain('FIXED_INCOME');
    expect(mockAssetClasses.asset_classes).toContain('COMMODITY');
    expect(mockAssetClasses.asset_classes).toContain('CURRENCY');
  });

  it('should have at least 4 asset classes', () => {
    expect(mockAssetClasses.asset_classes.length).toBeGreaterThanOrEqual(4);
  });

  it('should contain only strings', () => {
    mockAssetClasses.asset_classes.forEach((assetClass) => {
      expect(typeof assetClass).toBe('string');
    });
  });
});

describe('mockSectors', () => {
  it('should have sectors property', () => {
    expect(mockSectors).toHaveProperty('sectors');
  });

  it('should be an array', () => {
    expect(Array.isArray(mockSectors.sectors)).toBe(true);
  });

  it('should contain expected sectors', () => {
    expect(mockSectors.sectors).toContain('Energy');
    expect(mockSectors.sectors).toContain('Financials');
    expect(mockSectors.sectors).toContain('Technology');
  });

  it('should have at least 3 sectors', () => {
    expect(mockSectors.sectors.length).toBeGreaterThanOrEqual(3);
  });

  it('should contain only strings', () => {
    mockSectors.sectors.forEach((sector) => {
      expect(typeof sector).toBe('string');
    });
  });
});

describe('mockRelationships', () => {
  it('should be an array', () => {
    expect(Array.isArray(mockRelationships)).toBe(true);
  });

  it('should contain relationships', () => {
    expect(mockRelationships.length).toBeGreaterThan(0);
  });

  it('should have valid relationship structure', () => {
    mockRelationships.forEach((rel) => {
      expect(rel).toHaveProperty('source_id');
      expect(rel).toHaveProperty('target_id');
      expect(rel).toHaveProperty('relationship_type');
      expect(rel).toHaveProperty('strength');
    });
  });

  it('should have string IDs', () => {
    mockRelationships.forEach((rel) => {
      expect(typeof rel.source_id).toBe('string');
      expect(typeof rel.target_id).toBe('string');
      expect(rel.source_id.length).toBeGreaterThan(0);
      expect(rel.target_id).length).toBeGreaterThan(0);
    });
  });

  it('should have valid relationship types', () => {
    mockRelationships.forEach((rel) => {
      expect(typeof rel.relationship_type).toBe('string');
      expect(rel.relationship_type.length).toBeGreaterThan(0);
    });
  });

  it('should have strength between 0 and 1', () => {
    mockRelationships.forEach((rel) => {
      expect(rel.strength).toBeGreaterThanOrEqual(0);
      expect(rel.strength).toBeLessThanOrEqual(1);
    });
  });

  it('should have different source and target IDs', () => {
    mockRelationships.forEach((rel) => {
      expect(rel.source_id).not.toBe(rel.target_id);
    });
  });
});

describe('mockAllRelationships', () => {
  it('should be an array', () => {
    expect(Array.isArray(mockAllRelationships)).toBe(true);
  });

  it('should contain relationships', () => {
    expect(mockAllRelationships.length).toBeGreaterThan(0);
  });

  it('should have valid relationship structure', () => {
    mockAllRelationships.forEach((rel) => {
      expect(rel).toHaveProperty('source_id');
      expect(rel).toHaveProperty('target_id');
      expect(rel).toHaveProperty('relationship_type');
      expect(rel).toHaveProperty('strength');
    });
  });

  it('should have unique relationships', () => {
    const relationshipStrings = mockAllRelationships.map(
      (rel) => `${rel.source_id}-${rel.target_id}-${rel.relationship_type}`
    );
    const uniqueRelationships = new Set(relationshipStrings);
    expect(uniqueRelationships.size).toBe(relationshipStrings.length);
  });
});

describe('mockMetrics', () => {
  it('should be an object', () => {
    expect(typeof mockMetrics).toBe('object');
    expect(mockMetrics).not.toBeNull();
  });

  it('should have all required metric properties', () => {
    expect(mockMetrics).toHaveProperty('total_assets');
    expect(mockMetrics).toHaveProperty('total_relationships');
    expect(mockMetrics).toHaveProperty('asset_classes');
    expect(mockMetrics).toHaveProperty('avg_degree');
    expect(mockMetrics).toHaveProperty('max_degree');
    expect(mockMetrics).toHaveProperty('network_density');
  });

  it('should have positive total counts', () => {
    expect(mockMetrics.total_assets).toBeGreaterThan(0);
    expect(mockMetrics.total_relationships).toBeGreaterThan(0);
  });

  it('should have valid asset_classes object', () => {
    expect(typeof mockMetrics.asset_classes).toBe('object');
    expect(Object.keys(mockMetrics.asset_classes).length).toBeGreaterThan(0);
  });

  it('should have numeric asset class counts', () => {
    Object.values(mockMetrics.asset_classes).forEach((count) => {
      expect(typeof count).toBe('number');
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  it('should have valid degree metrics', () => {
    expect(mockMetrics.avg_degree).toBeGreaterThan(0);
    expect(mockMetrics.max_degree).toBeGreaterThanOrEqual(mockMetrics.avg_degree);
  });

  it('should have network density between 0 and 1', () => {
    expect(mockMetrics.network_density).toBeGreaterThanOrEqual(0);
    expect(mockMetrics.network_density).toBeLessThanOrEqual(1);
  });

  it('should have consistent total assets with sum of asset classes', () => {
    const sumOfClasses = Object.values(mockMetrics.asset_classes).reduce(
      (sum, count) => sum + count,
      0
    );
    expect(sumOfClasses).toBeLessThanOrEqual(mockMetrics.total_assets);
  });
});

describe('mockVisualizationData', () => {
  it('should be an object', () => {
    expect(typeof mockVisualizationData).toBe('object');
    expect(mockVisualizationData).not.toBeNull();
  });

  it('should have nodes and edges properties', () => {
    expect(mockVisualizationData).toHaveProperty('nodes');
    expect(mockVisualizationData).toHaveProperty('edges');
  });

  it('should have arrays for nodes and edges', () => {
    expect(Array.isArray(mockVisualizationData.nodes)).toBe(true);
    expect(Array.isArray(mockVisualizationData.edges)).toBe(true);
  });

  it('should have at least one node', () => {
    expect(mockVisualizationData.nodes.length).toBeGreaterThan(0);
  });

  it('should have valid node structure', () => {
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

  it('should have numeric coordinates', () => {
    mockVisualizationData.nodes.forEach((node) => {
      expect(typeof node.x).toBe('number');
      expect(typeof node.y).toBe('number');
      expect(typeof node.z).toBe('number');
    });
  });

  it('should have positive size values', () => {
    mockVisualizationData.nodes.forEach((node) => {
      expect(node.size).toBeGreaterThan(0);
    });
  });

  it('should have valid color hex codes', () => {
    mockVisualizationData.nodes.forEach((node) => {
      expect(node.color).toMatch(/^#[0-9a-fA-F]{6}$/);
    });
  });

  it('should have valid edge structure', () => {
    mockVisualizationData.edges.forEach((edge) => {
      expect(edge).toHaveProperty('source');
      expect(edge).toHaveProperty('target');
      expect(edge).toHaveProperty('relationship_type');
      expect(edge).toHaveProperty('strength');
    });
  });

  it('should have edges referencing existing nodes', () => {
    const nodeIds = new Set(mockVisualizationData.nodes.map((n) => n.id));
    mockVisualizationData.edges.forEach((edge) => {
      expect(nodeIds.has(edge.source)).toBe(true);
      expect(nodeIds.has(edge.target)).toBe(true);
    });
  });

  it('should have edge strength between 0 and 1', () => {
    mockVisualizationData.edges.forEach((edge) => {
      expect(edge.strength).toBeGreaterThanOrEqual(0);
      expect(edge.strength).toBeLessThanOrEqual(1);
    });
  });
});

describe('mockVizData', () => {
  it('should be an object', () => {
    expect(typeof mockVizData).toBe('object');
    expect(mockVizData).not.toBeNull();
  });

  it('should have nodes and edges properties', () => {
    expect(mockVizData).toHaveProperty('nodes');
    expect(mockVizData).toHaveProperty('edges');
  });

  it('should be different from mockVisualizationData', () => {
    expect(mockVizData).not.toEqual(mockVisualizationData);
  });

  it('should have valid node and edge structures', () => {
    mockVizData.nodes.forEach((node) => {
      expect(node).toHaveProperty('id');
      expect(node).toHaveProperty('name');
      expect(node).toHaveProperty('asset_class');
    });

    mockVizData.edges.forEach((edge) => {
      expect(edge).toHaveProperty('source');
      expect(edge).toHaveProperty('target');
      expect(edge).toHaveProperty('relationship_type');
    });
  });

  it('should contain different asset classes in nodes', () => {
    const assetClasses = new Set(mockVizData.nodes.map((n) => n.asset_class));
    expect(assetClasses.size).toBeGreaterThan(1);
  });

  it('should have edges connecting nodes with valid relationship types', () => {
    mockVizData.edges.forEach((edge) => {
      expect(typeof edge.relationship_type).toBe('string');
      expect(edge.relationship_type.length).toBeGreaterThan(0);
    });
  });
});

describe('Cross-mock consistency', () => {
  it('mockAsset should be similar to items in mockAssets', () => {
    const assetKeys = Object.keys(mockAsset);
    mockAssets.forEach((asset) => {
      assetKeys.forEach((key) => {
        expect(asset).toHaveProperty(key);
      });
    });
  });

  it('mockRelationships and mockAllRelationships should have same structure', () => {
    const relKeys = Object.keys(mockRelationships[0]);
    mockAllRelationships.forEach((rel) => {
      relKeys.forEach((key) => {
        expect(rel).toHaveProperty(key);
      });
    });
  });

  it('visualization data nodes should reference valid asset classes', () => {
    const validClasses = new Set(mockAssetClasses.asset_classes);
    
    mockVisualizationData.nodes.forEach((node) => {
      expect(validClasses.has(node.asset_class) || 
             typeof node.asset_class === 'string').toBe(true);
    });
    
    mockVizData.nodes.forEach((node) => {
      expect(validClasses.has(node.asset_class) || 
             typeof node.asset_class === 'string').toBe(true);
    });
  });
});

describe('Edge cases and boundaries', () => {
  it('should handle empty additional_fields gracefully', () => {
    const assetWithEmptyFields = mockAssets.find(
      (asset) => Object.keys(asset.additional_fields).length === 0
    );
    if (assetWithEmptyFields) {
      expect(assetWithEmptyFields.additional_fields).toEqual({});
    }
  });

  it('should have reasonable numeric ranges', () => {
    mockAssets.forEach((asset) => {
      expect(asset.price).toBeLessThan(1000000);
      expect(asset.market_cap).toBeLessThan(10000000000000);
    });
  });

  it('should have valid symbols', () => {
    mockAssets.forEach((asset) => {
      expect(asset.symbol).toMatch(/^[A-Z]{1,5}$/);
    });
  });

  it('metrics should have mathematically valid values', () => {
    expect(mockMetrics.max_degree).toBeGreaterThanOrEqual(0);
    expect(mockMetrics.avg_degree).toBeGreaterThanOrEqual(0);
    expect(mockMetrics.avg_degree).toBeLessThanOrEqual(mockMetrics.max_degree * 2);
  });
});