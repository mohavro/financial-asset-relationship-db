from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph

# Color and style mapping for relationship types (shared constant)
# Define default color as a constant for better maintainability
DEFAULT_COLOR = "#888888"  # Gray for unknown relationship types
REL_TYPE_COLORS = defaultdict(lambda: DEFAULT_COLOR, {
    "same_sector": "#FF6B6B",  # Red for sector relationships
    "market_cap_similar": "#4ECDC4",  # Teal for market cap
    "correlation": "#45B7D1",  # Blue for correlations
    "corporate_bond_to_equity": "#96CEB4",  # Green for corporate bonds
    "commodity_currency": "#FFEAA7",  # Yellow for commodity-currency
    "income_comparison": "#DDA0DD",  # Plum for income comparisons
    "regulatory_impact": "#FFA07A",  # Light salmon for regulatory
})


def _get_relationship_color(rel_type: str) -> str:
    """Get color for a relationship type"""
    return REL_TYPE_COLORS[rel_type]


def _build_asset_id_index(asset_ids: List[str]) -> Dict[str, int]:
    """Build O(1) lookup index for asset IDs to their positions.

    Args:
        asset_ids: List of asset IDs

    Returns:
        Dictionary mapping asset_id to its index in the list
    """
    return {asset_id: idx for idx, asset_id in enumerate(asset_ids)}


