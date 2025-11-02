"""
2D Network Visualization Module for Asset Relationship Graph
Provides 2D layout algorithms and visualization functions
"""

import math
import numpy as np
from typing import Dict, List, Tuple
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph


def visualize_2d_graph(graph: AssetRelationshipGraph,
                       show_same_sector: bool = True,
                       show_market_cap: bool = True,
                       show_correlation: bool = True,
                       show_corporate_bond: bool = True,
                       show_commodity_currency: bool = True,
                       show_income_comparison: bool = True,
                       show_regulatory: bool = True,
                       show_all_relationships: bool = False,
                       layout_type: str = "spring") -> go.Figure:
    """Create 2D network visualization of asset relationship graph"""

    # Get enhanced visualization data
    positions_3d, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    # Convert 3D positions to 2D using different layout strategies
    if layout_type == "circular":
        positions = _create_circular_layout(asset_ids)
    elif layout_type == "grid":
        positions = _create_grid_layout(asset_ids)
    else:  # spring layout (default)
        positions = _create_spring_layout_2d(positions_3d, asset_ids)

    fig = go.Figure()

    # Add relationship edges first (so they appear behind nodes)
    if show_all_relationships or any([show_same_sector, show_market_cap, show_correlation,
                                     show_corporate_bond, show_commodity_currency,
                                     show_income_comparison, show_regulatory]):

        relationship_traces = _create_2d_relationship_traces(
            graph, positions, asset_ids,
            show_same_sector, show_market_cap, show_correlation,
            show_corporate_bond, show_commodity_currency, show_income_comparison,
            show_regulatory, show_all_relationships
        )

        for trace in relationship_traces:
            fig.add_trace(trace)

    # Add asset nodes
    x_coords = [positions[asset_id][0] for asset_id in asset_ids]
    y_coords = [positions[asset_id][1] for asset_id in asset_ids]

    # Create node sizes based on asset importance (price or market cap)
    node_sizes = []
    for asset_id in asset_ids:
        asset = graph.assets[asset_id]
        if hasattr(asset, 'market_cap') and asset.market_cap:
            # Size based on market cap (normalized)
            size = max(20, min(50, 20 + (asset.market_cap / 1e12) * 20))
        else:
            # Size based on price (normalized)
            size = max(20, min(50, 20 + (asset.price / 1000) * 15))
        node_sizes.append(size)

    # Add main node trace
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=colors,
            line=dict(width=2, color='black'),
            opacity=0.8
        ),
        text=asset_ids,
        textposition="middle center",
        textfont=dict(size=10, color='white'),
        hovertext=hover_texts,
        hoverinfo='text',
        name='Assets',
        showlegend=False
    ))

    # Update layout for 2D
    fig.update_layout(
        title=dict(
            text="📈 2D Asset Relationship Network",
            x=0.5,
            font=dict(size=20, color='#2C3E50')
        ),
        showlegend=True,
        hovermode='closest',
        margin=dict(b=40, l=40, r=40, t=80),
        annotations=[
            dict(
                text=f"Network Layout: {layout_type.title()} | Assets: {len(asset_ids)} | "
                     f"Relationships: {sum(len(rels) for rels in graph.relationships.values())}",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor="left", yanchor="bottom",
                font=dict(size=12, color='#7F8C8D')
            )
        ],
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        )
    )

    return fig


def _create_circular_layout(asset_ids: List[str]) -> Dict[str, Tuple[float, float]]:
    """Create circular layout for 2D visualization"""
    positions = {}
    n_assets = len(asset_ids)

    for i, asset_id in enumerate(asset_ids):
        angle = 2 * math.pi * i / n_assets
        x = math.cos(angle)
        y = math.sin(angle)
        positions[asset_id] = (x, y)

    return positions


