from collections import defaultdict
from typing import List, Set, Tuple

import numpy as np
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph

# Color and style mapping for relationship types (shared constant)
REL_TYPE_COLORS = defaultdict(
    lambda: "#888888",
    {
        "same_sector": "#FF6B6B",  # Red for sector relationships
        "market_cap_similar": "#4ECDC4",  # Teal for market cap
        "correlation": "#45B7D1",  # Blue for correlations
        "corporate_bond_to_equity": "#96CEB4",  # Green for corporate bonds
        "commodity_currency": "#FFEAA7",  # Yellow for commodity-currency
        "income_comparison": "#DDA0DD",  # Plum for income comparisons
        "regulatory_impact": "#FFA07A",  # Light salmon for regulatory
    },
)


def _get_relationship_color(rel_type: str) -> str:
    """Get color for a relationship type"""
    return REL_TYPE_COLORS[rel_type]


def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create enhanced 3D visualization of asset relationship graph with improved relationship visibility"""
    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    # Create index mapping for O(1) lookups
    asset_id_to_idx = {asset_id: idx for idx, asset_id in enumerate(asset_ids)}

    fig = go.Figure()

    # Create separate traces for different relationship types and directions
    relationship_traces = _create_relationship_traces(graph, positions, asset_ids, asset_id_to_idx)

    # Add all relationship traces
    for trace in relationship_traces:
        fig.add_trace(trace)

    # Add directional arrows for unidirectional relationships
    arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    for trace in arrow_traces:
        fig.add_trace(trace)

    # Add nodes with enhanced styling
    fig.add_trace(
        go.Scatter3d(
            x=positions[:, 0],
            y=positions[:, 1],
            z=positions[:, 2],
            mode="markers+text",
            marker=dict(
                size=15,  # Larger nodes for better visibility
                color=colors,
                opacity=0.9,
                line=dict(color="rgba(0,0,0,0.8)", width=2),
                symbol="circle",
            ),
            text=asset_ids,
            hovertext=hover_texts,
            hoverinfo="text",
            textposition="top center",
            textfont=dict(size=12, color="black"),
            name="Assets",
            visible=True,
        )
    )

    fig.update_layout(
        title={
            "text": "Financial Asset Relationship Network - Enhanced 3D Visualization",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=dict(
            xaxis=dict(title="Dimension 1", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            yaxis=dict(title="Dimension 2", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            zaxis=dict(title="Dimension 3", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            bgcolor="rgba(248, 248, 248, 0.95)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        width=1200,
        height=800,
        showlegend=True,
        hovermode="closest",
        legend=dict(
            x=0.02, y=0.98, bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="rgba(0, 0, 0, 0.3)", borderwidth=1
        ),
    )

    return fig


def _build_relationship_set(graph: AssetRelationshipGraph, asset_ids: List[str]) -> Set[Tuple[str, str, str]]:
    """Build a set of all relationships for O(1) reverse relationship lookups.

    This optimization reduces the time complexity of reverse relationship checks
    from O(n) to O(1) by pre-building a set of all relationships. This is especially
    beneficial for graphs with a large number of relationships.

    Args:
        graph: The asset relationship graph
        asset_ids: List of asset IDs to include

    Returns:
        Set of tuples (source_id, target_id, rel_type) for all relationships
    """
    relationship_set = set()
    asset_ids_set = set(asset_ids)  # Convert to set for O(1) membership checks

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids_set:
            continue
        for target_id, rel_type, _ in rels:
            if target_id not in asset_ids_set:
                continue
            relationship_set.add((source_id, target_id, rel_type))

    return relationship_set


def _collect_relationships(
    graph: AssetRelationshipGraph, asset_ids: List[str], relationship_filters: dict = None
) -> tuple:
    """Collect all relationships with directionality info and filtering.

    Uses a pre-built relationship set for O(1) reverse relationship lookups,
    significantly improving performance for graphs with many relationships.

    Args:
        graph: The asset relationship graph
        asset_ids: List of asset IDs to include
        relationship_filters: Optional dict to filter relationship types

    Returns:
        Tuple of (all_relationships list, bidirectional_pairs set)
    """
    # Build relationship set once for O(1) lookups
    relationship_set = _build_relationship_set(graph, asset_ids)

    bidirectional_pairs = set()
    all_relationships = []

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            # Skip if this relationship type is filtered out
            if relationship_filters and rel_type in relationship_filters and not relationship_filters[rel_type]:
                continue

            pair_key = tuple(sorted([source_id, target_id]) + [rel_type])
            # O(1) lookup instead of O(n) iteration
            reverse_exists = (target_id, source_id, rel_type) in relationship_set
            is_bidirectional = reverse_exists and pair_key not in bidirectional_pairs

            if is_bidirectional:
                bidirectional_pairs.add(pair_key)

            all_relationships.append(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "rel_type": rel_type,
                    "strength": strength,
                    "is_bidirectional": is_bidirectional,
                    "pair_key": pair_key,
                }
            )

    return all_relationships, bidirectional_pairs


def _group_relationships(all_relationships: list, bidirectional_pairs: set) -> dict:
    """Group relationships by type and directionality"""
    relationship_groups = {}

    for rel in all_relationships:
        if rel["is_bidirectional"] and rel["pair_key"] in bidirectional_pairs:
            bidirectional_pairs.discard(rel["pair_key"])
        elif rel["is_bidirectional"]:
            continue

        group_key = (rel["rel_type"], rel["is_bidirectional"])
        if group_key not in relationship_groups:
            relationship_groups[group_key] = []
        relationship_groups[group_key].append(rel)

    return relationship_groups


def _build_edge_coordinates(relationships: list, positions: np.ndarray, asset_ids: List[str]) -> tuple:
    """Build edge coordinate lists for relationships"""
    edges_x, edges_y, edges_z = [], [], []

    for rel in relationships:
        source_idx = asset_ids.index(rel["source_id"])
        target_idx = asset_ids.index(rel["target_id"])

        edges_x.extend([positions[source_idx, 0], positions[target_idx, 0], None])
        edges_y.extend([positions[source_idx, 1], positions[target_idx, 1], None])
        edges_z.extend([positions[source_idx, 2], positions[target_idx, 2], None])

    return edges_x, edges_y, edges_z


def _build_hover_texts(relationships: list, rel_type: str, is_bidirectional: bool) -> list:
    """Build hover text list for relationships"""
    hover_texts = []
    direction_text = "↔" if is_bidirectional else "→"

    for rel in relationships:
        hover_text = f"{rel['source_id']} {direction_text} {rel['target_id']}<br>Type: {rel_type}<br>Strength: {rel['strength']:.2f}"
        hover_texts.extend([hover_text, hover_text, None])

    return hover_texts


def _get_line_style(rel_type: str, is_bidirectional: bool) -> dict:
    """Get line style configuration for a relationship"""
    return dict(
        color=_get_relationship_color(rel_type),
        width=4 if is_bidirectional else 2,
        dash="solid" if is_bidirectional else "dash",
    )


def _format_trace_name(rel_type: str, is_bidirectional: bool) -> str:
    """Format trace name for legend"""
    base_name = rel_type.replace("_", " ").title()
    direction_symbol = " (↔)" if is_bidirectional else " (→)"
    return base_name + direction_symbol


def _create_trace_for_group(
    rel_type: str, is_bidirectional: bool, relationships: list, positions: np.ndarray, asset_ids: List[str]
) -> go.Scatter3d:
    """Create a single trace for a relationship group"""
    edges_x, edges_y, edges_z = _build_edge_coordinates(relationships, positions, asset_ids)
    hover_texts = _build_hover_texts(relationships, rel_type, is_bidirectional)

    return go.Scatter3d(
        x=edges_x,
        y=edges_y,
        z=edges_z,
        mode="lines",
        line=_get_line_style(rel_type, is_bidirectional),
        hovertext=hover_texts,
        hoverinfo="text",
        name=_format_trace_name(rel_type, is_bidirectional),
        visible=True,
        legendgroup=rel_type,
    )


def _create_relationship_traces(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create separate traces for different types of relationships with enhanced visibility"""
    all_relationships, bidirectional_pairs = _collect_relationships(graph, asset_ids)
    relationship_groups = _group_relationships(all_relationships, bidirectional_pairs)

    traces = []
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        if relationships:
            trace = _create_trace_for_group(rel_type, is_bidirectional, relationships, positions, asset_ids)
            traces.append(trace)

    return traces