def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create enhanced 3D visualization of asset relationship graph with improved relationship visibility"""
    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    fig = go.Figure()

    # Create separate traces for different relationship types and directions
    relationship_traces = _create_relationship_traces(graph, positions, asset_ids)

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
    """Build a set of all relationships for O(1) reverse relationship lookups with optimized membership testing.

    Returns a set of tuples (source_id, target_id, rel_type) for efficient membership testing.
    """
    # Convert asset_ids to set for O(1) membership testing instead of O(n)
    asset_ids_set = set(asset_ids)

    relationship_set: Set[Tuple[str, str, str]] = set()
    for source_id, rels in graph.relationships.items():
        # O(1) lookup instead of O(n) for list membership
        if source_id not in asset_ids_set:
            continue
        for target_id, rel_type, _ in rels:
            if target_id in asset_ids_set:
                relationship_set.add((source_id, target_id, rel_type))
    return relationship_set


def _collect_and_group_relationships(
    graph: AssetRelationshipGraph,
    asset_ids: List[str],
    relationship_filters: Optional[Dict[str, bool]] = None,
) -> Dict[Tuple[str, bool], List[dict]]:
    """Collect and group relationships with directionality info and optional filtering.

    Optimized to minimize nested iterations and per-item checks using O(1) lookups.

    Returns a dictionary mapping (rel_type, is_bidirectional) to a list of relationships.
    """
    asset_ids_set = set(asset_ids)

    # Pre-compute allowed relationship types for O(1) checks per item
    allowed_types: Optional[Set[str]] = None
    if relationship_filters is not None:
        allowed_types = {rel for rel, allowed in relationship_filters.items() if allowed}

    # Build optimized relationship index: (source, target, type) -> strength
    relationship_index: Dict[Tuple[str, str, str], float] = {}
    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids_set:
            continue
        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids_set:
                continue
            if allowed_types is not None and rel_type not in allowed_types:
                continue
            relationship_index[(source_id, target_id, rel_type)] = strength

    processed_pairs: Set[Tuple[str, str, str]] = set()
    relationship_groups: Dict[Tuple[str, bool], List[dict]] = defaultdict(list)

    for (source_id, target_id, rel_type), strength in relationship_index.items():
        # Check for bidirectionality in O(1)
        is_bidirectional = (target_id, source_id, rel_type) in relationship_index

        # Skip duplicate entry for bidirectional pairs using canonical key
        if is_bidirectional:
            canonical_key = (min(source_id, target_id), max(source_id, target_id), rel_type)
            if canonical_key in processed_pairs:
                continue
            processed_pairs.add(canonical_key)

        group_key = (rel_type, is_bidirectional)
        relationship_groups[group_key].append(
            {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "strength": strength,
                "is_bidirectional": is_bidirectional,
            }
        )

    return relationship_groups


def _build_edge_coordinates_optimized(
    relationships: list, positions: np.ndarray, asset_id_index: Dict[str, int]
) -> Tuple[List[float], List[float], List[float]]:
    """Build edge coordinate lists for relationships using optimized O(1) lookups.

    Args:
        relationships: List of relationship dictionaries
        positions: NumPy array of node positions
        asset_id_index: Dictionary mapping asset_id to index for O(1) lookup

    Returns:
        Tuple of (edges_x, edges_y, edges_z) coordinate lists
    """
    # Pre-allocate arrays for better performance (3 values per relationship: start, end, None)
    num_edges = len(relationships)
    edges_x: List[float] = [None] * (num_edges * 3)  # type: ignore[list-item]
    edges_y: List[float] = [None] * (num_edges * 3)  # type: ignore[list-item]
    edges_z: List[float] = [None] * (num_edges * 3)  # type: ignore[list-item]

    for i, rel in enumerate(relationships):
        # O(1) lookup instead of O(n) list.index()
        source_idx = asset_id_index[rel["source_id"]]
        target_idx = asset_id_index[rel["target_id"]]

        # Calculate base index for this edge
        base_idx = i * 3

        # Set coordinates
        edges_x[base_idx] = positions[source_idx, 0]
        edges_x[base_idx + 1] = positions[target_idx, 0]

        edges_y[base_idx] = positions[source_idx, 1]
        edges_y[base_idx + 1] = positions[target_idx, 1]

        edges_z[base_idx] = positions[source_idx, 2]
        edges_z[base_idx + 1] = positions[target_idx, 2]

    return edges_x, edges_y, edges_z


def _build_hover_texts(relationships: list, rel_type: str, is_bidirectional: bool) -> list:
    """Build hover text list for relationships with pre-allocation for performance.

    Args:
        relationships: List of relationship dictionaries
        rel_type: Type of relationship
        is_bidirectional: Whether relationships are bidirectional

    Returns:
        List of hover texts
    """
    direction_text = "↔" if is_bidirectional else "→"

    # Pre-allocate array for better performance
    num_rels = len(relationships)
    hover_texts: List[str] = [None] * (num_rels * 3)  # type: ignore[list-item]

    for i, rel in enumerate(relationships):
        hover_text = (
            f"{rel['source_id']} {direction_text} {rel['target_id']}<br>"
            f"Type: {rel_type}<br>Strength: {rel['strength']:.2f}"
        )
        base_idx = i * 3
        hover_texts[base_idx] = hover_text
        hover_texts[base_idx + 1] = hover_text

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
    rel_type: str,
    is_bidirectional: bool,
    relationships: list,
    positions: np.ndarray,
    asset_id_index: Dict[str, int]
) -> go.Scatter3d:
    """Create a single trace for a relationship group with optimized performance.

    Args:
        rel_type: Type of relationship
        is_bidirectional: Whether relationships are bidirectional
        relationships: List of relationship dictionaries
        positions: NumPy array of node positions
        asset_id_index: Dictionary mapping asset_id to index for O(1) lookup

    Returns:
        Plotly Scatter3d trace object
    """
    edges_x, edges_y, edges_z = _build_edge_coordinates_optimized(relationships, positions, asset_id_index)
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
    graph: AssetRelationshipGraph,
    positions: np.ndarray,
    asset_ids: List[str],
    relationship_filters: Optional[Dict[str, bool]] = None,
) -> List[go.Scatter3d]:
    """Create separate traces for different types of relationships with enhanced visibility.

    Optimized for performance with large volumes of relationships by:
    - Using O(1) asset ID lookups via dictionary index
    - Pre-allocating arrays instead of using extend()
    - Single-pass collection and grouping of relationships
    - Efficient set-based bidirectional relationship detection

    Args:
        graph: The asset relationship graph
        positions: Node positions array
        asset_ids: List of asset IDs
        relationship_filters: Optional dict to filter relationship types

    Returns:
        List of Scatter3d traces for relationships
    """
    # Build asset ID index once for O(1) lookups throughout processing
    asset_id_index = _build_asset_id_index(asset_ids)

    # Collect and group relationships in a single pass
    relationship_groups = _collect_and_group_relationships(graph, asset_ids, relationship_filters)

    traces: List[go.Scatter3d] = []
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        if relationships:
            trace = _create_trace_for_group(rel_type, is_bidirectional, relationships, positions, asset_id_index)
            traces.append(trace)

    return traces


def _create_directional_arrows(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create arrow markers for unidirectional relationships.

    Uses a pre-built relationship set for O(1) reverse relationship lookups
    and asset ID index for O(1) position lookups.
    """
    # Build relationship set and indices once for O(1) lookups
    asset_ids_set = set(asset_ids)
    relationship_set = _build_relationship_set(graph, asset_ids)
    asset_id_index = _build_asset_id_index(asset_ids)

    arrows: List[dict] = []

    # Find unidirectional relationships
    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids_set:
            continue

        for target_id, rel_type, _ in rels:
            if target_id not in asset_ids_set:
                continue

            # Check if this is truly unidirectional using O(1) lookup
            if (target_id, source_id, rel_type) not in relationship_set:
                # O(1) lookup instead of O(n) list.index()
                source_idx = asset_id_index[source_id]
                target_idx = asset_id_index[target_id]

                # Calculate arrow position (70% along the edge towards target)
                arrow_pos = positions[source_idx] + 0.7 * (positions[target_idx] - positions[source_idx])

                arrows.append({
                    "pos": arrow_pos,
                    "hover": f"Direction: {source_id} → {target_id}<br>Type: {rel_type}",
                    "rel_type": rel_type,
                })

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
    relationship_traces = _create_relationship_traces(graph, positions, asset_ids, relationship_filters)

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
