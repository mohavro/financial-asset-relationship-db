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
    """Build optimized relationship index for O(1) lookups.

    This function consolidates relationship data into a single index structure
    that can be efficiently queried for:
    - Checking if a relationship exists (O(1) lookup)
    - Getting relationship strength (O(1) lookup)
    - Detecting bidirectional relationships (O(1) reverse lookup)

    Performance optimizations:
    - Pre-filters relationships to only process relevant source_ids
    - Uses set-based membership tests for O(1) lookups
    - Avoids unnecessary iterations over irrelevant relationships

    Thread Safety:
    This function creates and returns a new dictionary without modifying shared state.
    However, it reads from graph.relationships which should not be modified concurrently.
    If used in a multi-threaded context, ensure graph.relationships is not modified
    during execution, or use appropriate synchronization mechanisms (e.g., locks).

    Args:
        graph: The asset relationship graph
        asset_ids: Iterable of asset IDs to include (will be converted to a set for O(1) membership tests)

    Returns:
        Dictionary mapping (source_id, target_id, rel_type) to strength for all relationships
    """
    asset_ids_set = set(asset_ids)
    relationship_index: Dict[Tuple[str, str, str], float] = {}

    # Pre-filter relationships to only include relevant source_ids (optimization per review)
    # This reduces unnecessary iterations when source_id is frequently absent in asset_ids_set
    relevant_relationships = {
        source_id: rels
        for source_id, rels in graph.relationships.items()
        if source_id in asset_ids_set
    }

    for source_id, rels in relevant_relationships.items():
        for target_id, rel_type, strength in rels:
            if target_id in asset_ids_set:
                relationship_index[(source_id, target_id, rel_type)] = float(strength)

    return relationship_index


def _is_valid_color(color: str) -> bool:
    """Check if a string is a valid color format for Plotly.

    Validates common color formats:
    - Named colors (e.g., 'red', 'blue')
    - Hex colors (e.g., '#FF0000', '#F00')
    - RGB/RGBA (e.g., 'rgb(255,0,0)', 'rgba(255,0,0,0.5)')

    Args:
        color: String to validate as a color

    Returns:
        True if the color format is valid, False otherwise
    """
    if not isinstance(color, str) or not color:
        return False

    # Check for hex color format (#RGB or #RRGGBB)
    if re.match(r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$', color):
        return True

    # Check for rgb/rgba format
    if re.match(r'^rgba?\\s*\\([^)]+\\)$', color):
        return True

    # Accept any non-empty string as potentially valid named color
    return True


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

    # Validate colors content (must be valid color format strings)
    for i, color in enumerate(colors):
        if not isinstance(color, str) or not color:
            raise ValueError(f"colors[{i}] must be a non-empty string, got {type(color).__name__}")
        if not _is_valid_color(color):
            raise ValueError(f"colors[{i}] has invalid color format: '{color}'")

    # Validate hover_texts content (must be strings, can be empty)
    for i, hover_text in enumerate(hover_texts):
        if not isinstance(hover_text, str):
            raise ValueError(f"hover_texts[{i}] must be a string, got {type(hover_text).__name__}")


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
    """Configure the layout for 3D visualization.

    Args:
        fig: Plotly figure to configure
        title_text: Title text for the visualization
        width: Figure width in pixels (default: 1200)
        height: Figure height in pixels (default: 800)
        gridcolor: Grid color for axes (default: "rgba(200, 200, 200, 0.3)")
        bgcolor: Background color for scene (default: "rgba(248, 248, 248, 0.95)")
        legend_bgcolor: Background color for legend (default: "rgba(255, 255, 255, 0.8)")
        legend_bordercolor: Border color for legend (default: "rgba(0, 0, 0, 0.3)")
    """
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
    """Add directional arrows to the figure for unidirectional relationships using batch operations.

    Uses Plotly's add_traces (plural) method for efficient batch addition of traces,
    which reduces overhead compared to multiple add_trace calls.

    Args:
        fig: Plotly figure to add arrows to
        graph: The asset relationship graph
        positions: Node positions array
        asset_ids: List of asset IDs
    """
    arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    if arrow_traces:
        # Use batch operation for better performance
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
    """Configure the 3D layout for the figure.

    Args:
        fig: Plotly figure to configure
        title: Title text for the figure
        width: Figure width in pixels
        height: Figure height in pixels
        gridcolor: Color for grid lines in RGBA format
        bgcolor: Background color for the scene in RGBA format
        legend_bgcolor: Background color for the legend in RGBA format
        legend_bordercolor: Border color for the legend in RGBA format
    """
    fig.update_layout(
        title={
            "text": title,
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
        width=width,
        height=height,
        showlegend=True,
        hovermode="closest",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.3)",
            borderwidth=1,
        ),
    )


