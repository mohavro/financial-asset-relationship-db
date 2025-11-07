import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf
from src.models.financial_models import (
    Asset,
    Equity,
    Bond,
    Commodity,
    Currency,
    RegulatoryEvent,
    AssetClass,
    RegulatoryActivity,
)
from src.logic.asset_graph import AssetRelationshipGraph

logger = logging.getLogger(__name__)


class RealDataFetcher:
    """Fetches real financial data from Yahoo Finance and other sources"""

    def __init__(
        self,
        *,
        cache_path: Optional[str] = None,
        fallback_factory: Optional[Callable[[], AssetRelationshipGraph]] = None,
        enable_network: bool = True,
    ):
        self.session = None
        self.cache_path = Path(cache_path) if cache_path else None
        self.fallback_factory = fallback_factory
        self.enable_network = enable_network

    def create_real_database(self) -> AssetRelationshipGraph:
        """Create a database with real financial data from Yahoo Finance"""
        if self.cache_path and self.cache_path.exists():
            try:
                logger.info("Loading asset graph from cache at %s", self.cache_path)
                return _load_from_cache(self.cache_path)
            except Exception:
                logger.exception("Failed to load cached dataset; proceeding with standard fetch")

        if not self.enable_network:
            logger.info("Network fetching disabled. Using fallback dataset if available.")
            return self._fallback()

        logger.info("Creating database with real financial data from Yahoo Finance")
        graph = AssetRelationshipGraph()

        try:
            # Fetch real data for different asset classes
            equities = self._fetch_equity_data()
            bonds = self._fetch_bond_data()
            commodities = self._fetch_commodity_data()
            currencies = self._fetch_currency_data()

            # Add all assets to graph
            all_assets = equities + bonds + commodities + currencies
            for asset in all_assets:
                graph.add_asset(asset)

            # Add some regulatory events based on real companies
            events = self._create_regulatory_events()
            for event in events:
                graph.add_regulatory_event(event)

            # Build relationships
            graph.build_relationships()

            if self.cache_path:
                import os
                import tempfile

                try:
                    cache_dir = os.path.dirname(self.cache_path)
                    with tempfile.NamedTemporaryFile("wb", dir=cache_dir, delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                        _save_to_cache(graph, tmp_path)
                    os.replace(tmp_path, self.cache_path)
                except Exception:
                    logger.exception("Failed to persist dataset cache to %s", self.cache_path)

            logger.info(
                "Real database created with %s assets and %s relationships",
                len(graph.assets),
                sum(len(rels) for rels in graph.relationships.values()),
            )
            return graph

        except Exception as e:
            logger.error(f"Failed to create real database: {e}")
            # Fallback to sample data if real data fails
            logger.warning("Falling back to sample data due to real data fetch failure")
            return self._fallback()

    def _fallback(self) -> AssetRelationshipGraph:
        if self.fallback_factory is not None:
            return self.fallback_factory()
        from src.data.sample_data import create_sample_database

        return create_sample_database()

    def _fetch_equity_data(self) -> List[Equity]:
        """Fetch real equity data for major stocks"""
        equity_symbols = {
            "AAPL": ("Apple Inc.", "Technology"),
            "MSFT": ("Microsoft Corporation", "Technology"),
            "XOM": ("Exxon Mobil Corporation", "Energy"),
            "JPM": ("JPMorgan Chase & Co.", "Financial Services"),
        }

        equities = []
        for symbol, (name, sector) in equity_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")

                if hist.empty:
                    logger.warning(f"No price data for {symbol}")
                    continue

                current_price = float(hist["Close"].iloc[-1])

                equity = Equity(
                    id=symbol,
                    symbol=symbol,
                    name=name,
                    asset_class=AssetClass.EQUITY,
                    sector=sector,
                    price=current_price,
                    market_cap=info.get("marketCap"),
                    pe_ratio=info.get("trailingPE"),
                    dividend_yield=info.get("dividendYield"),
                    earnings_per_share=info.get("trailingEps"),
                    book_value=info.get("bookValue"),
                )
                equities.append(equity)
                logger.info(f"Fetched {symbol}: {name} at ${current_price:.2f}")

            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                continue

        return equities

    def _fetch_bond_data(self) -> List[Bond]:
        """Fetch real bond/treasury data"""
        # For bonds, we'll use Treasury ETFs and bond proxies since individual bonds are harder to access
        bond_symbols = {
            "TLT": ("iShares 20+ Year Treasury Bond ETF", "Government", None, "AAA"),
            "LQD": ("iShares iBoxx $ Investment Grade Corporate Bond ETF", "Corporate", None, "A"),
            "HYG": ("iShares iBoxx $ High Yield Corporate Bond ETF", "Corporate", None, "BB"),
        }

        bonds = []
        for symbol, (name, sector, issuer_id, rating) in bond_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")

                if hist.empty:
                    logger.warning(f"No price data for {symbol}")
                    continue

                current_price = float(hist["Close"].iloc[-1])

                bond = Bond(
                    id=symbol,
                    symbol=symbol,
                    name=name,
                    asset_class=AssetClass.FIXED_INCOME,
                    sector=sector,
                    price=current_price,
                    yield_to_maturity=info.get("yield", 0.03),  # Default 3% if not available
                    coupon_rate=info.get("yield", 0.025),  # Approximate
                    maturity_date="2035-01-01",  # Approximate for ETFs
                    credit_rating=rating,
                    issuer_id=issuer_id,
                )
                bonds.append(bond)
                logger.info(f"Fetched {symbol}: {name} at ${current_price:.2f}")

            except Exception as e:
                logger.error(f"Failed to fetch bond data for {symbol}: {e}")
                continue

        return bonds

    def _fetch_commodity_data(self) -> List[Commodity]:
        """Fetch real commodity data"""
        commodity_symbols = {
            "GC=F": ("Gold Futures", "Precious Metals", 100),
            "CL=F": ("Crude Oil Futures", "Energy", 1000),
            "SI=F": ("Silver Futures", "Precious Metals", 5000),
        }

        commodities = []
        for symbol, (name, sector, contract_size) in commodity_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")

                if hist.empty:
                    logger.warning(f"No price data for {symbol}")
                    continue

                current_price = float(hist["Close"].iloc[-1])

                # Calculate simple volatility from recent data
                hist_week = ticker.history(period="5d")
                volatility = float(hist_week["Close"].pct_change().std()) if len(hist_week) > 1 else 0.20

                commodity = Commodity(
                    id=symbol.replace("=F", "_FUTURE"),
                    symbol=symbol,
                    name=name,
                    asset_class=AssetClass.COMMODITY,
                    sector=sector,
                    price=current_price,
                    contract_size=contract_size,
                    delivery_date="2025-03-31",  # Approximate
                    volatility=volatility,
                )
                commodities.append(commodity)
                logger.info(f"Fetched {symbol}: {name} at ${current_price:.2f}")

            except Exception as e:
                logger.error(f"Failed to fetch commodity data for {symbol}: {e}")
                continue

        return commodities

    def _fetch_currency_data(self) -> List[Currency]:
        """Fetch real currency exchange rate data"""
        currency_symbols = {
            "EURUSD=X": ("Euro", "EU", "EUR"),
            "GBPUSD=X": ("British Pound", "UK", "GBP"),
            "JPYUSD=X": ("Japanese Yen", "Japan", "JPY"),
        }

        currencies = []
        for symbol, (name, country, currency_code) in currency_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")

                if hist.empty:
                    logger.warning(f"No price data for {symbol}")
                    continue

                current_rate = float(hist["Close"].iloc[-1])

                currency = Currency(
                    id=symbol.replace("=X", ""),
                    symbol=currency_code,
                    name=name,
                    asset_class=AssetClass.CURRENCY,
                    sector="Forex",
                    price=current_rate,
                    exchange_rate=current_rate,
                    country=country,
                    central_bank_rate=0.02,  # Approximate - would need separate API for real rates
                )
                currencies.append(currency)
                logger.info(f"Fetched {symbol}: {name} at {current_rate:.4f}")

            except Exception as e:
                logger.error(f"Failed to fetch currency data for {symbol}: {e}")
                continue

        return currencies

    def _create_regulatory_events(self) -> List[RegulatoryEvent]:
        """Create realistic regulatory events for the fetched assets"""
        # Create some realistic recent events
        events = []

        # Apple earnings event
        apple_earnings = RegulatoryEvent(
            id="AAPL_Q4_2024_REAL",
            asset_id="AAPL",
            event_type=RegulatoryActivity.EARNINGS_REPORT,
            date="2024-11-01",
            description="Q4 2024 Earnings Report - Record iPhone sales",
            impact_score=0.12,
            related_assets=["TLT", "MSFT"],  # Related tech and bonds
        )
        events.append(apple_earnings)

        # Microsoft dividend announcement
        msft_dividend = RegulatoryEvent(
            id="MSFT_DIV_2024_REAL",
            asset_id="MSFT",
            event_type=RegulatoryActivity.DIVIDEND_ANNOUNCEMENT,
            date="2024-09-15",
            description="Quarterly dividend increase - Cloud growth continues",
            impact_score=0.08,
            related_assets=["AAPL", "LQD"],
        )
        events.append(msft_dividend)

        # Energy sector regulatory event
        xom_filing = RegulatoryEvent(
            id="XOM_SEC_2024_REAL",
            asset_id="XOM",
            event_type=RegulatoryActivity.SEC_FILING,
            date="2024-10-01",
            description="10-K Filing - Increased oil reserves and sustainability initiatives",
            impact_score=0.05,
            related_assets=["CL_FUTURE"],  # Related to oil futures
        )
        events.append(xom_filing)

        return events


def create_real_database() -> AssetRelationshipGraph:
    """Main function to create database with real data - fallback to sample data if needed"""
    fetcher = RealDataFetcher()
    return fetcher.create_real_database()


def _enum_to_value(value: Any) -> Any:
    from enum import Enum

    if isinstance(value, Enum):
        return value.value
    return value


def _serialize_dataclass(obj: Any) -> Dict[str, Any]:
    data = asdict(obj)
    serialized = {key: _enum_to_value(val) for key, val in data.items()}
    serialized["__type__"] = obj.__class__.__name__
    return serialized


def _serialize_graph(graph: AssetRelationshipGraph) -> Dict[str, Any]:
    return {
        "assets": [_serialize_dataclass(asset) for asset in graph.assets.values()],
        "regulatory_events": [_serialize_dataclass(event) for event in graph.regulatory_events],
        "relationships": {
            source: [
                {"target": target, "relationship_type": rel_type, "strength": strength}
                for target, rel_type, strength in rels
            ]
            for source, rels in graph.relationships.items()
        },
        "incoming_relationships": {
            target: [
                {"source": source, "relationship_type": rel_type, "strength": strength}
                for source, rel_type, strength in rels
            ]
            for target, rels in graph.incoming_relationships.items()
        },
    }


def _deserialize_asset(data: Dict[str, Any]):
    type_name = data.pop("__type__", "Asset")
    if asset_class_value := data.get("asset_class"):
        data["asset_class"] = AssetClass(asset_class_value)

    cls_map = {
        "Asset": Asset,
        "Equity": Equity,
        "Bond": Bond,
        "Commodity": Commodity,
        "Currency": Currency,
    }

    cls = cls_map.get(type_name, Asset)
    return cls(**data)


def _deserialize_event(data: Dict[str, Any]) -> RegulatoryEvent:
    data = dict(data)
    data["event_type"] = RegulatoryActivity(data["event_type"])
    return RegulatoryEvent(**data)


def _deserialize_graph(payload: Dict[str, Any]) -> AssetRelationshipGraph:
    graph = AssetRelationshipGraph()
    for asset_data in payload.get("assets", []):
        asset = _deserialize_asset(dict(asset_data))
        graph.add_asset(asset)

    graph.regulatory_events = [_deserialize_event(event) for event in payload.get("regulatory_events", [])]

    relationships_payload = payload.get("relationships", {})
    incoming_payload = payload.get("incoming_relationships", {})

    graph.relationships = {
        source: [(item["target"], item["relationship_type"], float(item["strength"])) for item in rels]
        for source, rels in relationships_payload.items()
    }

    graph.incoming_relationships = {
        target: [(item["source"], item["relationship_type"], float(item["strength"])) for item in rels]
        for target, rels in incoming_payload.items()
    }

    return graph


def _load_from_cache(path: Path) -> AssetRelationshipGraph:
    with path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)
    return _deserialize_graph(payload)


def _save_to_cache(graph: AssetRelationshipGraph, path: Path) -> None:
    payload = _serialize_graph(graph)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
