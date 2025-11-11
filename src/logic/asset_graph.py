from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np


class AssetRelationshipGraph:
    """Lightweight interface stub for visualization to avoid import-time errors in tests.

    This stub mirrors the minimal API used by src/visualizations/graph_visuals.py.
    In the real application, the full implementation provides data and relationships.
    """

    def __init__(self) -> None:
        # Dict[source_id] -> List[(target_id, rel_type, strength)]
        self.relationships: Dict[str, List[Tuple[str, str, float]]] = {}

    def get_3d_visualization_data_enhanced(self) -> Tuple[np.ndarray, List[str], List[str], List[str]]:
        # Placeholder demo layout: single node at origin if empty
        asset_ids = list({node for node in self.relationships} | {t for rels in self.relationships.values() for t, _, _ in rels})
        if not asset_ids:
            positions = np.zeros((1, 3))
            return positions, ["A"], ["#888888"], ["Asset A"]
        n = len(asset_ids)
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        positions = np.stack([np.cos(theta), np.sin(theta), np.zeros_like(theta)], axis=1)
        colors = ["#4ECDC4"] * n
        hover = [f"Asset: {aid}" for aid in asset_ids]
        return positions, asset_ids, colors, hover