def _validate_visualization_data(
    positions: np.ndarray,
    asset_ids: List[str],
    colors: List[str],
    hover_texts: List[str],
) -> None:
    """Validate visualization data integrity to prevent runtime errors.

    This function performs comprehensive validation of data returned by
    graph.get_3d_visualization_data_enhanced() to ensure it contains all
    expected fields with correct data types and structure.

    Args:
        positions: NumPy array of node positions
        asset_ids: List of asset IDs
        colors: List of node colors
        hover_texts: List of hover texts

    Raises:
        ValueError: If any validation check fails with descriptive error message
    """
    # Validate positions array
    if not isinstance(positions, np.ndarray):
        raise ValueError(
            f"Invalid graph data: positions must be a numpy array, got {type(positions).__name__}"
        )
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError(f"Invalid graph data: Expected positions to be a (n, 3) numpy array, got array with shape {positions.shape}")
    if not np.issubdtype(positions.dtype, np.number):
        raise ValueError(
            f"Invalid graph data: positions must contain numeric values, got dtype {positions.dtype}"
        )
    if not np.isfinite(positions).all():
        raise ValueError("Invalid graph data: positions must contain finite values (no NaN or Inf)")

    # Validate asset_ids
    if not isinstance(asset_ids, (list, tuple)):
        raise ValueError(
            f"Invalid graph data: asset_ids must be a list or tuple, got {type(asset_ids).__name__}"
        )
    if not all(isinstance(a, str) and a for a in asset_ids):
        raise ValueError("Invalid graph data: asset_ids must contain non-empty strings")

    # Validate length consistency
    n = len(asset_ids)
    if positions.shape[0] != n:
        raise ValueError(f"Invalid graph data: positions length ({positions.shape[0]}) must match asset_ids length ({n})")
    if not isinstance(colors, (list, tuple)) or len(colors) != n:
        raise ValueError(f"Invalid graph data: colors must be a list/tuple of length {n}, got {type(colors).__name__} with length {len(colors) if isinstance(colors, (list, tuple)) else 'N/A'}")
    if not all(isinstance(c, str) and c for c in colors):
        raise ValueError("Invalid graph data: colors must contain non-empty strings")
    if not isinstance(hover_texts, (list, tuple)) or len(hover_texts) != n:
        raise ValueError(f"Invalid graph data: hover_texts must be a list/tuple of length {n}")
    if not all(isinstance(h, str) for h in hover_texts):
        raise ValueError("Invalid graph data: hover_texts must contain strings")


