import re
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

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

# Valid relationship types for filter validation
VALID_RELATIONSHIP_TYPES = {
    "same_sector",
    "market_cap_similar",
    "correlation",
    "corporate_bond_to_equity",
    "commodity_currency",
    "income_comparison",
    "regulatory_impact",
}


def _is_valid_color_format(color: str) -> bool:
    """Validate if a string is a valid color format for Plotly.

    Accepts hex colors (#RGB or #RRGGBB), rgb/rgba format, or named colors.

    Args:
        color: Color string to validate

    Returns:
        True if the color format is valid, False otherwise
    """
    if not isinstance(color, str) or not color:
        return False

    # Check for hex color format (#RGB or #RRGGBB or #RRGGBBAA)
    if re.match(r'^#(?:[0-9A-Fa-f]{3}){1,2}(?:[0-9A-Fa-f]{2})?$', color):
        return True

    # Check for rgb/rgba format
    if re.match(r'^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*[\d.]+\s*)?\)$', color):
        return True

    # Fallback: allow named colors; Plotly will validate at render time
    return True


def _validate_filter_configuration(relationship_filters: Optional[Dict[str, bool]]) -> None:
    """Validate relationship filter configuration.

    Args:
        relationship_filters: Dictionary mapping relationship types to boolean visibility flags

    Raises:
        ValueError: If filter configuration contains invalid relationship types or non-boolean values
    """
    if relationship_filters is None:
        return

    if not isinstance(relationship_filters, dict):
        raise ValueError("relationship_filters must be a dictionary")

    for rel_type, enabled in relationship_filters.items():
        if not isinstance(rel_type, str) or not rel_type:
            raise ValueError(f"Invalid relationship type in filters: {rel_type}")
        if rel_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(f"Unknown relationship type in filters: '{rel_type}'. Valid types: {VALID_RELATIONSHIP_TYPES}")
        if not isinstance(enabled, bool):
            raise ValueError(f"Filter value for '{rel_type}' must be boolean, got {type(enabled).__name__}")


def _build_asset_id_index(asset_ids: List[str]) -> Dict[str, int]:
    """Build O(1) lookup index for asset IDs to their positions.

    Args:
        asset_ids: List of asset IDs

    Returns:
        Dictionary mapping asset_id to its index in the list
    """
    return {asset_id: idx for idx, asset_id in enumerate(asset_ids)}


def _build_relationship_index(
    graph: AssetRelationshipGraph, asset_ids: Iterable[str]
) -> Dict[Tuple[str, str, str], float]:
    """Build optimized relationship index for O(1) lookups with pre-filtering.

    This function consolidates relationship data into a single index structure
    that can be efficiently queried for:
    - Checking if a relationship exists (O(1) lookup)
    - Getting relationship strength (O(1) lookup)
    - Detecting bidirectional relationships (O(1) reverse lookup)

    Performance optimizations (addressing review feedback):
    - Pre-filters graph.relationships to only include relevant source_ids
    - Uses set-based membership tests for O(1) lookups
    - Avoids unnecessary iterations over irrelevant relationships
    - Reduces continue statements by filtering upfront

    Thread Safety:
    - This function is thread-safe as it only reads from the input graph and
      creates a new local dictionary without modifying any shared state.
    - The returned dictionary is a new object.

    Args:
        graph: The asset relationship graph
        asset_ids: Iterable of asset IDs to include (will be converted to a set for O(1) membership tests)

    Returns:
        Dictionary mapping (source_id, target_id, rel_type) to strength for all relationships
    """
    asset_ids_set = set(asset_ids)

    # Snapshot and pre-filter relationships to include only relevant source_ids
    # Use list() to snapshot keys and tuple() to snapshot per-source relationship lists
    # This avoids issues if graph.relationships is mutated concurrently elsewhere.
    relevant_relationships = {
        source_id: tuple(rels)
        for source_id, rels in list(graph.relationships.items())
        if source_id in asset_ids_set
    }

    relationship_index: Dict[Tuple[str, str, str], float] = {}
    for source_id, rels in relevant_relationships.items():
        for target_id, rel_type, strength in rels:
            if target_id in asset_ids_set:
                relationship_index[(source_id, target_id, rel_type)] = float(strength)

    return relationship_index


