import numpy as np
import plotly.graph_objects as go
from src.logic.asset_graph import AssetRelationshipGraph
from src.visualizations.graph_visuals import (REL_TYPE_COLORS,
                                              _build_asset_id_index,
                                              _build_relationship_index,
                                              _create_directional_arrows,
                                              _create_relationship_traces)

import pytest


class DummyGraph(AssetRelationshipGraph):
    def __init__(self, relationships):
        # relationships: Dict[str, List[Tuple[str, str, float]]]
        self.relationships = relationships

    def get_3d_visualization_data_enhanced(self):
        # Return positions (n,3), asset_ids, colors, hover_texts
        asset_ids = sorted({k for k in self.relationships.keys()} | {t for v in self.relationships.values() for t, _, _ in v})
        n = len(asset_ids)
        positions = np.arange(n * 3, dtype=float).reshape(n, 3)
        colors = ["#000000"] * n
        hover_texts = asset_ids
        return positions, asset_ids, colors, hover_texts


def test_rel_type_colors_default():
    # Ensure defaultdict provides fallback color, and direct indexing works without KeyError
    assert REL_TYPE_COLORS["unknown_type"] == "#888888"


def test_build_asset_id_index():
    ids = ["A", "B", "C"]
    idx = _build_asset_id_index(ids)
    assert idx == {"A": 0, "B": 1, "C": 2}


def test_build_relationship_index_filters_to_asset_ids():
    graph = DummyGraph({
        "A": [("B", "correlation", 0.9), ("X", "correlation", 0.5)],
        "C": [("A", "same_sector", 1.0)],
    })
    index = _build_relationship_index(graph, ["A", "B", "C"])
    # Should include only pairs where both ends are in the provided list
    assert ("A", "B", "correlation") in index
    assert ("C", "A", "same_sector") in index
    assert ("A", "X", "correlation") not in index


def test_create_relationship_traces_basic():
    graph = DummyGraph({
        "A": [("B", "correlation", 0.9)],
        "B": [("A", "correlation", 0.9)],  # bidirectional
        "C": [("A", "same_sector", 1.0)],  # unidirectional
    })
    positions, asset_ids, _, _ = graph.get_3d_visualization_data_enhanced()

    traces = _create_relationship_traces(graph, positions, asset_ids)
    # There should be two groups: correlation (bidirectional) and same_sector (unidirectional)
    names = {t.name for t in traces}
    assert any("Correlation (↔)" == name for name in names)
    assert any("Same Sector (→)" == name for name in names)

    # Lines should carry color directly from REL_TYPE_COLORS via direct indexing
    corr_trace = next(t for t in traces if t.legendgroup == "correlation")
    assert corr_trace.line.color == REL_TYPE_COLORS["correlation"]


def test_create_directional_arrows_validation_errors():
    graph = DummyGraph({})
    with pytest.raises(TypeError):
        _create_directional_arrows(object(), np.zeros((0, 3)), [])  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        _create_directional_arrows(graph, None, [])  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        _create_directional_arrows(graph, np.zeros((1, 2)), ["A"])  # invalid shape


def test_create_directional_arrows_basic():
    graph = DummyGraph({
        "A": [("B", "correlation", 0.9)],  # unidirectional
        "B": [("A", "correlation", 0.9)],  # and reverse, makes it bidirectional (no arrow)
        "C": [("A", "same_sector", 1.0)],  # unidirectional
    })
    positions, asset_ids, _, _ = graph.get_3d_visualization_data_enhanced()

    # Remove one side to ensure a unidirectional exists
    graph.relationships["B"] = []

    arrows = _create_directional_arrows(graph, positions, asset_ids)
    assert isinstance(arrows, list)
    if arrows:
        arrow_trace = arrows[0]
        assert isinstance(arrow_trace, go.Scatter3d)
        assert arrow_trace.mode == "markers"
        assert arrow_trace.showlegend is False
