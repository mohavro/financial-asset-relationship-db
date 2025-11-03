import plotly.graph_objects as go
import numpy as np
from typing import Tuple, List, Dict
from src.logic.asset_graph import AssetRelationshipGraph


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


def _create_relationship_traces(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create separate traces for different types of relationships with enhanced visibility"""
    traces = []

    # Track bidirectional relationships to avoid duplicates
    bidirectional_pairs = set()

    # Collect all relationships with their directionality info
    all_relationships = []

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            # Check if this is bidirectional
            is_bidirectional = False
            reverse_exists = False

            if target_id in graph.relationships:
                for reverse_target, reverse_rel_type, reverse_strength in graph.relationships[target_id]:
                    if reverse_target == source_id and reverse_rel_type == rel_type:
                        reverse_exists = True
                        break

            # Create a unique pair identifier
            pair_key = tuple(sorted([source_id, target_id]) + [rel_type])

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

    # Group relationships by type and directionality
    relationship_groups = {}

    for rel in all_relationships:
        # Skip if we already processed this bidirectional relationship
        if rel["is_bidirectional"] and rel["pair_key"] in bidirectional_pairs:
            bidirectional_pairs.discard(rel["pair_key"])  # Remove to prevent duplicate processing
        elif rel["is_bidirectional"]:
            continue  # Skip duplicate of bidirectional relationship

        group_key = (rel["rel_type"], rel["is_bidirectional"])
        if group_key not in relationship_groups:
            relationship_groups[group_key] = []
        relationship_groups[group_key].append(rel)

    # Color and style mapping for relationship types
    rel_type_colors = {
        "same_sector": "#FF6B6B",  # Red for sector relationships
        "market_cap_similar": "#4ECDC4",  # Teal for market cap
        "correlation": "#45B7D1",  # Blue for correlations
        "corporate_bond_to_equity": "#96CEB4",  # Green for corporate bonds
        "commodity_currency": "#FFEAA7",  # Yellow for commodity-currency
        "income_comparison": "#DDA0DD",  # Plum for income comparisons
        "regulatory_impact": "#FFA07A",  # Light salmon for regulatory
        "default": "#888888",  # Gray for others
    }

    # Create traces for each relationship group
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        edges_x, edges_y, edges_z = [], [], []
        hover_texts = []

        for rel in relationships:
            source_idx = asset_ids.index(rel["source_id"])
            target_idx = asset_ids.index(rel["target_id"])

            edges_x.extend([positions[source_idx, 0], positions[target_idx, 0], None])
            edges_y.extend([positions[source_idx, 1], positions[target_idx, 1], None])
            edges_z.extend([positions[source_idx, 2], positions[target_idx, 2], None])

            # Add hover information
            direction_text = "↔" if is_bidirectional else "→"
            hover_text = f"{rel['source_id']} {direction_text} {rel['target_id']}<br>Type: {rel_type}<br>Strength: {rel['strength']:.2f}"
            hover_texts.extend([hover_text, hover_text, None])

        if edges_x:  # Only create trace if there are edges
            color = rel_type_colors.get(rel_type, rel_type_colors["default"])
            line_width = 4 if is_bidirectional else 2
            line_dash = "solid" if is_bidirectional else "dash"

            trace_name = f"{rel_type.replace('_', ' ').title()}"
            if is_bidirectional:
                trace_name += " (↔)"
            else:
                trace_name += " (→)"

            trace = go.Scatter3d(
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
            traces.append(trace)

    return traces


def _create_directional_arrows(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create arrow markers for unidirectional relationships"""
    arrows = []

    # Find unidirectional relationships
    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            # Check if this is truly unidirectional
            is_unidirectional = True
            if target_id in graph.relationships:
                for reverse_target, reverse_rel_type, reverse_strength in graph.relationships[target_id]:
                    if reverse_target == source_id and reverse_rel_type == rel_type:
                        is_unidirectional = False
                        break

            if is_unidirectional:
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
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str], relationship_filters: dict = None
) -> List[go.Scatter3d]:
    """Create relationship traces with optional filtering"""
    traces = []

    if relationship_filters is None:
        # Show all relationships - use original logic
        return _create_relationship_traces(graph, positions, asset_ids)

    # Track bidirectional relationships to avoid duplicates
    bidirectional_pairs = set()

    # Collect all relationships with their directionality info
    all_relationships = []

    for source_id, rels in graph.relationships.items():
        if source_id not in asset_ids:
            continue

        for target_id, rel_type, strength in rels:
            if target_id not in asset_ids:
                continue

            # Skip if this relationship type is filtered out
            if rel_type in relationship_filters and not relationship_filters[rel_type]:
                continue

            # Check if this is bidirectional
            is_bidirectional = False
            reverse_exists = False

            if target_id in graph.relationships:
                for reverse_target, reverse_rel_type, reverse_strength in graph.relationships[target_id]:
                    if reverse_target == source_id and reverse_rel_type == rel_type:
                        reverse_exists = True
                        break

            # Create a unique pair identifier
            pair_key = tuple(sorted([source_id, target_id]) + [rel_type])

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

    # Group relationships by type and directionality
    relationship_groups = {}

    for rel in all_relationships:
        # Skip if we already processed this bidirectional relationship
        if rel["is_bidirectional"] and rel["pair_key"] in bidirectional_pairs:
            bidirectional_pairs.discard(rel["pair_key"])
        elif rel["is_bidirectional"]:
            continue

        group_key = (rel["rel_type"], rel["is_bidirectional"])
        if group_key not in relationship_groups:
            relationship_groups[group_key] = []
        relationship_groups[group_key].append(rel)

    # Color and style mapping for relationship types
    rel_type_colors = {
        "same_sector": "#FF6B6B",
        "market_cap_similar": "#4ECDC4",
        "correlation": "#45B7D1",
        "corporate_bond_to_equity": "#96CEB4",
        "commodity_currency": "#FFEAA7",
        "income_comparison": "#DDA0DD",
        "regulatory_impact": "#FFA07A",
        "default": "#888888",
    }

    # Create traces for each relationship group
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
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

        if edges_x:
            color = rel_type_colors.get(rel_type, rel_type_colors["default"])
            line_width = 4 if is_bidirectional else 2
            line_dash = "solid" if is_bidirectional else "dash"

            trace_name = f"{rel_type.replace('_', ' ').title()}"
            if is_bidirectional:
                trace_name += " (↔)"
            else:
                trace_name += " (→)"

            trace = go.Scatter3d(
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
            traces.append(trace)

    return traces