def _create_node_trace(
    positions: np.ndarray,
    asset_ids: List[str],
    colors: List[str],
    hover_texts: List[str],
) -> go.Scatter3d:
    """Create node trace for 3D visualization.

    Args:
        positions: NumPy array of node positions with shape (n, 3) containing finite numeric values
        asset_ids: List of asset ID strings (must be non-empty strings, length must match positions)
        colors: List of node colors (length must match positions)
        hover_texts: List of hover texts (length must match positions)

    Returns:
        Plotly Scatter3d trace for nodes

    Raises:
        ValueError: If input parameters are invalid, have mismatched dimensions, or contain invalid data
    """
    # Validate positions array
    if not isinstance(positions, np.ndarray):
        raise ValueError("positions must be a NumPy array")
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError(f"positions must be a 2D array with 3 columns, got shape {positions.shape}")
    if not np.issubdtype(positions.dtype, np.number):
        raise ValueError("positions must contain numeric values")
    if not np.isfinite(positions).all():
        raise ValueError("positions must contain finite numeric values (no NaN or inf)")

    # Validate input lists
    if not isinstance(asset_ids, (list, tuple)):
        raise ValueError("asset_ids must be a list or tuple")
    if not isinstance(colors, (list, tuple)):
        raise ValueError("colors must be a list or tuple")
    if not isinstance(hover_texts, (list, tuple)):
        raise ValueError("hover_texts must be a list or tuple")

    # Validate asset_ids contains non-empty strings
    if not all(isinstance(aid, str) and aid for aid in asset_ids):
        raise ValueError("asset_ids must contain non-empty strings")

    # Validate colors content (must be valid color format strings)
    for i, color in enumerate(colors):
        if not isinstance(color, str) or not color:
            raise ValueError(f"colors[{i}] must be a non-empty string, got {type(color).__name__}")
        if not _is_valid_color_format(color):
            raise ValueError(f"colors[{i}] has invalid color format: '{color}'")

    # Validate hover_texts content (must be strings, can be empty)
    for i, hover_text in enumerate(hover_texts):
        if not isinstance(hover_text, str):
            raise ValueError(f"hover_texts[{i}] must be a string, got {type(hover_text).__name__}")

    # Validate length alignment
    n_positions = positions.shape[0]
    n_asset_ids = len(asset_ids)
    n_colors = len(colors)
    n_hover_texts = len(hover_texts)

    if not (n_positions == n_asset_ids == n_colors == n_hover_texts):
        raise ValueError(
            f"Length mismatch: positions has {n_positions} rows, "
            f"asset_ids has {n_asset_ids} elements, colors has {n_colors} elements, "
            f"hover_texts has {n_hover_texts} elements. All must have the same length."
        )

    return go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode="markers+text",
        marker=dict(
            size=15,
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


def _configure_layout(
    fig: go.Figure,
    title_text: str,
    width: int = 1200,
    height: int = 800,
    gridcolor: str = "rgba(200, 200, 200, 0.3)",
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)",
    legend_bordercolor: str = "rgba(0, 0, 0, 0.3)",
    bgcolor: str = "rgba(248, 248, 248, 0.95)",
) -> None:
    """Configure the layout for 3D visualization."""
    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=dict(
            xaxis=dict(title="Dimension 1", showgrid=True, gridcolor=gridcolor),
            yaxis=dict(title="Dimension 2", showgrid=True, gridcolor=gridcolor),
            zaxis=dict(title="Dimension 3", showgrid=True, gridcolor=gridcolor),
            bgcolor=bgcolor,
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        width=width,
        height=height,
        showlegend=True,
        hovermode="closest",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor=legend_bgcolor,
            bordercolor=legend_bordercolor,
            borderwidth=1,
        ),
    )


def _add_directional_arrows_to_figure(
    fig: go.Figure, graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> None:
    """Add directional arrows to the figure for unidirectional relationships using batch operations."""
    arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    if arrow_traces:
        fig.add_traces(arrow_traces)


def _configure_3d_layout(
    fig: go.Figure,
    title: str,
    width: int = 1200,
    height: int = 800,
    gridcolor: str = "rgba(200, 200, 200, 0.3)",
    bgcolor: str = "rgba(248, 248, 248, 0.95)",
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)",
    legend_bordercolor: str = "rgba(0, 0, 0, 0.3)",
) -> None:
    """Configure the 3D layout for the figure."""
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        scene=dict(
            xaxis=dict(title="Dimension 1", showgrid=True, gridcolor=gridcolor),
            yaxis=dict(title="Dimension 2", showgrid=True, gridcolor=gridcolor),
            zaxis=dict(title="Dimension 3", showgrid=True, gridcolor=gridcolor),
            bgcolor=bgcolor,
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        width=width,
        height=height,
        showlegend=True,
        hovermode="closest",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor=legend_bgcolor,
            bordercolor=legend_bordercolor,
            borderwidth=1,
        ),
    )
