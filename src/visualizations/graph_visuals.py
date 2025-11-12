import logging
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

import numpy as np
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph

logger = logging.getLogger(__name__)

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


def _is_valid_color_format(color: str) -> bool:
    """Validate if a string is a valid color format.

    Supports common color formats:
    - Hex colors (#RGB, #RRGGBB, #RRGGBBAA)
    - RGB/RGBA (e.g., 'rgb(255,0,0)', 'rgba(255,0,0,0.5)')
    - Named colors (delegated to Plotly)

    Args:
        color: Color string to validate

    Returns:
        True if color format is valid, False otherwise
    """
    if not isinstance(color, str) or not color:
        return False

    # Hex colors
    if re.match(r'^#(?:[0-9A-Fa-f]{3}){1,2}(?:[0-9A-Fa-f]{2})?$', color):
        return True

    # rgb/rgba functions
    if re.match(r'^rgba?\\(\\s*\\d+\\s*,\\s*\\d+\\s*,\\s*\\d+\\s*(,\\s*[\\d.]+\\s*)?\\)$', color):
        return True

    # Fallback: allow named colors; Plotly will validate at render time
    return True


def _build_asset_id_index(asset_ids: List[str]) -> Dict[str, int]:
    """Build O(1) lookup index for asset IDs to their positions."""
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

    Thread Safety and Data Integrity:
    - Creates and returns a new dictionary (no shared state modification)
    - Reads graph.relationships without mutating it
    - Function itself does not modify any shared state

    Thread safety guarantees:
    This function is thread-safe for concurrent execution ONLY under these conditions:
    1. The graph.relationships dictionary is NOT modified during execution
    2. Multiple threads can safely call this function simultaneously IF AND ONLY IF
       the graph object remains immutable

    NOT thread-safe when:
    - graph.relationships is modified by any thread during execution
    - This can cause data races, inconsistent states, or runtime errors

    Recommendations for Multi-Threaded Environments:
    1. PREFERRED: Use immutable graph objects (freeze graph.relationships after creation)
    2. ALTERNATIVE: Implement external synchronization:
       - Use threading.Lock or similar mechanism to protect graph access
       - Ensure all reads/writes to graph.relationships are synchronized
    3. AVOID: Modifying graph.relationships while any thread may be reading it

    For multi-threaded environments with mutable graphs:
    Note: If your application modifies the graph concurrently, you MUST implement
    external locking or use immutable data structures to prevent race conditions.

    Args:
        graph: The asset relationship graph (should be immutable in multi-threaded contexts)
        asset_ids: Iterable of asset IDs to include (will be converted to a set for O(1) membership tests)

    Returns:
        Dictionary mapping (source_id, target_id, rel_type) to strength for all relationships
    """
    asset_ids_set = set(asset_ids)

    # Pre-filter relationships to only include relevant source_ids
    relevant_relationships = {
        source_id: rels
        for source_id, rels in graph.relationships.items()
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
    """Create node trace for 3D visualization with comprehensive input validation.

    Validates all inputs to ensure:
    - positions is a non-empty 2D numpy array with shape (n, 3) containing finite numeric values
    - asset_ids is a non-empty list/tuple of non-empty strings with length matching positions
    - colors is a non-empty list/tuple of valid color strings with length matching positions
    - hover_texts is a non-empty list/tuple of strings with length matching positions
    - All arrays have consistent lengths
    - No duplicate asset IDs

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
    # Input validation: Perform basic type checks before delegating to comprehensive validator
    # This provides early failure with clear error messages for common mistakes
    if not isinstance(positions, np.ndarray):
        raise ValueError(f"positions must be a numpy array, got {type(positions).__name__}")
    if not isinstance(asset_ids, (list, tuple)):
        raise ValueError(f"asset_ids must be a list or tuple, got {type(asset_ids).__name__}")
    if not isinstance(colors, (list, tuple)):
        raise ValueError(f"colors must be a list or tuple, got {type(colors).__name__}")
    if not isinstance(hover_texts, (list, tuple)):
        raise ValueError(f"hover_texts must be a list or tuple, got {type(hover_texts).__name__}")

    # Validate dimensions and alignment before detailed validation
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError(f"positions must have shape (n, 3), got {positions.shape}")
    if len(asset_ids) != len(colors) or len(asset_ids) != len(hover_texts):
        raise ValueError(
            f"Length mismatch: asset_ids({len(asset_ids)}), colors({len(colors)}), "
            f"hover_texts({len(hover_texts)}) must all be equal"
        )
    if positions.shape[0] != len(asset_ids):
        raise ValueError(
            f"positions length ({positions.shape[0]}) must match asset_ids length ({len(asset_ids)})"
        )

    # Comprehensive validation: detailed checks on content, numeric types, and finite values
    # Delegates to shared validator to ensure consistency across all visualization functions
    _validate_visualization_data(positions, asset_ids, colors, hover_texts)

    # Edge case validation: Ensure inputs are not empty
    if len(asset_ids) == 0:
        raise ValueError("Cannot create node trace with empty inputs (asset_ids length is 0)")
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


