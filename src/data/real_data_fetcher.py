import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from src.models.financial_models import (
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

    def __init__(self):
        self.session = None

    def create_real_database(self) -> AssetRelationshipGraph:
        """Create a database with real financial data from Yahoo Finance"""
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

            logger.info(
                f"Real database created with {len(graph.assets)} assets and {sum(len(rels) for rels in graph.relationships.values())} relationships"
            )
            return graph

        except Exception as e:
            logger.error(f"Failed to create real database: {e}")
            # Fallback to sample data if real data fails
            logger.warning("Falling back to sample data due to real data fetch failure")
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