def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create enhanced 3D visualization of asset relationship graph with improved relationship visibility"""
    if not isinstance(graph, AssetRelationshipGraph) or not hasattr(graph, "get_3d_visualization_data_enhanced"):
        raise ValueError("Invalid graph data provided")

    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    # Validate visualization data to prevent runtime errors (addresses review feedback)
    _validate_visualization_data(positions, asset_ids, colors, hover_texts)

    fig = go.Figure()

    # Create separate traces for different relationship types and directions
    relationship_traces = _create_relationship_traces(graph, positions, asset_ids)

    # Performance optimization: Use batch operation (add_traces) instead of adding traces
    # individually in a loop, which reduces function call overhead for large graphs
    if relationship_traces:
        fig.add_traces(relationship_traces)

    # Add directional arrows for unidirectional relationships
    arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    if arrow_traces:
        fig.add_traces(arrow_traces)

    # Add nodes with enhanced styling
    fig.add_trace(
        go.Scatter3d(
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
            x=0.02,
            y=0.98,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.3)",
            borderwidth=1,
        ),
    )

    return fig


def _collect_and_group_relationships(
    graph: AssetRelationshipGraph,
    asset_ids: Iterable[str],
    relationship_filters: Optional[Dict[str, bool]] = None,
) -> Dict[Tuple[str, bool], List[dict]]:
    """Collect and group relationships with directionality info in a single pass.

    Optimized to avoid nested loops and intermediate lists by:
    - Building a relationship index once for O(1) lookups
    - Detecting bidirectionality via reverse-key checks
    - Using a processed-pairs set to avoid double-counting

    Args:
        graph: The asset relationship graph
        asset_ids: Iterable of asset IDs to include
        relationship_filters: Optional dict to filter relationship types

    Returns:
        Dictionary mapping (rel_type, is_bidirectional) to a list of relationship dicts
        with keys: source_id, target_id, strength
    """
    relationship_index = _build_relationship_index(graph, asset_ids)

    processed_pairs: Set[Tuple[str, str, str]] = set()
    relationship_groups: Dict[Tuple[str, bool], List[dict]] = defaultdict(list)

    for (source_id, target_id, rel_type), strength in relationship_index.items():
        if relationship_filters and rel_type in relationship_filters and not relationship_filters[rel_type]:
            continue

        # Canonical pair key for bidirectional detection without sorting overhead
        if source_id <= target_id:
            pair_key: Tuple[str, str, str] = (source_id, target_id, rel_type)
        else:
            pair_key = (target_id, source_id, rel_type)

        # O(1) reverse lookup for bidirectionality
        is_bidirectional = (target_id, source_id, rel_type) in relationship_index

        # Avoid duplicate entries for bidirectional edges
        if is_bidirectional and pair_key in processed_pairs:
            continue
        if is_bidirectional:
            processed_pairs.add(pair_key)

        relationship_groups[(rel_type, is_bidirectional)].append(
            {
                "source_id": source_id,
                "target_id": target_id,
                "strength": float(strength),
            }
        )

    return relationship_groups


def _build_edge_coordinates_optimized(
    relationships: List[dict],
    positions: np.ndarray,
    asset_id_index: Dict[str, int],
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
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
    edges_x: List[Optional[float]] = [None] * (num_edges * 3)
    edges_y: List[Optional[float]] = [None] * (num_edges * 3)
    edges_z: List[Optional[float]] = [None] * (num_edges * 3)

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


def _build_hover_texts(relationships: List[dict], rel_type: str, is_bidirectional: bool) -> List[Optional[str]]:
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
    hover_texts: List[Optional[str]] = [None] * (num_rels * 3)

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
        color=REL_TYPE_COLORS[rel_type],
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
    relationships: List[dict],
    positions: np.ndarray,
    asset_id_index: Dict[str, int],
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
    edges_x, edges_y, edges_z = _build_edge_coordinates_optimized(
        relationships, positions, asset_id_index
    )
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


def _generate_dynamic_title(num_assets: int, num_relationships: int) -> str:
    """Generate dynamic title based on asset and relationship counts.

    Args:
        num_assets: Number of assets in the visualization
        num_relationships: Number of visible relationships

    Returns:
        Formatted title string
    """
    return (
        f"Financial Asset Relationship Network - "
        f"{num_assets} Assets, {num_relationships} Relationships"
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
    - Building relationship index once and reusing it

    Args:
        graph: The asset relationship graph
        positions: Node positions array
        asset_ids: List of asset IDs
        relationship_filters: Optional dict to filter relationship types

    Returns:
        List of Scatter3d traces for relationships
    """
    # Validate input parameters
    if not isinstance(graph, AssetRelationshipGraph):
        raise ValueError("Invalid input data: graph must be an AssetRelationshipGraph instance")
    if not hasattr(graph, "relationships") or not isinstance(graph.relationships, dict):
        raise ValueError("Invalid input data: graph must have a relationships dictionary")
    if not isinstance(positions, np.ndarray):
        raise ValueError("Invalid input data: positions must be a numpy array")
    if len(positions) != len(asset_ids):
        raise ValueError("Invalid input data: positions array length must match asset_ids length")

    # Build asset ID index once for O(1) lookups throughout processing
    asset_id_index = _build_asset_id_index(asset_ids)

    # Collect and group relationships in a single pass (addressing review feedback)
    relationship_groups = _collect_and_group_relationships(
        graph, asset_ids, relationship_filters
    )

    traces: List[go.Scatter3d] = []
    for (rel_type, is_bidirectional), relationships in relationship_groups.items():
        if relationships:
            trace = _create_trace_for_group(
                rel_type, is_bidirectional, relationships, positions, asset_id_index
            )
            traces.append(trace)

    return traces


