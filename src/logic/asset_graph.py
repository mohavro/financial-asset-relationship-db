import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from src.models.financial_models import Asset, Equity, Bond, Commodity, Currency, RegulatoryEvent, AssetClass

class AssetRelationshipGraph:
    """Manages relationships between assets across all classes"""

    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.relationships: Dict[str, List[Tuple[str, str, float]]] = {}  # asset_id -> [(target_id, rel_type, strength)]
        self.incoming_relationships: Dict[str, List[Tuple[str, str, float]]] = {}  # asset_id -> [(source_id, rel_type, strength)]
        self.regulatory_events: List[RegulatoryEvent] = []
        self.relationship_metrics: Dict[str, float] = {}
        self._positions: Optional[np.ndarray] = None  # persist 3D positions

    def add_asset(self, asset: Asset):
        """Add asset to graph"""
        self.assets[asset.id] = asset
        if asset.id not in self.relationships:
            self.relationships[asset.id] = []
        if asset.id not in self.incoming_relationships:
            self.incoming_relationships[asset.id] = []
        # Invalidate positions if asset count changes
        self._positions = None

    def add_relationship(self, source_id: str, target_id: str, rel_type: str, strength: float = 0.5, bidirectional: bool = False):
        """Add relationship between assets, with optional bidirectionality and deduplication"""
        strength = float(max(0.0, min(1.0, strength)))
        if source_id not in self.relationships:
            self.relationships[source_id] = []
        if target_id not in self.incoming_relationships:
            self.incoming_relationships[target_id] = []
        
        rel = (target_id, rel_type, strength)
        if rel not in self.relationships[source_id]:
            self.relationships[source_id].append(rel)
        
        # Add to incoming relationships
        incoming_rel = (source_id, rel_type, strength)
        if incoming_rel not in self.incoming_relationships[target_id]:
            self.incoming_relationships[target_id].append(incoming_rel)
        
        if bidirectional:
            # Add reverse direction without recursion loop
            if target_id not in self.relationships:
                self.relationships[target_id] = []
            if source_id not in self.incoming_relationships:
                self.incoming_relationships[source_id] = []
            
            rel_rev = (source_id, rel_type, strength)
            if rel_rev not in self.relationships[target_id]:
                self.relationships[target_id].append(rel_rev)
            
            incoming_rel_rev = (target_id, rel_type, strength)
            if incoming_rel_rev not in self.incoming_relationships[source_id]:
                self.incoming_relationships[source_id].append(incoming_rel_rev)

    def add_regulatory_event(self, event: RegulatoryEvent):
        """Add regulatory event and link to related assets"""
        self.regulatory_events.append(event)
        for related_id in event.related_assets:
            self.add_relationship(event.asset_id, related_id, f"event_{event.event_type.value}", abs(event.impact_score), bidirectional=False)

    def build_relationships(self):
        """Automatically build relationships based on asset attributes"""
        asset_list = list(self.assets.values())
        for i, asset1 in enumerate(asset_list):
            for asset2 in asset_list[i+1:]:
                relationships_found = self._find_relationships(asset1, asset2)
                for rel_type, strength, bidirectional in relationships_found:
                    self.add_relationship(asset1.id, asset2.id, rel_type, strength, bidirectional=bidirectional)

    def _find_relationships(self, asset1: Asset, asset2: Asset) -> List[Tuple[str, float, bool]]:
        """Find relationships between two assets.
        Returns list of tuples: (relationship_type, strength, bidirectional)
        """
        relationships: List[Tuple[str, float, bool]] = []

        # Same sector relationship: symmetric
        if getattr(asset1, "sector", None) and getattr(asset2, "sector", None):
            if asset1.sector == asset2.sector:
                relationships.append(("same_sector", 0.7, True))

        # Currency relationship (simple): link asset to single-currency asset whose symbol matches asset.currency
        # With current data, Currency asset has symbol="EUR" for EURUSD representation; this links only non-USD EUR assets.
        if isinstance(asset2, Currency) and getattr(asset1, "currency", None) == asset2.symbol:
            relationships.append(("currency_exposure", 0.8, False))

        # Corporate bond to equity relationship: directional
        if isinstance(asset1, Bond) and isinstance(asset2, Equity):
            if asset1.issuer_id == asset2.id:
                relationships.append(("corporate_bond_to_equity", 0.9, False))

        # Commodity to equity relationship: directional
        if isinstance(asset1, Commodity) and isinstance(asset2, Equity):
            if self._is_commodity_related(asset1, asset2):
                relationships.append(("commodity_exposure", 0.6, False))

        # Dividend yield to bond yield: symmetric, similarity in [0,1]
        if isinstance(asset1, Equity) and isinstance(asset2, Bond):
            if asset1.dividend_yield is not None and asset2.yield_to_maturity is not None:
                eps = 1e-6
                num = abs(asset1.dividend_yield - asset2.yield_to_maturity)
                den = abs(asset1.dividend_yield) + abs(asset2.yield_to_maturity) + eps
                strength = max(0.0, 1.0 - num / den)
                relationships.append(("income_comparison", strength, True))

        return relationships

    def _is_commodity_related(self, commodity: Commodity, equity: Equity) -> bool:
        """Check if equity company is related to commodity"""
        commodity_sectors = {
            "CRUDE": ["Energy", "Oil & Gas"],
            "CL": ["Energy", "Oil & Gas"],
            "GOLD": ["Materials", "Mining", "Precious Metals"],
            "GC": ["Materials", "Mining", "Precious Metals"],
            "WHEAT": ["Agriculture"],
            "COPPER": ["Materials", "Mining"],
        }
        # Try both full symbol and first token
        key_candidates = [commodity.symbol.upper(), commodity.symbol.split()[0].upper()]
        sectors = set()
        for k in key_candidates:
            sectors.update(commodity_sectors.get(k, []))
        return equity.sector in sectors

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate relationship strength metrics"""
        metrics: Dict[str, Any] = {
            "total_assets": len(self.assets),
            "total_relationships": sum(len(rels) for rels in self.relationships.values()),
            "average_relationship_strength": 0.0,
            "relationship_distribution": {},
            "asset_class_distribution": {},
            "regulatory_event_count": len(self.regulatory_events),
            "top_relationships": [],
        }

        # Asset class distribution
        for asset in self.assets.values():
            ac = asset.asset_class.value
            metrics["asset_class_distribution"][ac] = metrics["asset_class_distribution"].get(ac, 0) + 1

        # Relationship metrics
        all_strengths: List[float] = []
        all_relationships: List[Tuple[str, str, str, float]] = []
        for source_id, rels in self.relationships.items():
            for target_id, rel_type, strength in rels:
                all_strengths.append(strength)
                all_relationships.append((source_id, target_id, rel_type, strength))
                metrics["relationship_distribution"][rel_type] = metrics["relationship_distribution"].get(rel_type, 0) + 1

        if all_strengths:
            metrics["average_relationship_strength"] = float(np.mean(all_strengths))
            metrics["top_relationships"] = sorted(all_relationships, key=lambda x: x[3], reverse=True)[:5]

        # Relationship density (% of possible directed pairs)
        n = max(1, metrics["total_assets"])
        metrics["relationship_density"] = (metrics["total_relationships"] / (n * n)) * 100.0
        return metrics

    def get_3d_visualization_data(self) -> Tuple[np.ndarray, List[str], List[str], List[str], Tuple[List[float], List[float], List[float]]]:
        """Generate 3D coordinates for visualization; positions persist across refreshes"""
        n_assets = len(self.assets)
        asset_ids = list(self.assets.keys())

        # Initialize/persist positions
        if self._positions is None or self._positions.shape[0] != n_assets:
            # Stable, deterministic positions based on sorted asset ids
            np.random.seed(42)
            self._positions = np.random.randn(n_assets, 3) * 10
        positions = self._positions

        asset_colors: List[str] = []
        asset_text: List[str] = []

        color_map = {
            AssetClass.EQUITY.value: "blue",
            AssetClass.FIXED_INCOME.value: "green",
            AssetClass.COMMODITY.value: "orange",
            AssetClass.CURRENCY.value: "red",
            AssetClass.DERIVATIVE.value: "purple",
        }

        for asset_id in asset_ids:
            asset = self.assets[asset_id]
            asset_colors.append(color_map.get(asset.asset_class.value, "gray"))
            # Use exchange_rate for currencies if present; otherwise price
            price_display = asset.price
            if isinstance(asset, Currency) and asset.exchange_rate is not None:
                price_display = asset.exchange_rate
            asset_text.append(f"{asset.symbol}<br>{asset.name}<br>{price_display}")

        # Create edges
        edges_x: List[float] = []
        edges_y: List[float] = []
        edges_z: List[float] = []

        for source_id, rels in self.relationships.items():
            if source_id not in asset_ids:
                continue
            source_idx = asset_ids.index(source_id)
            for target_id, rel_type, strength in rels:
                if target_id in asset_ids:
                    target_idx = asset_ids.index(target_id)
                    edges_x.extend([positions[source_idx, 0], positions[target_idx, 0], None])
                    edges_y.extend([positions[source_idx, 1], positions[target_idx, 1], None])
                    edges_z.extend([positions[source_idx, 2], positions[target_idx, 2], None])

        return positions, asset_ids, asset_colors, asset_text, (edges_x, edges_y, edges_z)

    def get_3d_visualization_data_enhanced(self) -> Tuple[np.ndarray, List[str], List[str], List[str]]:
        """Generate enhanced 3D coordinates for visualization with better relationship handling"""
        n_assets = len(self.assets)
        asset_ids = list(self.assets.keys())

        # Initialize/persist positions
        if self._positions is None or self._positions.shape[0] != n_assets:
            # Stable, deterministic positions based on sorted asset ids
            np.random.seed(42)
            self._positions = np.random.randn(n_assets, 3) * 10
        positions = self._positions

        asset_colors: List[str] = []
        asset_text: List[str] = []

        color_map = {
            AssetClass.EQUITY.value: "#1f77b4",      # Professional blue
            AssetClass.FIXED_INCOME.value: "#2ca02c", # Professional green
            AssetClass.COMMODITY.value: "#ff7f0e",    # Professional orange
            AssetClass.CURRENCY.value: "#d62728",     # Professional red
            AssetClass.DERIVATIVE.value: "#9467bd",   # Professional purple
        }

        for asset_id in asset_ids:
            asset = self.assets[asset_id]
            asset_colors.append(color_map.get(asset.asset_class.value, "#7f7f7f"))
            
            # Enhanced hover text with more detail
            price_display = asset.price
            if isinstance(asset, Currency) and asset.exchange_rate is not None:
                price_display = asset.exchange_rate
                
            # Get relationship counts for this asset
            outgoing_count = len(self.relationships.get(asset_id, []))
            incoming_count = len(self.incoming_relationships.get(asset_id, []))
            
            asset_text.append(
                f"<b>{asset.symbol}</b><br>"
                f"{asset.name}<br>"
                f"<b>Price:</b> ${price_display:.2f}<br>"
                f"<b>Class:</b> {asset.asset_class.value}<br>"
                f"<b>Sector:</b> {asset.sector}<br>"
                f"<b>Relationships:</b> {outgoing_count + incoming_count}<br>"
                f"<b>Out:</b> {outgoing_count} | <b>In:</b> {incoming_count}"
            )

        return positions, asset_ids, asset_colors, asset_text