def _create_directional_arrows(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create arrow markers for unidirectional relationships.

    Uses a pre-built relationship set for O(1) reverse relationship lookups,
    improving performance compared to iterating through all relationships.
    """
    arrows = []

    # Build relationship set once for O(1) lookups
    relationship_set = _build_relationship_set(graph, asset_ids)

    # Find unidirectional relationships
    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            # Check if this is truly unidirectional using O(1) lookup
            if (target_id, source_id, rel_type) not in relationship_set:
                source_idx = asset_ids.index(source_id)
                target_idx = asset_ids.index(target_id)

                # Calculate arrow position (70% along the edge towards target)
                arrow_pos = positions[source_idx] + 0.7 * (positions[target_idx] - positions[source_idx])

                arrows.append(
                    {
                        "pos": arrow_pos,
                        "hover": f"Direction: {source_id} → {target_id}<br>Type: {rel_type}",
                        "rel_type": rel_type,
                    }
                )

    # Create arrow trace
    if arrows:
        arrow_x = [arrow["pos"][0] for arrow in arrows]
        arrow_y = [arrow["pos"][1] for arrow in arrows]
        arrow_z = [arrow["pos"][2] for arrow in arrows]
        arrow_hovers = [arrow["hover"] for arrow in arrows]

        arrow_trace = go.Scatter3d(
            x=arrow_x,
            y=arrow_y,
            z=arrow_z,
            mode="markers",
            marker=dict(
                symbol="diamond",  # Use diamond instead of arrow for 3D compatibility
                size=8,
                color="rgba(255, 0, 0, 0.8)",
                line=dict(color="red", width=1),
            ),
            hovertext=arrow_hovers,
            hoverinfo="text",
            name="Direction Arrows",
            visible=True,
            showlegend=False,
        )
        return [arrow_trace]
    return []


def visualize_3d_graph_with_filters(
    graph: AssetRelationshipGraph,
    show_same_sector: bool = True,
    show_market_cap: bool = True,
    show_correlation: bool = True,
    show_corporate_bond: bool = True,
    show_commodity_currency: bool = True,
    show_income_comparison: bool = True,
    show_regulatory: bool = True,
    show_all_relationships: bool = True,
    toggle_arrows: bool = True,
) -> go.Figure:
    """Create 3D visualization with selective relationship filtering"""

    if not show_all_relationships:
        # Filter which relationship types to show
        relationship_filters = {
            "same_sector": show_same_sector,
            "market_cap_similar": show_market_cap,
            "correlation": show_correlation,
            "corporate_bond_to_equity": show_corporate_bond,
            "commodity_currency": show_commodity_currency,
            "income_comparison": show_income_comparison,
            "regulatory_impact": show_regulatory,
        }
    else:
        # Show all relationships if the master toggle is on
        relationship_filters = None

    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    fig = go.Figure()

    # Create relationship traces with filtering
    relationship_traces = _create_filtered_relationship_traces(graph, positions, asset_ids, relationship_filters)

    # Add all relationship traces
    for trace in relationship_traces:
        fig.add_trace(trace)

    # Add directional arrows if enabled
    if toggle_arrows:
        arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
        for trace in arrow_traces:
            fig.add_trace(trace)

    # Add nodes with enhanced styling
    fig.add_trace(
        go.Scatter3d(
            x=positions[:, 0],
            y=positions[:, 1],
            z=positions[:, 2],
            mode="markers+text",
            marker=dict(
                size=15, color=colors, opacity=0.9, line=dict(color="rgba(0,0,0,0.8)", width=2), symbol="circle"
            ),
            text=asset_ids,
            hovertext=hover_texts,
            hoverinfo="text",
            textposition="top center",
            textfont=dict(size=12, color="black"),
            name="Assets",
            visible=True,
        )
    )

    # Count visible relationships
    visible_relationships = sum(len(trace.x or []) for trace in relationship_traces if hasattr(trace, "x")) // 3

    fig.update_layout(
        title={
            "text": f"Financial Asset Network - {len(asset_ids)} Assets, {visible_relationships} Relationships",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=dict(
            xaxis=dict(title="Dimension 1", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            yaxis=dict(title="Dimension 2", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            zaxis=dict(title="Dimension 3", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
            bgcolor="rgba(248, 248, 248, 0.95)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        width=1200,
        height=800,
        showlegend=True,
        hovermode="closest",
        legend=dict(
            x=0.02, y=0.98, bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="rgba(0, 0, 0, 0.3)", borderwidth=1
        ),
    )

    return fig


def _create_filtered_relationship_traces(
    graph: AssetRelationshipGraph,
    positions: np.ndarray,
    asset_ids: List[str],
    relationship_filters: dict = None,
) -> List[go.Scatter3d]:
    """Create relationship traces with optional filtering"""
    if relationship_filters is None:
        return _create_relationship_traces(graph, positions, asset_ids)

    all_relationships, bidirectional_pairs = _collect_relationships(graph, asset_ids, relationship_filters)
    relationship_groups = _group_relationships(all_relationships, bidirectional_pairs)

    traces = []
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        if relationships:
            trace = _create_trace_for_group(rel_type, is_bidirectional, relationships, positions, asset_ids)
            traces.append(trace)

    return traces
