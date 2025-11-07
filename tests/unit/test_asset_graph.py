"""Unit tests for AssetRelationshipGraph.

This module contains comprehensive unit tests for the asset relationship graph including:
- Graph initialization and asset management
- Relationship creation (directional and bidirectional)
- Automatic relationship discovery algorithms
- Relationship strength calculation and clamping
- Metric calculation (totals, averages, distributions, density)
- 3D visualization data generation with deterministic positioning
- Regulatory event integration and impact modeling
"""

import numpy as np

from src.logic.asset_graph import AssetRelationshipGraph
from src.models.financial_models import AssetClass, Bond, Equity


class TestAssetRelationshipGraph:
    """Test cases for the AssetRelationshipGraph class."""

    def test_empty_graph_initialization(self, empty_graph):
        """Test initializing an empty graph."""
        assert len(empty_graph.assets) == 0
        assert len(empty_graph.relationships) == 0
        assert len(empty_graph.regulatory_events) == 0

    def test_add_single_asset(self, empty_graph, sample_equity):
        """Test adding a single asset to the graph."""
        empty_graph.add_asset(sample_equity)
        assert len(empty_graph.assets) == 1
        assert "TEST_AAPL" in empty_graph.assets
        assert empty_graph.assets["TEST_AAPL"] == sample_equity

    def test_add_multiple_assets(self, populated_graph):
        """Test adding multiple assets to the graph."""
        assert len(populated_graph.assets) == 4
        assert "TEST_AAPL" in populated_graph.assets
        assert "TEST_BOND" in populated_graph.assets

    def test_add_relationship(self, populated_graph):
        """Test adding a relationship between two assets."""
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "test_relationship", 0.8)
        assert "TEST_AAPL" in populated_graph.relationships
        assert len(populated_graph.relationships["TEST_AAPL"]) > 0

        # Check that the relationship was added
        relationships = populated_graph.relationships["TEST_AAPL"]
        found = any(rel[0] == "TEST_BOND" and rel[1] == "test_relationship" for rel in relationships)
        assert found

    def test_add_bidirectional_relationship(self, populated_graph):
        """Test adding a bidirectional relationship."""
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "bidirectional_test", 0.7, bidirectional=True)

        # Check forward direction
        assert "TEST_AAPL" in populated_graph.relationships
        forward_found = any(
            rel[0] == "TEST_BOND" and rel[1] == "bidirectional_test"
            for rel in populated_graph.relationships["TEST_AAPL"]
        )
        assert forward_found

        # Check reverse direction
        assert "TEST_BOND" in populated_graph.relationships
        reverse_found = any(
            rel[0] == "TEST_AAPL" and rel[1] == "bidirectional_test"
            for rel in populated_graph.relationships["TEST_BOND"]
        )
        assert reverse_found

    def test_relationship_strength_clamping(self, empty_graph, sample_equity, sample_bond):
        """Test that relationship strength is clamped to [0, 1]."""
        empty_graph.add_asset(sample_equity)
        empty_graph.add_asset(sample_bond)

        # Test strength > 1.0
        empty_graph.add_relationship(sample_equity.id, sample_bond.id, "test", 2.0)
        strength = [rel[2] for rel in empty_graph.relationships[sample_equity.id] if rel[0] == sample_bond.id][0]
        assert strength == 1.0

        # Test strength < 0.0
        empty_graph.add_relationship(sample_bond.id, sample_equity.id, "test", -0.5)
        strength = [rel[2] for rel in empty_graph.relationships[sample_bond.id] if rel[0] == sample_equity.id][0]
        assert strength == 0.0

    def test_add_regulatory_event(self, populated_graph, sample_regulatory_event):
        """Test adding a regulatory event."""
        populated_graph.add_regulatory_event(sample_regulatory_event)
        assert len(populated_graph.regulatory_events) == 1
        assert populated_graph.regulatory_events[0] == sample_regulatory_event

        # Check that relationships were created
        assert sample_regulatory_event.asset_id in populated_graph.relationships

    def test_build_relationships(self, populated_graph):
        """Test automatic relationship building."""
        initial_count = sum(len(rels) for rels in populated_graph.relationships.values())
        populated_graph.build_relationships()
        final_count = sum(len(rels) for rels in populated_graph.relationships.values())

        # Should have found some relationships
        assert final_count >= initial_count

    def test_calculate_metrics(self, populated_graph):
        """Test calculating graph metrics."""
        populated_graph.build_relationships()
        metrics = populated_graph.calculate_metrics()

        assert "total_assets" in metrics
        assert metrics["total_assets"] == 4
        assert "total_relationships" in metrics
        assert "average_relationship_strength" in metrics
        assert "asset_class_distribution" in metrics
        assert "relationship_distribution" in metrics
        assert "relationship_density" in metrics

    def test_same_sector_relationship(self):
        """Test that assets in the same sector are linked."""
        graph = AssetRelationshipGraph()

        equity1 = Equity(
            id="TECH1",
            symbol="TECH1",
            name="Tech Company 1",
            asset_class=AssetClass.EQUITY,
            sector="Technology",
            price=100.0,
        )
        equity2 = Equity(
            id="TECH2",
            symbol="TECH2",
            name="Tech Company 2",
            asset_class=AssetClass.EQUITY,
            sector="Technology",
            price=150.0,
        )

        graph.add_asset(equity1)
        graph.add_asset(equity2)
        graph.build_relationships()

        # Check for same_sector relationship
        relationships = graph.relationships.get("TECH1", [])
        same_sector = any(rel[1] == "same_sector" for rel in relationships if rel[0] == "TECH2")
        assert same_sector

    def test_corporate_bond_relationship(self):
        """Test that corporate bonds are linked to their issuing equity."""
        graph = AssetRelationshipGraph()

        equity = Equity(
            id="CORP_EQUITY",
            symbol="CORP",
            name="Corporation",
            asset_class=AssetClass.EQUITY,
            sector="Technology",
            price=100.0,
        )
        bond = Bond(
            id="CORP_BOND",
            symbol="CORP_BOND",
            name="Corporate Bond",
            asset_class=AssetClass.FIXED_INCOME,
            sector="Technology",
            price=1000.0,
            issuer_id="CORP_EQUITY",
        )

        graph.add_asset(equity)
        graph.add_asset(bond)
        graph.build_relationships()

        # Check for corporate_bond_to_equity relationship
        relationships = graph.relationships.get("CORP_BOND", [])
        corporate_link = any(rel[1] == "corporate_bond_to_equity" for rel in relationships if rel[0] == "CORP_EQUITY")
        assert corporate_link

    def test_get_3d_visualization_data(self, populated_graph):
        """Test generating 3D visualization data."""
        positions, asset_ids, colors, text, edges = populated_graph.get_3d_visualization_data()

        assert isinstance(positions, np.ndarray)
        assert positions.shape[0] == len(populated_graph.assets)
        assert positions.shape[1] == 3
        assert len(asset_ids) == len(populated_graph.assets)
        assert len(colors) == len(populated_graph.assets)
        assert len(text) == len(populated_graph.assets)

    def test_positions_persistence(self, populated_graph):
        """Test that 3D positions are deterministic and persistent."""
        # Get positions twice
        positions1, _, _, _, _ = populated_graph.get_3d_visualization_data()
        positions2, _, _, _, _ = populated_graph.get_3d_visualization_data()

        # Positions should be identical
        np.testing.assert_array_equal(positions1, positions2)

    def test_deduplication(self, empty_graph, sample_equity, sample_bond):
        """Test that duplicate relationships are not added."""
        empty_graph.add_asset(sample_equity)
        empty_graph.add_asset(sample_bond)

        # Add the same relationship twice
        empty_graph.add_relationship(sample_equity.id, sample_bond.id, "test", 0.5)
        empty_graph.add_relationship(sample_equity.id, sample_bond.id, "test", 0.5)

        # Should only have one relationship
        relationships = empty_graph.relationships[sample_equity.id]
        test_rels = [rel for rel in relationships if rel[0] == sample_bond.id and rel[1] == "test"]
        assert len(test_rels) == 1
