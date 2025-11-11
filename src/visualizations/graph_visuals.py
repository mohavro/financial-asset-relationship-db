from typing import List

import numpy as np
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph

REL_TYPE_COLORS = {
    "same_sector": "#FF6B6B",
    "market_cap_similar": "#4ECDC4",
    "correlation": "#45B7D1",
    "corporate_bond_to_equity": "#96CEB4",
    "commodity_currency": "#FFEAA7",
    "income_comparison": "#DDA0DD",
    "regulatory_impact": "#FFA07A",
    "default": "#888888",
}


def _get_scene_config():
    """Get standard scene configuration for 3D plots"""
    return dict(
        xaxis=dict(title="Dimension 1", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
        yaxis=dict(title="Dimension 2", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
        zaxis=dict(title="Dimension 3", showgrid=True, gridcolor="rgba(200, 200, 200, 0.3)"),
        bgcolor="rgba(248, 248, 248, 0.95)",
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
    )


def _get_legend_config():
    """Get standard legend configuration"""
    return dict(
        x=0.02, y=0.98, bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="rgba(0, 0, 0, 0.3)", borderwidth=1
    )


def _get_node_marker_config(colors):
    """Get standard node marker configuration"""
    return dict(
        size=15,
        color=colors,
        opacity=0.9,
        line=dict(color="rgba(0,0,0,0.8)", width=2),
        symbol="circle",
    )


def _create_node_trace(positions, asset_ids, colors, hover_texts):
    """Create node trace for assets"""
    return go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode="markers+text",
        marker=_get_node_marker_config(colors),
        text=asset_ids,
        hovertext=hover_texts,
        hoverinfo="text",
        textposition="top center",
        textfont=dict(size=12, color="black"),
        name="Assets",
        visible=True,
    )


def _check_bidirectional_relationship(graph, source_id, target_id, rel_type):
    """Check if a relationship is bidirectional"""
    if target_id not in graph.relationships:
        return False

    for reverse_target, reverse_rel_type, _ in graph.relationships[target_id]:
        if reverse_target == source_id and reverse_rel_type == rel_type:
            return True
    return False


def _collect_relationships(graph, asset_ids, relationship_filters=None):
    """Collect and categorize all relationships"""
    bidirectional_pairs = set()
    all_relationships = []

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            if relationship_filters and rel_type in relationship_filters:
                if not relationship_filters[rel_type]:
                    continue

            reverse_exists = _check_bidirectional_relationship(graph, source_id, target_id, rel_type)
            pair_key = tuple(sorted([source_id, target_id]) + [rel_type])

            is_bidirectional = False
            if reverse_exists and pair_key not in bidirectional_pairs:
                is_bidirectional = True
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


def _group_relationships(all_relationships, bidirectional_pairs):
    """Group relationships by type and directionality"""
    relationship_groups = {}
    processed_pairs = set()

    for rel in all_relationships:
        if rel["is_bidirectional"] and rel["pair_key"] in bidirectional_pairs:
            if rel["pair_key"] in processed_pairs:
                continue
            processed_pairs.add(rel["pair_key"])
        elif rel["is_bidirectional"]:
            continue

        group_key = (rel["rel_type"], rel["is_bidirectional"])
        if group_key not in relationship_groups:
            relationship_groups[group_key] = []
        relationship_groups[group_key].append(rel)

    return relationship_groups


def _create_edge_trace(rel_type, is_bidirectional, relationships, positions, asset_ids):
    """Create a single edge trace for a group of relationships"""
    edges_x, edges_y, edges_z = [], [], []
    hover_texts = []

    for rel in relationships:
        source_idx = asset_ids.index(rel["source_id"])
        target_idx = asset_ids.index(rel["target_id"])

        edges_x.extend([positions[source_idx, 0], positions[target_idx, 0], None])
        edges_y.extend([positions[source_idx, 1], positions[target_idx, 1], None])
        edges_z.extend([positions[source_idx, 2], positions[target_idx, 2], None])

        direction_text = "↔" if is_bidirectional else "→"
        hover_text = f"{rel['source_id']} {direction_text} {rel['target_id']}<br>Type: {rel_type}<br>Strength: {rel['strength']:.2f}"
        hover_texts.extend([hover_text, hover_text, None])

    if not edges_x:
        return None

    color = REL_TYPE_COLORS.get(rel_type, REL_TYPE_COLORS["default"])
    line_width = 4 if is_bidirectional else 2
    line_dash = "solid" if is_bidirectional else "dash"

    trace_name = f"{rel_type.replace('_', ' ').title()}"
    trace_name += " (↔)" if is_bidirectional else " (→)"

    return go.Scatter3d(
        x=edges_x,
        y=edges_y,
        z=edges_z,
        mode="lines",
        line=dict(color=color, width=line_width, dash=line_dash),
        hovertext=hover_texts,
        hoverinfo="text",
        name=trace_name,
        visible=True,
        legendgroup=rel_type,
    )


def _create_relationship_traces(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str], relationship_filters=None
) -> List[go.Scatter3d]:
    """Create traces for relationships with optional filtering"""
    all_relationships, bidirectional_pairs = _collect_relationships(graph, asset_ids, relationship_filters)
    relationship_groups = _group_relationships(all_relationships, bidirectional_pairs)

    traces = []
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        trace = _create_edge_trace(rel_type, is_bidirectional, relationships, positions, asset_ids)
        if trace:
            traces.append(trace)

    return traces


