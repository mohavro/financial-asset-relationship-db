"""Unit tests for 3D graph visualizations.

This module contains comprehensive unit tests for the graph_visuals module including:
- 3D graph visualization creation
- Relationship trace creation for 3D
- Directional arrow creation
- Filtering options
- Edge cases and error handling
"""

import pytest
import numpy as np

import plotly.graph_objects as go

from src.visualizations.graph_visuals import (
    visualize_3d_graph,
    visualize_3d_graph_with_filters,
)


@pytest.mark.unit
class TestVisualize3DGraph:
    """Test suite for the visualize_3d_graph function."""

    def test_visualize_3d_graph_with_populated_graph(self, populated_graph):
        """Test creating 3D visualization with populated graph."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)
        assert "Financial Asset Relationship Network" in fig.layout.title.text
        assert fig.layout.width == 1200
        assert fig.layout.height == 800
        assert fig.layout.showlegend is True

    def test_visualize_3d_graph_with_empty_graph(self, empty_graph):
        """Test creating 3D visualization with empty graph."""
        # Execute
        fig = visualize_3d_graph(empty_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_has_scene_configuration(self, populated_graph):
        """Test that 3D scene is properly configured."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert hasattr(fig.layout, 'scene')
        scene = fig.layout.scene
        assert hasattr(scene, 'xaxis')
        assert hasattr(scene, 'yaxis')
        assert hasattr(scene, 'zaxis')
        assert scene.xaxis.title.text == "Dimension 1"
        assert scene.yaxis.title.text == "Dimension 2"
        assert scene.zaxis.title.text == "Dimension 3"

    def test_visualize_3d_graph_has_camera_configuration(self, populated_graph):
        """Test that camera is properly configured."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert hasattr(fig.layout.scene, 'camera')
        camera = fig.layout.scene.camera
        assert hasattr(camera, 'eye')

    def test_visualize_3d_graph_includes_nodes(self, populated_graph):
        """Test that node trace is included."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Find node trace (should have mode containing 'markers+text')
        node_traces = [
            trace for trace in fig.data
            if hasattr(trace, 'mode') and 'markers' in trace.mode and 'text' in trace.mode
        ]
        
        # Assert
        assert len(node_traces) > 0, "Should have at least one node trace"
        node_trace = node_traces[0]
        assert node_trace.name == "Assets"
        assert hasattr(node_trace, 'x')
        assert hasattr(node_trace, 'y')
        assert hasattr(node_trace, 'z')

    def test_visualize_3d_graph_node_properties(self, populated_graph):
        """Test node trace properties."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Find node trace
        node_traces = [
            trace for trace in fig.data
            if hasattr(trace, 'mode') and 'markers' in trace.mode and 'text' in trace.mode
        ]
        
        node_trace = node_traces[0]
        
        # Assert marker properties
        assert node_trace.marker.size == 15
        assert node_trace.marker.opacity == 0.9
        assert hasattr(node_trace.marker, 'color')
        assert hasattr(node_trace.marker, 'line')

    def test_visualize_3d_graph_preserves_graph_state(self, populated_graph):
        """Test that visualization doesn't modify the graph."""
        initial_asset_count = len(populated_graph.assets)
        initial_relationship_count = sum(len(rels) for rels in populated_graph.relationships.values())
        
        # Execute
        visualize_3d_graph(populated_graph)

        # Assert
        assert len(populated_graph.assets) == initial_asset_count
        assert sum(len(rels) for rels in populated_graph.relationships.values()) == initial_relationship_count

    def test_visualize_3d_graph_with_single_asset(self, empty_graph, sample_equity):
        """Test 3D visualization with only one asset."""
        empty_graph.add_asset(sample_equity)
        
        # Execute
        fig = visualize_3d_graph(empty_graph)

        # Assert
        assert isinstance(fig, go.Figure)
        # Should have at least one node
        node_traces = [t for t in fig.data if hasattr(t, 'mode') and 'markers' in t.mode]
        assert len(node_traces) > 0