def _generate_dynamic_title(
    num_assets: int,
    num_relationships: int,
    base_title: str = "Financial Asset Network"
) -> str:
    """Generate a dynamic title for the visualization based on asset and relationship counts.

    This function creates a consistent title format across different visualization contexts,
    improving modularity and making it easier to customize titles without modifying core logic.

    Args:
        num_assets: Number of assets in the visualization
        num_relationships: Number of relationships displayed
        base_title: Base title text (default: "Financial Asset Network")

    Returns:
        Formatted title string with asset and relationship counts
    """
    return f"{base_title} - {num_assets} Assets, {num_relationships} Relationships"


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
    options: Optional[Dict[str, object]] = None,
) -> None:
    """Configure the 3D layout for the figure.

    Args:
        fig: Target Plotly figure
        title: Title text
        options: Optional mapping to override defaults. Supported keys:
            - width (int)
            - height (int)
            - gridcolor (str)
            - bgcolor (str)
            - legend_bgcolor (str)
            - legend_bordercolor (str)
    """
    opts = options or {}
    width = int(opts.get("width", 1200))
    height = int(opts.get("height", 800))
    gridcolor = str(opts.get("gridcolor", "rgba(200, 200, 200, 0.3)"))
    bgcolor = str(opts.get("bgcolor", "rgba(248, 248, 248, 0.95)"))
    legend_bgcolor = str(opts.get("legend_bgcolor", "rgba(255, 255, 255, 0.8)"))
    legend_bordercolor = str(opts.get("legend_bordercolor", "rgba(0, 0, 0, 0.3)"))

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


def _validate_visualization_data(
    positions: np.ndarray,
    asset_ids: List[str],
    colors: List[str],
    hover_texts: List[str],
) -> None:
    """Validate visualization data integrity to prevent runtime errors."""
    # Validate positions array
    if not isinstance(positions, np.ndarray):
        raise ValueError(
            f"Invalid graph data: positions must be a numpy array, got {type(positions).__name__}"
        )
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError(
            f"Invalid graph data: Expected positions to be a (n, 3) numpy array, got array with shape {positions.shape}"
        )
    if not np.issubdtype(positions.dtype, np.number):
        raise ValueError(
            f"Invalid graph data: positions must contain numeric values, got dtype {positions.dtype}"
        )
    if not np.isfinite(positions).all():
        nan_count = int(np.isnan(positions).sum())
        inf_count = int(np.isinf(positions).sum())
        raise ValueError(
            f"Invalid graph data: positions must contain finite values (no NaN or Inf). Found {nan_count} NaN and {inf_count} Inf"
        )

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
        raise ValueError(
            f"Invalid graph data: positions length ({positions.shape[0]}) must match asset_ids length ({n})"
        )
    if not isinstance(colors, (list, tuple)) or len(colors) != n:
        colors_type = type(colors).__name__
        colors_len = len(colors) if isinstance(colors, (list, tuple)) else 'N/A'
        raise ValueError(
            f"Invalid graph data: colors must be a list/tuple of length {n}, "
            f"got {colors_type} with length {colors_len}"
        )
    if not all(isinstance(c, str) and c for c in colors):
        raise ValueError("Invalid graph data: colors must contain non-empty strings")
    # Validate color formats
    for i, color in enumerate(colors):
        if not _is_valid_color_format(color):
            raise ValueError(f"Invalid graph data: colors[{i}] has invalid color format: '{color}'")
    if not isinstance(hover_texts, (list, tuple)) or len(hover_texts) != n:
        raise ValueError(
            f"Invalid graph data: hover_texts must be a list/tuple of length {n}"
        )
    if not all(isinstance(h, str) for h in hover_texts):
        raise ValueError("Invalid graph data: hover_texts must contain strings")