def _create_directional_arrows(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create arrow markers for unidirectional relationships"""
    arrows = []

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, _ in rels:
            if target_id not in asset_ids:
                continue

            is_unidirectional = not _check_bidirectional_relationship(graph, source_id, target_id, rel_type)

            if is_unidirectional:
                source_idx = asset_ids.index(source_id)
                target_idx = asset_ids.index(target_id)

                arrow_pos = positions[source_idx] + 0.7 * (positions[target_idx] - positions[source_idx])

                arrows.append(
                    {
                        "pos": arrow_pos,
                        "hover": f"Direction: {source_id} → {target_id}<br>Type: {rel_type}",
                        "rel_type": rel_type,
                    }
                )

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
                symbol="diamond",
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


def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create enhanced 3D visualization of asset relationship graph with improved relationship visibility"""
    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    fig = go.Figure()

    relationship_traces = _create_relationship_traces(graph, positions, asset_ids)
    for trace in relationship_traces:
        fig.add_trace(trace)

    arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    for trace in arrow_traces:
        fig.add_trace(trace)

    fig.add_trace(_create_node_trace(positions, asset_ids, colors, hover_texts))

    fig.update_layout(
        title={
            "text": "Financial Asset Relationship Network - Enhanced 3D Visualization",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=_get_scene_config(),
        width=1200,
        height=800,
        showlegend=True,
        hovermode="closest",
        legend=_get_legend_config(),
    )

    return fig


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
        relationship_filters = None

    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    fig = go.Figure()

    relationship_traces = _create_relationship_traces(graph, positions, asset_ids, relationship_filters)
    for trace in relationship_traces:
        fig.add_trace(trace)

    if toggle_arrows:
        arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
        for trace in arrow_traces:
            fig.add_trace(trace)

    fig.add_trace(_create_node_trace(positions, asset_ids, colors, hover_texts))

    visible_relationships = sum(len(trace.x or []) for trace in relationship_traces if hasattr(trace, "x")) // 3

    fig.update_layout(
        title={
            "text": f"Financial Asset Network - {len(asset_ids)} Assets, {visible_relationships} Relationships",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=_get_scene_config(),
        width=1200,
        height=800,
        showlegend=True,
        hovermode="closest",
        legend=_get_legend_config(),
    )

    return fig