def _create_grid_layout(asset_ids: List[str]) -> Dict[str, Tuple[float, float]]:
    """Create grid layout for 2D visualization"""
    positions = {}
    n_assets = len(asset_ids)
    grid_size = math.ceil(math.sqrt(n_assets))

    for i, asset_id in enumerate(asset_ids):
        row = i // grid_size
        col = i % grid_size
        x = col - grid_size / 2
        y = row - grid_size / 2
        positions[asset_id] = (x, y)

    return positions


def _create_spring_layout_2d(positions_3d: np.ndarray,
                             asset_ids: List[str]) -> Dict[str, Tuple[float, float]]:
    """Convert 3D positions to 2D using projection"""
    positions = {}

    for idx, asset_id in enumerate(asset_ids):
        x3d, y3d, z3d = positions_3d[idx]
        # Project to 2D by ignoring z-coordinate and normalizing
        positions[asset_id] = (float(x3d), float(y3d))

    return positions


def _create_2d_relationship_traces(graph: AssetRelationshipGraph,
                                   positions: Dict[str, Tuple[float, float]],
                                   asset_ids: List[str],
                                   show_same_sector: bool,
                                   show_market_cap: bool,
                                   show_correlation: bool,
                                   show_corporate_bond: bool,
                                   show_commodity_currency: bool,
                                   show_income_comparison: bool,
                                   show_regulatory: bool,
                                   show_all_relationships: bool) -> List[go.Scatter]:
    """Create 2D relationship traces with filtering"""

    traces = []

    # Define relationship filters
    filters = {
        'same_sector': show_same_sector or show_all_relationships,
        'market_cap_similar': show_market_cap or show_all_relationships,
        'correlation': show_correlation or show_all_relationships,
        'corporate_bond_to_equity': show_corporate_bond or show_all_relationships,
        'commodity_currency': show_commodity_currency or show_all_relationships,
        'income_comparison': show_income_comparison or show_all_relationships,
        'regulatory_impact': show_regulatory or show_all_relationships
    }

    # Color mapping for relationship types
    color_map = {
        'same_sector': '#FF6B6B',
        'market_cap_similar': '#4ECDC4',
        'correlation': '#45B7D1',
        'corporate_bond_to_equity': '#96CEB4',
        'commodity_currency': '#FFEAA7',
        'income_comparison': '#DDA0DD',
        'regulatory_impact': '#98D8C8'
    }

    # Group relationships by type
    relationships_by_type = {}
    for source_id, relationships in graph.relationships.items():
        for target_id, rel_type, strength in relationships:
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append((source_id, target_id, strength))

    # Create traces for each relationship type
    for rel_type, rel_list in relationships_by_type.items():
        if not filters.get(rel_type, False):
            continue

        edges_x = []
        edges_y = []
        hover_texts = []

        for source_id, target_id, strength in rel_list:
            if source_id in positions and target_id in positions:
                x0, y0 = positions[source_id]
                x1, y1 = positions[target_id]

                edges_x.extend([x0, x1, None])
                edges_y.extend([y0, y1, None])
                hover_texts.append(f"{rel_type}: {source_id} ↔ {target_id} (strength: {strength:.2f})")

        if edges_x:  # Only create trace if there are edges
            color = color_map.get(rel_type, '#CCCCCC')

            # Determine line style based on relationship directionality
            bidirectional_types = ['same_sector', 'market_cap_similar', 'correlation',
                                   'commodity_currency', 'income_comparison']
            line_width = 3 if rel_type in bidirectional_types else 2
            line_dash = 'solid' if rel_type in bidirectional_types else 'dash'

            trace_name = rel_type.replace('_', ' ').title()
            if rel_type not in bidirectional_types:
                trace_name += " (→)"

            trace = go.Scatter(
                x=edges_x, y=edges_y,
                mode='lines',
                line=dict(
                    color=color,
                    width=line_width,
                    dash=line_dash
                ),
                hovertext=hover_texts,
                hoverinfo='text',
                name=trace_name,
                visible=True,
                legendgroup=rel_type,
                opacity=0.7
            )
            traces.append(trace)

    return traces