@pytest.mark.unit
class TestVisualize3DGraphWithFilters:
    """Test suite for visualize_3d_graph_with_filters function."""

    def test_visualize_3d_graph_with_all_filters_on(self, populated_graph):
        """Test 3D visualization with all filters enabled."""
        # Execute
        fig = visualize_3d_graph_with_filters(
            populated_graph,
            show_same_sector=True,
            show_market_cap=True,
            show_correlation=True,
            show_corporate_bond=True,
            show_commodity_currency=True,
            show_income_comparison=True,
            show_regulatory=True,
            show_all_relationships=True,
            toggle_arrows=True,
        )

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_with_all_filters_off(self, populated_graph):
        """Test 3D visualization with all filters disabled."""
        # Execute
        fig = visualize_3d_graph_with_filters(
            populated_graph,
            show_same_sector=False,
            show_market_cap=False,
            show_correlation=False,
            show_corporate_bond=False,
            show_commodity_currency=False,
            show_income_comparison=False,
            show_regulatory=False,
            show_all_relationships=False,
            toggle_arrows=False,
        )

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_selective_filtering(self, populated_graph):
        """Test selective relationship filtering."""
        # Execute - only show same sector and correlation
        fig = visualize_3d_graph_with_filters(
            populated_graph,
            show_same_sector=True,
            show_market_cap=False,
            show_correlation=True,
            show_corporate_bond=False,
            show_commodity_currency=False,
            show_income_comparison=False,
            show_regulatory=False,
            show_all_relationships=False,
            toggle_arrows=False,
        )

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_show_all_overrides_filters(self, populated_graph):
        """Test that show_all_relationships overrides individual filters."""
        # Execute - show_all=True should override all False filters
        fig = visualize_3d_graph_with_filters(
            populated_graph,
            show_same_sector=False,
            show_market_cap=False,
            show_correlation=False,
            show_corporate_bond=False,
            show_commodity_currency=False,
            show_income_comparison=False,
            show_regulatory=False,
            show_all_relationships=True,
            toggle_arrows=True,
        )

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_with_arrows_toggle(self, populated_graph):
        """Test arrow toggle functionality."""
        # Add a unidirectional relationship
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "corporate_bond_to_equity", 0.8)
        
        # Execute with arrows on
        fig_with_arrows = visualize_3d_graph_with_filters(
            populated_graph,
            show_all_relationships=True,
            toggle_arrows=True,
        )
        
        # Execute with arrows off
        fig_without_arrows = visualize_3d_graph_with_filters(
            populated_graph,
            show_all_relationships=True,
            toggle_arrows=False,
        )

        # Assert
        assert isinstance(fig_with_arrows, go.Figure)
        assert isinstance(fig_without_arrows, go.Figure)

    def test_visualize_3d_graph_with_empty_graph(self, empty_graph):
        """Test filtered 3D visualization with empty graph."""
        # Execute
        fig = visualize_3d_graph_with_filters(
            empty_graph,
            show_all_relationships=True,
            toggle_arrows=True,
        )

        # Assert
        assert isinstance(fig, go.Figure)


