"""Asset relationship graph service backed by the relational database."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy.orm import sessionmaker

from src.data.database import create_engine_from_url, create_session_factory, init_db, session_scope
from src.data.repository import AssetGraphRepository, RelationshipRecord
from src.models.financial_models import Asset, AssetClass, Bond, Commodity, Currency, Equity, RegulatoryEvent


class AssetRelationshipGraph:
    """High-level service translating between persistent storage and analytics logic."""

    def __init__(self, session_factory: Optional[sessionmaker] = None, database_url: Optional[str] = None):
        if session_factory is not None:
            self._session_factory = session_factory
            self._engine = None
        else:
            self._engine = create_engine_from_url(database_url)
            init_db(self._engine)
            self._session_factory = create_session_factory(self._engine)
        self._positions: Optional[np.ndarray] = None
        self._relationship_cache: Optional[List[RelationshipRecord]] = None
        self._relationship_cache_valid = False
        self._positions_known_asset_ids: List[str] = []
        self.relationship_metrics: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Properties exposing database-backed collections
    # ------------------------------------------------------------------
    @property
    def assets(self) -> Dict[str, Asset]:
        return self._run_repository(lambda repo: repo.get_assets_map())

    @property
    def relationships(self) -> Dict[str, List[Tuple[str, str, float]]]:
        relationships = self._get_relationship_records()
        outgoing: Dict[str, List[Tuple[str, str, float]]] = {}
        for rel in relationships:
            outgoing.setdefault(rel.source_id, []).append((rel.target_id, rel.relationship_type, rel.strength))
        return outgoing

    @property
    def incoming_relationships(self) -> Dict[str, List[Tuple[str, str, float]]]:
        relationships = self._get_relationship_records()
        incoming: Dict[str, List[Tuple[str, str, float]]] = {}
        for rel in relationships:
            incoming.setdefault(rel.target_id, []).append((rel.source_id, rel.relationship_type, rel.strength))
        return incoming

    @property
    def regulatory_events(self) -> List[RegulatoryEvent]:
        return self._run_repository(lambda repo: repo.list_regulatory_events())

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def add_asset(self, asset: Asset) -> None:
        """Add or update an asset in persistent storage."""

        self._run_repository(lambda repo: repo.upsert_asset(asset))
        self._invalidate_caches(asset_changed=True)

    def delete_asset(self, asset_id: str) -> None:
        """Delete an asset from the database."""

        self._run_repository(lambda repo: repo.delete_asset(asset_id))
        self._invalidate_caches(asset_changed=True)

    def add_relationship(
        self, source_id: str, target_id: str, rel_type: str, strength: float = 0.5, bidirectional: bool = False
    ) -> None:
        """Persist a relationship between two assets."""

        strength = float(max(0.0, min(1.0, strength)))

        def _op(repo: AssetGraphRepository) -> None:
            repo.add_or_update_relationship(source_id, target_id, rel_type, strength, bidirectional)
            if bidirectional:
                repo.add_or_update_relationship(target_id, source_id, rel_type, strength, bidirectional)

        self._run_repository(_op)
        self._invalidate_caches()

    def delete_relationship(self, source_id: str, target_id: str, rel_type: str) -> None:
        """Remove a relationship from the database."""

        def _op(repo: AssetGraphRepository) -> None:
            record = repo.get_relationship(source_id, target_id, rel_type)
            if record is None:
                return
            repo.delete_relationship(source_id, target_id, rel_type)
            if record.bidirectional:
                repo.delete_relationship(target_id, source_id, rel_type)

        self._run_repository(_op)
        self._invalidate_caches()

    def add_regulatory_event(self, event: RegulatoryEvent) -> None:
        """Add a regulatory event and link it to related assets."""

        self._run_repository(lambda repo: repo.upsert_regulatory_event(event))
        for related_id in event.related_assets:
            self.add_relationship(
                event.asset_id,
                related_id,
                f"event_{event.event_type.value}",
                abs(event.impact_score),
                bidirectional=False,
            )
        self._invalidate_caches()

    def delete_regulatory_event(self, event_id: str) -> None:
        """Delete a regulatory event."""

        self._run_repository(lambda repo: repo.delete_regulatory_event(event_id))
        self._invalidate_caches()

    # ------------------------------------------------------------------
    # Relationship discovery and analytics
    # ------------------------------------------------------------------
    def build_relationships(self) -> None:
        """Automatically build relationships based on asset attributes."""

        def _op(repo: AssetGraphRepository) -> None:
            assets = repo.list_assets()
            for i, asset1 in enumerate(assets):
                for asset2 in assets[i + 1 :]:
                    for rel_type, strength, bidirectional in self._find_relationships(asset1, asset2):
                        repo.add_or_update_relationship(asset1.id, asset2.id, rel_type, strength, bidirectional)
                        if bidirectional:
                            repo.add_or_update_relationship(asset2.id, asset1.id, rel_type, strength, bidirectional)
                    for rel_type, strength, bidirectional in self._find_relationships(asset2, asset1):
                        if not bidirectional:
                            repo.add_or_update_relationship(asset2.id, asset1.id, rel_type, strength, bidirectional)

        self._run_repository(_op)
        self._invalidate_caches()

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate network metrics for the current graph state."""

        assets, relationships, events = self._collect_graph_state()

        metrics: Dict[str, Any] = {
            "total_assets": len(assets),
            "total_relationships": len(relationships),
            "average_relationship_strength": 0.0,
            "relationship_distribution": {},
            "asset_class_distribution": {},
            "regulatory_event_count": len(events),
            "top_relationships": [],
            "total_in_degree": 0,
            "total_out_degree": 0,
            "average_in_degree": 0.0,
            "average_out_degree": 0.0,
            "average_degree": 0.0,
            "avg_degree": 0.0,
            "max_in_degree": 0,
            "max_out_degree": 0,
            "max_degree": 0,
            "network_density": 0.0,
            "relationship_density": 0.0,
        }

        for asset in assets.values():
            ac = asset.asset_class.value
            metrics["asset_class_distribution"][ac] = metrics["asset_class_distribution"].get(ac, 0) + 1

        outgoing_map = self._build_outgoing_map(relationships)
        incoming_map = self._build_incoming_map(relationships)

        strengths: List[float] = []
        all_relationships: List[Tuple[str, str, str, float]] = []
        for source_id, rels in outgoing_map.items():
            for target_id, rel_type, strength in rels:
                strengths.append(strength)
                all_relationships.append((source_id, target_id, rel_type, strength))
                metrics["relationship_distribution"][rel_type] = metrics["relationship_distribution"].get(rel_type, 0) + 1

        if strengths:
            metrics["average_relationship_strength"] = float(np.mean(strengths))
            metrics["top_relationships"] = sorted(all_relationships, key=lambda item: item[3], reverse=True)[:5]

        node_ids = set(assets.keys()) | set(outgoing_map.keys()) | set(incoming_map.keys())
        node_count = len(node_ids)

        total_in_degree = sum(len(v) for v in incoming_map.values())
        total_out_degree = sum(len(v) for v in outgoing_map.values())

        if node_count > 0:
            metrics["total_in_degree"] = total_in_degree
            metrics["total_out_degree"] = total_out_degree
            metrics["total_relationships"] = total_out_degree
            metrics["average_in_degree"] = total_in_degree / node_count
            metrics["average_out_degree"] = total_out_degree / node_count
            metrics["avg_degree"] = (total_in_degree + total_out_degree) / node_count
            metrics["average_degree"] = metrics["avg_degree"]

            metrics["max_in_degree"] = max((len(v) for v in incoming_map.values()), default=0)
            metrics["max_out_degree"] = max((len(v) for v in outgoing_map.values()), default=0)
            metrics["max_degree"] = max(
                (
                    len(outgoing_map.get(node_id, [])) + len(incoming_map.get(node_id, []))
                    for node_id in node_ids
                ),
                default=0,
            )

            possible_edges = node_count * (node_count - 1) if node_count > 1 else 0
            density = (total_out_degree / possible_edges) * 100.0 if possible_edges else 0.0
            metrics["network_density"] = density
            metrics["relationship_density"] = density

        self.relationship_metrics = metrics
        return metrics

    # ------------------------------------------------------------------
    # Visualisation helpers
    # ------------------------------------------------------------------
    def get_3d_visualization_data(
        self,
    ) -> Tuple[np.ndarray, List[str], List[str], List[str], Tuple[List[float], List[float], List[float]]]:
        """Generate deterministic 3D coordinates for visualization."""

        assets = self.assets
        relationships = self._get_relationship_records()
        asset_ids = list(assets.keys())
        n_assets = len(asset_ids)

        if self._positions is None or self._positions.shape[0] != n_assets or self._positions_asset_ids_changed(asset_ids):
            np.random.seed(42)
            self._positions = np.random.randn(n_assets, 3) * 10
            self._positions_known_asset_ids = asset_ids.copy()

        positions = self._positions

        color_map = {
            AssetClass.EQUITY.value: "blue",
            AssetClass.FIXED_INCOME.value: "green",
            AssetClass.COMMODITY.value: "orange",
            AssetClass.CURRENCY.value: "red",
            AssetClass.DERIVATIVE.value: "purple",
        }

        asset_colors: List[str] = []
        asset_text: List[str] = []

        for asset_id in asset_ids:
            asset = assets[asset_id]
            asset_colors.append(color_map.get(asset.asset_class.value, "gray"))
            price_display = asset.price
            if isinstance(asset, Currency) and asset.exchange_rate is not None:
                price_display = asset.exchange_rate
            asset_text.append(f"{asset.symbol}<br>{asset.name}<br>{price_display}")

        edges_x: List[float] = []
        edges_y: List[float] = []
        edges_z: List[float] = []

        outgoing_map = self._build_outgoing_map(relationships)
        id_to_index = {asset_id: idx for idx, asset_id in enumerate(asset_ids)}
        for source_id, rels in outgoing_map.items():
            if source_id not in id_to_index:
                continue
            source_idx = id_to_index[source_id]
            for target_id, _, _ in rels:
                if target_id not in id_to_index:
                    continue
                target_idx = id_to_index[target_id]
                edges_x.extend([positions[source_idx, 0], positions[target_idx, 0], None])
                edges_y.extend([positions[source_idx, 1], positions[target_idx, 1], None])
                edges_z.extend([positions[source_idx, 2], positions[target_idx, 2], None])

        return positions, asset_ids, asset_colors, asset_text, (edges_x, edges_y, edges_z)

    def get_3d_visualization_data_enhanced(self) -> Tuple[np.ndarray, List[str], List[str], List[str]]:
        """Enhanced 3D visualization payload with richer hover text."""

        assets = self.assets
        relationships = self._get_relationship_records()
        asset_ids = list(assets.keys())
        n_assets = len(asset_ids)

        if self._positions is None or self._positions.shape[0] != n_assets or self._positions_asset_ids_changed(asset_ids):
            np.random.seed(42)
            self._positions = np.random.randn(n_assets, 3) * 10
            self._positions_known_asset_ids = asset_ids.copy()

        color_map = {
            AssetClass.EQUITY.value: "#1f77b4",
            AssetClass.FIXED_INCOME.value: "#2ca02c",
            AssetClass.COMMODITY.value: "#ff7f0e",
            AssetClass.CURRENCY.value: "#d62728",
            AssetClass.DERIVATIVE.value: "#9467bd",
        }

        outgoing_map = self._build_outgoing_map(relationships)
        incoming_map = self._build_incoming_map(relationships)

        asset_colors: List[str] = []
        asset_text: List[str] = []

        for asset_id in asset_ids:
            asset = assets[asset_id]
            asset_colors.append(color_map.get(asset.asset_class.value, "#7f7f7f"))
            price_display = asset.price
            if isinstance(asset, Currency) and asset.exchange_rate is not None:
                price_display = asset.exchange_rate

            outgoing_count = len(outgoing_map.get(asset_id, []))
            incoming_count = len(incoming_map.get(asset_id, []))

            asset_text.append(
                f"<b>{asset.symbol}</b><br>"
                f"{asset.name}<br>"
                f"<b>Price:</b> ${price_display:.2f}<br>"
                f"<b>Class:</b> {asset.asset_class.value}<br>"
                f"<b>Sector:</b> {asset.sector}<br>"
                f"<b>Relationships:</b> {outgoing_count + incoming_count}<br>"
                f"<b>Out:</b> {outgoing_count} | <b>In:</b> {incoming_count}"
            )

        return self._positions, asset_ids, asset_colors, asset_text

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run_repository(self, handler):
        with session_scope(self._session_factory) as session:
            repo = AssetGraphRepository(session)
            result = handler(repo)
        return result

    def _get_relationship_records(self) -> List[RelationshipRecord]:
        if self._relationship_cache_valid and self._relationship_cache is not None:
            return self._relationship_cache

        relationships = self._run_repository(lambda repo: repo.list_relationships())
        self._relationship_cache = relationships
        self._relationship_cache_valid = True
        return relationships

    def _collect_graph_state(self) -> Tuple[Dict[str, Asset], List[RelationshipRecord], List[RegulatoryEvent]]:
        def _op(repo: AssetGraphRepository):
            assets = repo.get_assets_map()
            relationships = repo.list_relationships()
            events = repo.list_regulatory_events()
            return assets, relationships, events

        assets, relationships, events = self._run_repository(_op)
        self._relationship_cache = relationships
        self._relationship_cache_valid = True
        return assets, relationships, events

    def _invalidate_caches(self, asset_changed: bool = False) -> None:
        self._relationship_cache_valid = False
        if asset_changed:
            self._positions = None
            self._positions_known_asset_ids = []

    def _positions_asset_ids_changed(self, asset_ids: List[str]) -> bool:
        return sorted(asset_ids) != sorted(self._positions_known_asset_ids)

    def _build_outgoing_map(self, relationships: List[RelationshipRecord]) -> Dict[str, List[Tuple[str, str, float]]]:
        outgoing: Dict[str, List[Tuple[str, str, float]]] = {}
        for rel in relationships:
            outgoing.setdefault(rel.source_id, []).append((rel.target_id, rel.relationship_type, rel.strength))
        return outgoing

    def _build_incoming_map(self, relationships: List[RelationshipRecord]) -> Dict[str, List[Tuple[str, str, float]]]:
        incoming: Dict[str, List[Tuple[str, str, float]]] = {}
        for rel in relationships:
            incoming.setdefault(rel.target_id, []).append((rel.source_id, rel.relationship_type, rel.strength))
        return incoming

    def _find_relationships(self, asset1: Asset, asset2: Asset) -> List[Tuple[str, float, bool]]:
        relationships: List[Tuple[str, float, bool]] = []

        if getattr(asset1, "sector", None) and getattr(asset2, "sector", None) and asset1.sector == asset2.sector:
            relationships.append(("same_sector", 0.7, True))

        if isinstance(asset2, Currency) and getattr(asset1, "currency", None) == asset2.symbol:
            relationships.append(("currency_exposure", 0.8, False))

        if isinstance(asset1, Bond) and isinstance(asset2, Equity) and asset1.issuer_id == asset2.id:
            relationships.append(("corporate_bond_to_equity", 0.9, False))

        if isinstance(asset1, Commodity) and isinstance(asset2, Equity) and self._is_commodity_related(asset1, asset2):
            relationships.append(("commodity_exposure", 0.6, False))

        if isinstance(asset1, Equity) and isinstance(asset2, Bond) and (asset1.dividend_yield is not None and asset2.yield_to_maturity is not None):
            eps = 1e-6
            num = abs(asset1.dividend_yield - asset2.yield_to_maturity)
            den = abs(asset1.dividend_yield) + abs(asset2.yield_to_maturity) + eps
            strength = max(0.0, 1.0 - num / den)
            relationships.append(("income_comparison", strength, True))

        return relationships

    def _is_commodity_related(self, commodity: Commodity, equity: Equity) -> bool:
        commodity_sectors = {
            "CRUDE": ["Energy", "Oil & Gas"],
            "CL": ["Energy", "Oil & Gas"],
            "GOLD": ["Materials", "Mining", "Precious Metals"],
            "GC": ["Materials", "Mining", "Precious Metals"],
            "WHEAT": ["Agriculture"],
            "COPPER": ["Materials", "Mining"],
        }
        key_candidates = [commodity.symbol.upper(), commodity.symbol.split()[0].upper()]
        sectors = set()
        for key in key_candidates:
            sectors.update(commodity_sectors.get(key, []))
        return equity.sector in sectors
