-
"""2D graph visualization module for asset relationship networks.

This module provides functions to create 2D visualizations of asset relationship graphs
with support for multiple layout algorithms (circular, grid, spring) and relationship filtering.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import plotly.graph_objects as go

from src.logic.asset_graph import AssetRelationshipGraph

logger = logging.getLogger(__name__)

# Relationship type colors (consistent with 3D visualization)
REL_TYPE_COLORS = {
    "same_sector": "#FF6B6B",
    "market_cap_similar": "#4ECDC4",
    "correlation": "#45B7D1",
    "corporate_bond_to_equity": "#96CEB4",
    "commodity_currency": "#FFEAA7",
    "income_comparison": "#DDA0DD",
    "regulatory_impact": "#FFA07A",
}


def _create_circular_layout(asset_ids: List[str]) -> Dict[str, Tuple[float, float]]:
    """Create circular layout for 2D visualization.

    Args:
        asset_ids: List of asset IDs to position

    Returns:
        Dictionary mapping asset IDs to (x, y) positions on a unit circle
    """
    if not asset_ids:
        return {}

    positions = {}
    n = len(asset_ids)

    for i, asset_id in enumerate(asset_ids):
        angle = 2 * math.pi * i / n
        x = math.cos(angle)
        y = math.sin(angle)
        positions[asset_id] = (x, y)

    return positions


def _create_grid_layout(asset_ids: List[str]) -> Dict[str, Tuple[float, float]]:
    """Create grid layout for 2D visualization.

    Args:
        asset_ids: List of asset IDs to position

    Returns:
        Dictionary mapping asset IDs to (x, y) positions in a grid
    """
    if not asset_ids:
        return {}

    positions = {}
    n = len(asset_ids)

    # Calculate grid dimensions (roughly square)
    cols = math.ceil(math.sqrt(n))

    for i, asset_id in enumerate(asset_ids):
        row = i // cols
        col = i % cols
        positions[asset_id] = (float(col), float(row))

    return positions


def _create_spring_layout_2d(
    positions_3d: Dict[str, Tuple[float, float, float]],
    asset_ids: List[str]
) -> Dict[str, Tuple[float, float]]:
    """Convert 3D spring layout positions to 2D by dropping z-coordinate.

    Args:
        positions_3d: Dictionary mapping asset IDs to (x, y, z) positions
        asset_ids: List of asset IDs

    Returns:
        Dictionary mapping asset IDs to (x, y) positions
    """
    if not positions_3d:
        return {}

    positions_2d = {}
    for asset_id in asset_ids:
        if asset_id in positions_3d:
            pos_3d = positions_3d[asset_id]
            # Handle both tuple and array-like positions
            if hasattr(pos_3d, '__getitem__'):
                positions_2d[asset_id] = (float(pos_3d[0]), float(pos_3d[1]))

    return positions_2d


def _create_2d_relationship_traces(
    graph: AssetRelationshipGraph,
    positions: Dict[str, Tuple[float, float]],
    asset_ids: List[str],
    show_same_sector: bool = True,
    show_market_cap: bool = True,
    show_correlation: bool = True,
    show_corporate_bond: bool = True,
    show_commodity_currency: bool = True,
    show_income_comparison: bool = True,
    show_regulatory: bool = True,
    show_all_relationships: bool = False,
) -> List[go.Scatter]:
    """Create 2D relationship traces with filtering.

    Args:
        graph: Asset relationship graph
        positions: Dictionary mapping asset IDs to (x, y) positions
        asset_ids: List of asset IDs
        show_same_sector: Show same sector relationships
        show_market_cap: Show market cap relationships
        show_correlation: Show correlation relationships
        show_corporate_bond: Show corporate bond relationships
        show_commodity_currency: Show commodity currency relationships
        show_income_comparison: Show income comparison relationships
        show_regulatory: Show regulatory relationships
        show_all_relationships: Master toggle to show all relationships

    Returns:
        List of Plotly Scatter traces for relationships
    """
    traces = []

    # Build filter map
    if not show_all_relationships:
        filter_map = {
            "same_sector": show_same_sector,
            "market_cap_similar": show_market_cap,
            "correlation": show_correlation,
            "corporate_bond_to_equity": show_corporate_bond,
            "commodity_currency": show_commodity_currency,
            "income_comparison": show_income_comparison,
            "regulatory_impact": show_regulatory,
        }
    else:
        filter_map = None

    # Group relationships by type
    relationship_groups = {}

    for source_id in asset_ids:
        if source_id not in graph.relationships:
            continue

        for target_id, rel_type, strength in graph.relationships[source_id]:
            # Skip if target not in positions
            if target_id not in positions:
                continue

            # Apply filters
            if filter_map is not None and rel_type in filter_map:
                if not filter_map[rel_type]:
                    continue

            # Group by relationship type
            if rel_type not in relationship_groups:
                relationship_groups[rel_type] = []

            relationship_groups[rel_type].append({
                'source_id': source_id,
                'target_id': target_id,
                'strength': strength
            })

    # Create traces for each relationship type
    for rel_type, relationships in relationship_groups.items():
        if not relationships:
            continue

        # Build edge coordinates
        edge_x = []
        edge_y = []
        hover_texts = []

        for rel in relationships:
            source_pos = positions[rel['source_id']]
            target_pos = positions[rel['target_id']]

            edge_x.extend([source_pos[0], target_pos[0], None])
            edge_y.extend([source_pos[1], target_pos[1], None])

            hover_text = (
                f"{rel['source_id']} → {rel['target_id']}<br>"
                f"Type: {rel_type}<br>"
                f"Strength: {rel['strength']:.2f}"
            )
            hover_texts.extend([hover_text, hover_text, None])

        # Get color for relationship type
        color = REL_TYPE_COLORS.get(rel_type, "#888888")

        # Create trace
        trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(color=color, width=2),
            hovertext=hover_texts,
            hoverinfo='text',
            name=rel_type.replace('_', ' ').title(),
            showlegend=True,
        )
        traces.append(trace)

    return traces


def visualize_2d_graph(
    graph: AssetRelationshipGraph,
    layout_type: str = "spring",
    show_same_sector: bool = True,
    show_market_cap: bool = True,
    show_correlation: bool = True,
    show_corporate_bond: bool = True,
    show_commodity_currency: bool = True,
    show_income_comparison: bool = True,
    show_regulatory: bool = True,
    show_all_relationships: bool = False,
) -> go.Figure:
    """Create 2D visualization of asset relationship graph.

    Args:
        graph: Asset relationship graph to visualize
        layout_type: Layout algorithm to use ('spring', 'circular', 'grid')
        show_same_sector: Show same sector relationships
        show_market_cap: Show market cap relationships
        show_correlation: Show correlation relationships
        show_corporate_bond: Show corporate bond relationships
        show_commodity_currency: Show commodity currency relationships
        show_income_comparison: Show income comparison relationships
        show_regulatory: Show regulatory relationships
        show_all_relationships: Master toggle to show all relationships

    Returns:
        Plotly Figure object with 2D visualization
    """
    # Get asset data
    asset_ids = list(graph.assets.keys())

    if not asset_ids:
        # Return empty figure for empty graph
        fig = go.Figure()
        fig.update_layout(
            title="2D Asset Relationship Network (No Assets)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            paper_bgcolor="#F8F9FA",
        )
        return fig

    # Create layout based on type
    if layout_type == "circular":
        positions = _create_circular_layout(asset_ids)
    elif layout_type == "grid":
        positions = _create_grid_layout(asset_ids)
    else:  # spring or default
        # Get 3D positions and convert to 2D
        try:
            positions_3d, _, _, _ = graph.get_3d_visualization_data_enhanced()
            positions_dict = {asset_ids[i]: positions_3d[i] for i in range(len(asset_ids))}
            positions = _create_spring_layout_2d(positions_dict, asset_ids)
        except Exception as e:
            logger.warning(f"Failed to get spring layout, falling back to circular: {e}")
            positions = _create_circular_layout(asset_ids)

    # Create figure
    fig = go.Figure()

    # Add relationship traces
    relationship_traces = _create_2d_relationship_traces(
        graph,
        positions,
        asset_ids,
        show_same_sector=show_same_sector,
        show_market_cap=show_market_cap,
        show_correlation=show_correlation,
        show_corporate_bond=show_corporate_bond,
        show_commodity_currency=show_commodity_currency,
        show_income_comparison=show_income_comparison,
        show_regulatory=show_regulatory,
        show_all_relationships=show_all_relationships,
    )

    for trace in relationship_traces:
        fig.add_trace(trace)

    # Add node trace
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    hover_texts = []

    for asset_id in asset_ids:
        if asset_id in positions:
            pos = positions[asset_id]
            node_x.append(pos[0])
            node_y.append(pos[1])
            node_text.append(asset_id)

            # Get asset info for color and hover text
            asset = graph.assets[asset_id]
            asset_class = asset.asset_class.value if hasattr(asset.asset_class, 'value') else str(asset.asset_class)

            # Color by asset class
            color_map = {
                'equity': '#1f77b4',
                'fixed_income': '#2ca02c',
                'commodity': '#ff7f0e',
                'currency': '#d62728',
                'derivative': '#9467bd',
            }
            node_colors.append(color_map.get(asset_class, '#7f7f7f'))

            hover_text = f"{asset_id}<br>Class: {asset_class}"
            hover_texts.append(hover_text)

    # Calculate node sizes based on connections
    node_sizes = []
    for asset_id in asset_ids:
        if asset_id in positions:
            num_connections = len(graph.relationships.get(asset_id, []))
            size = 20 + min(num_connections * 3, 30)  # Size between 20 and 50
            node_sizes.append(size)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(color='white', width=2),
        ),
        text=node_text,
        hovertext=hover_texts,
        hoverinfo='text',
        textposition='top center',
        name='Assets',
        showlegend=False,
    )
    fig.add_trace(node_trace)

    # Update layout
    fig.update_layout(
        title=f"2D Asset Relationship Network ({layout_type} layout)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        paper_bgcolor="#F8F9FA",
        hovermode='closest',
        showlegend=True,
        width=1200,
        height=800,
    )

    # Add layout type annotation
    fig.add_annotation(
        text=f"Layout: {layout_type}",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        font=dict(size=10, color="gray"),
    )

    return fig