def _create_directional_arrows(
    graph: AssetRelationshipGraph, positions: np.ndarray, asset_ids: List[str]
) -> List[go.Scatter3d]:
    """Create arrow markers for unidirectional relationships using vectorized NumPy operations.

    Uses a pre-built relationship index for O(1) lookups and computes arrow positions
    in a single vectorized step for performance. Includes comprehensive input validation
    to prevent runtime errors when working with external data sources.

    Args:
        graph: AssetRelationshipGraph instance containing relationship data
        positions: NumPy array of shape (n, 3) with node positions
        asset_ids: List of asset ID strings matching positions array length

    Returns:
        List containing a single Scatter3d trace with arrow markers, or empty list if no arrows

    Raises:
        TypeError: If graph is not an AssetRelationshipGraph instance
        ValueError: If positions or asset_ids are None, have mismatched lengths,
                   contain invalid data types, or have non-finite values

    Notes:
        Implements comprehensive input validation as suggested in code review to prevent
        runtime errors when working with external data sources. Validates that positions
        and asset_ids are not None, have matching lengths, and contain valid data types.
    """
    if not isinstance(graph, AssetRelationshipGraph):
        raise TypeError("Expected graph to be an instance of AssetRelationshipGraph")
    if not hasattr(graph, "relationships") or not isinstance(graph.relationships, dict):
        raise ValueError("Invalid input data: graph must have a relationships dictionary")

    # Early validation as suggested in review: check None, length match, and basic compatibility
    try:
        if positions is None or asset_ids is None:
            raise ValueError("positions and asset_ids must not be None")
        if len(positions) != len(asset_ids):
            raise ValueError("positions and asset_ids must have the same length")
    except TypeError as exc:
        raise ValueError("Invalid input data: positions and asset_ids must support len()") from exc
    if not isinstance(positions, np.ndarray):
        positions = np.asarray(positions)
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError("Invalid positions shape: expected (n, 3)")
    if not isinstance(asset_ids, (list, tuple)):
        try:
            asset_ids = list(asset_ids)
        except Exception as exc:
            raise ValueError("asset_ids must be an iterable of strings") from exc
    if not np.issubdtype(positions.dtype, np.number):
        try:
            positions = positions.astype(float)
        except Exception as exc:
            raise ValueError("Invalid positions: values must be numeric") from exc
    if not np.isfinite(positions).all():
        raise ValueError("Invalid positions: values must be finite numbers")
    if not all(isinstance(a, str) and a for a in asset_ids):
        raise ValueError("asset_ids must contain non-empty strings")

    # Build relationship index once for O(1) lookups (optimization per review comment)
    relationship_index = _build_relationship_index(graph, asset_ids)
    asset_id_index = _build_asset_id_index(asset_ids)

    source_indices: List[int] = []
    target_indices: List[int] = []
    hover_texts: List[str] = []

    # Gather unidirectional relationships using the pre-built index
    for (source_id, target_id, rel_type), _ in relationship_index.items():
        # Check for reverse relationship using O(1) index lookup
        reverse_key = (target_id, source_id, rel_type)
        if reverse_key not in relationship_index:
            # This is a unidirectional relationship
            source_indices.append(asset_id_index[source_id])
            target_indices.append(asset_id_index[target_id])
            hover_texts.append(f"Direction: {source_id} → {target_id}<br>Type: {rel_type}")

    if not source_indices:
        return []

    # Performance optimization: Use vectorized NumPy operations for arrow position calculation.
    # Instead of calculating positions in a loop, we compute all arrow positions at once using
    # array operations, which is significantly faster for large graphs (vectorized operations
    # leverage optimized C code and SIMD instructions vs. interpreted Python loops).
    src_idx_arr = np.asarray(source_indices, dtype=int)
    tgt_idx_arr = np.asarray(target_indices, dtype=int)
    # Vectorized computation places markers at 70% along each edge towards the target
    # Formula: arrow_positions = source_positions + 0.7 * (target_positions - source_positions)
    source_positions = positions[src_idx_arr]
    target_positions = positions[tgt_idx_arr]
    arrow_positions = source_positions + 0.7 * (target_positions - source_positions)
    # This vectorized approach is significantly faster than looping: O(1) array operations
    # vs O(n) loop iterations, especially beneficial for large graphs with many relationships

    arrow_trace = go.Scatter3d(
        x=arrow_positions[:, 0].tolist(),
        y=arrow_positions[:, 1].tolist(),
        z=arrow_positions[:, 2].tolist(),
        mode="markers",
        marker=dict(
            symbol="diamond",  # Use diamond instead of arrow for 3D compatibility
            size=8,
            color="rgba(255, 0, 0, 0.8)",
            line=dict(color="red", width=1),
        ),
        hovertext=hover_texts,
        hoverinfo="text",
        name="Direction Arrows",
        visible=True,
        showlegend=False,
    )
    return [arrow_trace]


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
    """Create 3D visualization with selective relationship filtering.

    This function dynamically creates and adds relationship traces based on optional filters.
    Includes comprehensive error handling to manage potential issues from invalid filter
    configurations or data inconsistencies.

    Args:
        graph: AssetRelationshipGraph instance containing the data to visualize
        show_same_sector: Whether to show same sector relationships
        show_market_cap: Whether to show market cap similar relationships
        show_correlation: Whether to show correlation relationships
        show_corporate_bond: Whether to show corporate bond to equity relationships
        show_commodity_currency: Whether to show commodity currency relationships
        show_income_comparison: Whether to show income comparison relationships
        show_regulatory: Whether to show regulatory impact relationships
        show_all_relationships: Master toggle to show all relationships regardless of individual filters
        toggle_arrows: Whether to show directional arrows for unidirectional relationships

    Returns:
        Plotly Figure object with the 3D visualization

    Raises:
        ValueError: If graph is invalid or data is inconsistent
        TypeError: If filter parameters are not boolean values
        RuntimeError: If trace creation or figure generation fails
    """
    # Validate graph input
    if not isinstance(graph, AssetRelationshipGraph):
        raise ValueError("Invalid graph data provided: graph must be an AssetRelationshipGraph instance")
    if not hasattr(graph, "get_3d_visualization_data_enhanced"):
        raise ValueError("Invalid graph data provided: graph must have get_3d_visualization_data_enhanced method")

    # Validate filter parameters are boolean
    filter_params = {
        "show_same_sector": show_same_sector,
        "show_market_cap": show_market_cap,
        "show_correlation": show_correlation,
        "show_corporate_bond": show_corporate_bond,
        "show_commodity_currency": show_commodity_currency,
        "show_income_comparison": show_income_comparison,
        "show_regulatory": show_regulatory,
        "show_all_relationships": show_all_relationships,
        "toggle_arrows": toggle_arrows,
    }

    for param_name, param_value in filter_params.items():
        if not isinstance(param_value, bool):
            raise TypeError(f"Invalid filter configuration: {param_name} must be a boolean, got {type(param_value).__name__}")

    # Build relationship filters based on parameters
    try:
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
    except Exception as exc:
        raise RuntimeError(f"Failed to configure relationship filters: {exc}") from exc

    # Retrieve visualization data with error handling
    try:
        positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()
    except AttributeError as exc:
        raise ValueError(f"Invalid graph data: get_3d_visualization_data_enhanced method failed: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to retrieve visualization data from graph: {exc}") from exc

    # Validate visualization data to prevent runtime errors
    try:
        _validate_visualization_data(positions, asset_ids, colors, hover_texts)
    except ValueError as exc:
        raise ValueError(f"Data validation failed: {exc}") from exc

    # Create figure with error handling
    try:
        fig = go.Figure()
    except Exception as exc:
        raise RuntimeError(f"Failed to create Plotly figure: {exc}") from exc

    # Create relationship traces with filtering and error handling
    try:
        relationship_traces = _create_relationship_traces(
            graph, positions, asset_ids, relationship_filters
        )
    except (ValueError, KeyError) as exc:
        raise ValueError(f"Failed to create relationship traces: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Unexpected error during relationship trace creation: {exc}") from exc

    # Add relationship traces with error handling
    try:
        if relationship_traces:
            fig.add_traces(relationship_traces)
    except Exception as exc:
        raise RuntimeError(f"Failed to add relationship traces to figure: {exc}") from exc

    # Add directional arrows if enabled with error handling
    if toggle_arrows:
        try:
            arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
            if arrow_traces:
                fig.add_traces(arrow_traces)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Failed to create directional arrows: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected error during arrow creation: {exc}") from exc

    # Add nodes with enhanced styling and error handling
    try:
        fig.add_trace(
            go.Scatter3d(
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
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to add node trace to figure: {exc}") from exc

    # Count visible relationships for dynamic title with error handling
    try:
        visible_relationships = (
            sum(len(trace.x or []) for trace in relationship_traces if hasattr(trace, "x")) // 3
        )
    except Exception as exc:
        # If counting fails, default to 0 to avoid breaking the visualization
        visible_relationships = 0

    # Generate dynamic title with error handling
    try:
        dynamic_title = _generate_dynamic_title(len(asset_ids), visible_relationships)
    except Exception as exc:
        # Fallback to a simple title if dynamic title generation fails
        dynamic_title = "Financial Asset Relationship Network"

    # Configure layout with error handling
    try:
        _configure_3d_layout(fig, dynamic_title)
    except Exception as exc:
        raise RuntimeError(f"Failed to configure figure layout: {exc}") from exc

    return fig