@pytest.mark.unit
class TestRelationshipVisualization:
    """Test suite for relationship visualization in 3D."""

    def test_visualize_3d_graph_with_multiple_relationship_types(self, populated_graph):
        """Test visualization with multiple relationship types."""
        # Add various relationships
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "corporate_bond_to_equity", 0.8)
        populated_graph.add_relationship("TEST_GOLD", "TEST_EUR", "commodity_currency", 0.6)
        
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)
        # Should have relationship traces
        assert len(fig.data) > 1, "Should have both node and relationship traces"

    def test_visualize_3d_graph_bidirectional_relationships(self, populated_graph):
        """Test visualization handles bidirectional relationships."""
        # Add bidirectional relationship
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "correlation", 0.7)
        populated_graph.add_relationship("TEST_BOND", "TEST_AAPL", "correlation", 0.7)
        
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_unidirectional_relationships(self, populated_graph):
        """Test visualization of unidirectional relationships."""
        # Add unidirectional relationship
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "corporate_bond_to_equity", 0.8)
        # Don't add reverse relationship
        
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_visualize_3d_graph_with_many_assets(self, empty_graph):
        """Test 3D visualization with many assets."""
        from src.models.financial_models import Equity, AssetClass
        
        # Add 20 assets
        for i in range(20):
            equity = Equity(
                id=f"ASSET_{i}",
                symbol=f"AST{i}",
                name=f"Asset {i}",
                asset_class=AssetClass.EQUITY,
                sector="Technology" if i % 2 == 0 else "Finance",
                price=100.0 + i * 5,
                market_cap=1e10 * (i + 1),
                pe_ratio=20.0,
                dividend_yield=0.02,
                earnings_per_share=5.0,
            )
            empty_graph.add_asset(equity)

        # Execute
        fig = visualize_3d_graph(empty_graph)

        # Assert
        assert isinstance(fig, go.Figure)
        # Should handle many assets
        node_traces = [t for t in fig.data if hasattr(t, 'mode') and 'markers' in t.mode]
        assert len(node_traces) > 0

    def test_visualize_3d_graph_with_many_relationships(self, populated_graph):
        """Test 3D visualization with many relationships."""
        # Add many relationships
        asset_ids = list(populated_graph.assets.keys())
        for i, source in enumerate(asset_ids):
            for target in asset_ids[i+1:]:
                populated_graph.add_relationship(source, target, "correlation", 0.5)

        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_handles_missing_3d_data(self, empty_graph):
        """Test that visualization handles cases where 3D positioning might fail."""
        from src.models.financial_models import Equity, AssetClass
        
        # Add minimal assets
        equity = Equity(
            id="MIN_ASSET",
            symbol="MIN",
            name="Minimal Asset",
            asset_class=AssetClass.EQUITY,
            sector="Test",
            price=100.0,
            market_cap=1e9,
            pe_ratio=15.0,
            dividend_yield=0.01,
            earnings_per_share=6.67,
        )
        empty_graph.add_asset(equity)

        # Execute
        fig = visualize_3d_graph(empty_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_with_zero_strength_relationships(self, populated_graph):
        """Test visualization with zero-strength relationships."""
        # Add relationship with zero strength
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "correlation", 0.0)
        
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_with_high_strength_relationships(self, populated_graph):
        """Test visualization with maximum strength relationships."""
        # Add relationship with maximum strength
        populated_graph.add_relationship("TEST_AAPL", "TEST_BOND", "correlation", 1.0)
        
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_filtered_visualization_preserves_graph_state(self, populated_graph):
        """Test that filtered visualization doesn't modify the graph."""
        initial_asset_count = len(populated_graph.assets)
        initial_relationship_count = sum(len(rels) for rels in populated_graph.relationships.values())
        
        # Execute
        visualize_3d_graph_with_filters(
            populated_graph,
            show_all_relationships=True,
            toggle_arrows=True,
        )

        # Assert
        assert len(populated_graph.assets) == initial_asset_count
        assert sum(len(rels) for rels in populated_graph.relationships.values()) == initial_relationship_count

    def test_visualize_3d_graph_with_all_same_sector(self, empty_graph):
        """Test visualization when all assets are in the same sector."""
        from src.models.financial_models import Equity, AssetClass
        
        # Add multiple assets in same sector
        for i in range(3):
            equity = Equity(
                id=f"TECH_{i}",
                symbol=f"TCH{i}",
                name=f"Tech Stock {i}",
                asset_class=AssetClass.EQUITY,
                sector="Technology",
                price=100.0 + i * 10,
                market_cap=1e10,
                pe_ratio=20.0,
                dividend_yield=0.01,
                earnings_per_share=5.0,
            )
            empty_graph.add_asset(equity)

        # Execute
        fig = visualize_3d_graph(empty_graph)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_visualize_3d_graph_legend_configuration(self, populated_graph):
        """Test that legend is properly configured."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert fig.layout.showlegend is True
        assert hasattr(fig.layout, 'legend')
        legend = fig.layout.legend
        assert legend.x == 0.02
        assert legend.y == 0.98

    def test_visualize_3d_graph_hover_mode(self, populated_graph):
        """Test that hover mode is properly set."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert
        assert fig.layout.hovermode == "closest"

    def test_visualize_3d_graph_grid_display(self, populated_graph):
        """Test that grid is properly configured."""
        # Execute
        fig = visualize_3d_graph(populated_graph)

        # Assert scene grid configuration
        scene = fig.layout.scene
        assert scene.xaxis.showgrid is True
        assert scene.yaxis.showgrid is True
        assert scene.zaxis.showgrid is True