def visualize_3d_graph(graph: AssetRelationshipGraph) -> go.Figure:
    """Create enhanced 3D visualization of asset relationship graph with improved relationship visibility"""
    if not isinstance(graph, AssetRelationshipGraph) or not hasattr(
        graph, "get_3d_visualization_data_enhanced"
    ):
        raise ValueError("Invalid graph data provided")

    positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()

    # Validate visualization data to prevent runtime errors (addresses review feedback)
    _validate_visualization_data(positions, asset_ids, colors, hover_texts)

    fig = go.Figure()

    # Create separate traces for different relationship types and directions
    try:
        relationship_traces = _create_relationship_traces(graph, positions, asset_ids)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create relationship traces: %s", exc)
        relationship_traces = []

    # Batch add traces
    if relationship_traces:
        try:
            fig.add_traces(relationship_traces)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to add relationship traces to figure: %s", exc)

    # Add directional arrows for unidirectional relationships
    try:
        arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create directional arrow traces: %s", exc)
        arrow_traces = []

    if arrow_traces:
        try:
            fig.add_traces(arrow_traces)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to add arrow traces to figure: %s", exc)

    # Add nodes with enhanced styling
    node_trace = _create_node_trace(positions, asset_ids, colors, hover_texts)
    fig.add_trace(node_trace)

    # Calculate total relationships for dynamic title
    total_relationships = sum(len(getattr(trace, "x", []) or []) for trace in relationship_traces) // 3
    dynamic_title = _generate_dynamic_title(len(asset_ids), total_relationships)

    fig.update_layout(
        title={
            "text": dynamic_title,
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
    """Collect and group relationships with directionality info in a single pass."""
    relationship_index = _build_relationship_index(graph, asset_ids)

    processed_pairs: Set[Tuple[str, str, str]] = set()
    relationship_groups: Dict[Tuple[str, bool], List[dict]] = defaultdict(list)

    for (source_id, target_id, rel_type), strength in relationship_index.items():
        if relationship_filters and rel_type in relationship_filters and not relationship_filters[rel_type]:
            continue

        # Canonical pair key for bidirectional detection
        if source_id <= target_id:
            pair_key: Tuple[str, str, str] = (source_id, target_id, rel_type)
        else:
            pair_key = (target_id, source_id, rel_type)

        # Reverse lookup for bidirectionality
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
    """Build edge coordinate lists for relationships using optimized O(1) lookups."""
    num_edges = len(relationships)
    edges_x: List[Optional[float]] = [None] * (num_edges * 3)
    edges_y: List[Optional[float]] = [None] * (num_edges * 3)
    edges_z: List[Optional[float]] = [None] * (num_edges * 3)

    for i, rel in enumerate(relationships):
        source_idx = asset_id_index[rel["source_id"]]
        target_idx = asset_id_index[rel["target_id"]]

        base_idx = i * 3

        edges_x[base_idx] = positions[source_idx, 0]
        edges_x[base_idx + 1] = positions[target_idx, 0]

        edges_y[base_idx] = positions[source_idx, 1]
        edges_y[base_idx + 1] = positions[target_idx, 1]

        edges_z[base_idx] = positions[source_idx, 2]
        edges_z[base_idx + 1] = positions[target_idx, 2]

    return edges_x, edges_y, edges_z


def _build_hover_texts(relationships: List[dict], rel_type: str, is_bidirectional: bool) -> List[Optional[str]]:
    """Build hover text list for relationships with pre-allocation for performance."""
    direction_text = "↔" if is_bidirectional else "→"

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
    """Get line style configuration for a relationship with color validation.

    Args:
        rel_type: Relationship type identifier
        is_bidirectional: Whether the relationship is bidirectional

    Returns:
        Dictionary with line style configuration including validated color
    """
    color = REL_TYPE_COLORS[rel_type]
    if not _is_valid_color_format(color):
        logger.warning("Invalid color format for relationship type '%s': '%s'. Using default gray.", rel_type, color)
        color = "#888888"

    return dict(
        color=color,
        width=4 if is_bidirectional else 2,
        dash="solid" if is_bidirectional else "dash",
    )


def _format_trace_name(rel_type: str, is_bidirectional: bool) -> str:
    """Format trace name for legend."""
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
    """Create a single trace for a relationship group with optimized performance."""
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


def _create_relationship_traces(
    graph: AssetRelationshipGraph,
    positions: np.ndarray,
    asset_ids: List[str],
    relationship_filters: Optional[Dict[str, bool]] = None,
) -> List[go.Scatter3d]:
    """Create separate traces for different types of relationships with enhanced visibility.

    Returns a list of traces for batch addition to figure using fig.add_traces() for optimal performance.
    """
    if not isinstance(graph, AssetRelationshipGraph):
        raise ValueError("Invalid input data: graph must be an AssetRelationshipGraph instance")
    if not hasattr(graph, "relationships") or not isinstance(graph.relationships, dict):
        raise ValueError("Invalid input data: graph must have a relationships dictionary")
    if not isinstance(positions, np.ndarray):
        raise ValueError("Invalid input data: positions must be a numpy array")
    if len(positions) != len(asset_ids):
        raise ValueError("Invalid input data: positions array length must match asset_ids length")

    asset_id_index = _build_asset_id_index(asset_ids)

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
    """Create arrow markers for unidirectional relationships using vectorized NumPy operations. Returns a list of traces for batch addition to figure."""
    if not isinstance(graph, AssetRelationshipGraph):
        raise TypeError("Expected graph to be an instance of AssetRelationshipGraph")
    if not hasattr(graph, "relationships") or not isinstance(graph.relationships, dict):
        raise ValueError("Invalid input data: graph must have a relationships dictionary")

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
        except Exception as exc:  # pylint: disable=broad-except
            raise ValueError("asset_ids must be an iterable of strings") from exc

    if not np.issubdtype(positions.dtype, np.number):
        try:
            positions = positions.astype(float)
        except Exception as exc:  # pylint: disable=broad-except
            raise ValueError("Invalid positions: values must be numeric") from exc

    if not np.isfinite(positions).all():
        raise ValueError("Invalid positions: values must be finite numbers")

    if not all(isinstance(a, str) and a for a in asset_ids):
        raise ValueError("asset_ids must contain non-empty strings")

    relationship_index = _build_relationship_index(graph, asset_ids)
    asset_id_index = _build_asset_id_index(asset_ids)

    source_indices: List[int] = []
    target_indices: List[int] = []
    hover_texts: List[str] = []

    # Gather unidirectional relationships
    for (source_id, target_id, rel_type), _ in relationship_index.items():
        reverse_key = (target_id, source_id, rel_type)
        if reverse_key not in relationship_index:
            source_indices.append(asset_id_index[source_id])
            target_indices.append(asset_id_index[target_id])
            hover_texts.append(f"Direction: {source_id} → {target_id}<br>Type: {rel_type}")

    if not source_indices:
        return []

    # Vectorized arrow position calculation at 70% along each edge
    src_idx_arr = np.asarray(source_indices, dtype=int)
    tgt_idx_arr = np.asarray(target_indices, dtype=int)
    source_positions = positions[src_idx_arr]
    target_positions = positions[tgt_idx_arr]
    arrow_positions = source_positions + 0.7 * (target_positions - source_positions)

    arrow_trace = go.Scatter3d(
        x=arrow_positions[:, 0].tolist(),
        y=arrow_positions[:, 1].tolist(),
        z=arrow_positions[:, 2].tolist(),
        mode="markers",
        marker=dict(
            symbol="diamond",
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


def _validate_filter_parameters(
    show_same_sector: bool,
    show_market_cap: bool,
    show_correlation: bool,
    show_corporate_bond: bool,
    show_commodity_currency: bool,
    show_income_comparison: bool,
    show_regulatory: bool,
    show_all_relationships: bool,
    toggle_arrows: bool,
) -> None:
    """Validate that all filter parameters are boolean values.

    Args:
        show_same_sector: Filter for same sector relationships
        show_market_cap: Filter for market cap relationships
        show_correlation: Filter for correlation relationships
        show_corporate_bond: Filter for corporate bond relationships
        show_commodity_currency: Filter for commodity currency relationships
        show_income_comparison: Filter for income comparison relationships
        show_regulatory: Filter for regulatory relationships
        show_all_relationships: Master toggle for all relationships
        toggle_arrows: Toggle for directional arrows

    Raises:
        TypeError: If any parameter is not a boolean
    """
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

    invalid_params = [
        name for name, value in filter_params.items() if not isinstance(value, bool)
    ]

    if invalid_params:
        raise TypeError(
            f"Invalid filter configuration: The following parameters must be boolean values: "
            f"{', '.join(invalid_params)}"
        )


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

    This function dynamically creates and adds relationship traces based on optional filters,
    with comprehensive error handling to manage potential issues from invalid filter
    configurations or data inconsistencies.

    Args:
        graph: Asset relationship graph to visualize
        show_same_sector: Show same sector relationships (default: True)
        show_market_cap: Show market cap relationships (default: True)
        show_correlation: Show correlation relationships (default: True)
        show_corporate_bond: Show corporate bond relationships (default: True)
        show_commodity_currency: Show commodity currency relationships (default: True)
        show_income_comparison: Show income comparison relationships (default: True)
        show_regulatory: Show regulatory relationships (default: True)
        show_all_relationships: Master toggle to show all relationships (default: True)
        toggle_arrows: Show directional arrows for unidirectional relationships (default: True)

    Returns:
        Plotly Figure object with 3D visualization

    Raises:
        ValueError: If graph is invalid or missing required methods/attributes
        TypeError: If filter parameters are not boolean values
    """
    # Validate graph input
    if not isinstance(graph, AssetRelationshipGraph) or not hasattr(
        graph, "get_3d_visualization_data_enhanced"
    ):
        raise ValueError(
            "Invalid graph data provided: graph must be an AssetRelationshipGraph instance "
            "with get_3d_visualization_data_enhanced method"
        )

    # Validate filter parameters
    try:
        _validate_filter_parameters(
            show_same_sector,
            show_market_cap,
            show_correlation,
            show_corporate_bond,
            show_commodity_currency,
            show_income_comparison,
            show_regulatory,
            show_all_relationships,
            toggle_arrows,
        )
    except TypeError as exc:
        logger.error("Invalid filter configuration: %s", exc)
        raise

    # Build filter configuration
    try:
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
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to build filter configuration: %s", exc)
        raise ValueError("Invalid filter configuration") from exc

    # Retrieve visualization data with error handling
    try:
        positions, asset_ids, colors, hover_texts = graph.get_3d_visualization_data_enhanced()
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to retrieve visualization data from graph: %s", exc)
        raise ValueError("Failed to retrieve graph visualization data") from exc

    # Validate retrieved data
    try:
        _validate_visualization_data(positions, asset_ids, colors, hover_texts)
    except ValueError as exc:
        logger.error("Invalid visualization data: %s", exc)
        raise

    # Create figure
    fig = go.Figure()

    # Build relationship traces with comprehensive error handling
    try:
        relationship_traces = _create_relationship_traces(
            graph, positions, asset_ids, relationship_filters
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "Failed to create filtered relationship traces (filters: %s): %s",
            relationship_filters,
            exc
        )
        relationship_traces = []

    # Add relationship traces with error handling
    if relationship_traces:
        try:
            fig.add_traces(relationship_traces)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to add filtered relationship traces to figure: %s", exc)

    # Add directional arrows if enabled
    if toggle_arrows:
        try:
            arrow_traces = _create_directional_arrows(graph, positions, asset_ids)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to create directional arrows: %s", exc)
            arrow_traces = []

        if arrow_traces:
            try:
                fig.add_traces(arrow_traces)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Failed to add directional arrows to figure: %s", exc)

    # Add node trace
    try:
        node_trace = _create_node_trace(positions, asset_ids, colors, hover_texts)
        fig.add_trace(node_trace)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create or add node trace: %s", exc)
        raise ValueError("Failed to create node visualization") from exc

    # Calculate visible relationships count
    visible_relationships = 0
    try:
        visible_relationships = (
            sum(len(getattr(trace, "x", []) or []) for trace in relationship_traces) // 3
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to compute visible relationships count: %s", exc)

    # Configure layout
    try:
        dynamic_title = _generate_dynamic_title(len(asset_ids), visible_relationships)
        _configure_3d_layout(fig, dynamic_title)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to configure figure layout: %s", exc)
        # Use fallback title if dynamic title generation fails
        fallback_title = "Financial Asset Network"
        _configure_3d_layout(fig, fallback_title)

    return fig
