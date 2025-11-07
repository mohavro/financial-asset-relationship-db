"""Pytest configuration and fixtures for the financial asset relationship database tests."""

import pytest

from src.logic.asset_graph import AssetRelationshipGraph
from src.models.financial_models import (
    AssetClass,
    Bond,
    Commodity,
    Currency,
    Equity,
    RegulatoryActivity,
    RegulatoryEvent,
)


@pytest.fixture
def sample_equity():
    """Create a sample equity asset for testing."""
    return Equity(
        id="TEST_AAPL",
        symbol="AAPL",
        name="Apple Inc.",
        asset_class=AssetClass.EQUITY,
        sector="Technology",
        price=150.00,
        market_cap=2.4e12,
        pe_ratio=25.5,
        dividend_yield=0.005,
        earnings_per_share=5.89,
    )


@pytest.fixture
def sample_bond():
    """Create a sample bond asset for testing."""
    return Bond(
        id="TEST_BOND",
        symbol="AAPL_BOND",
        name="Apple Corporate Bond",
        asset_class=AssetClass.FIXED_INCOME,
        sector="Technology",
        price=1000.00,
        yield_to_maturity=0.03,
        coupon_rate=0.025,
        maturity_date="2030-01-01",
        credit_rating="AAA",
        issuer_id="TEST_AAPL",
    )


@pytest.fixture
def sample_commodity():
    """Create a sample commodity asset for testing."""
    return Commodity(
        id="TEST_GOLD",
        symbol="GOLD",
        name="Gold Futures",
        asset_class=AssetClass.COMMODITY,
        sector="Materials",
        price=1950.00,
        contract_size=100.0,
        delivery_date="2024-12-31",
        volatility=0.15,
    )


@pytest.fixture
def sample_currency():
    """Create a sample currency asset for testing."""
    return Currency(
        id="TEST_EUR",
        symbol="EUR",
        name="Euro",
        asset_class=AssetClass.CURRENCY,
        sector="Currency",
        price=1.10,
        exchange_rate=1.10,
        country="Eurozone",
        central_bank_rate=0.04,
    )


@pytest.fixture
def sample_regulatory_event():
    """Create a sample regulatory event for testing."""
    return RegulatoryEvent(
        id="EVENT_001",
        asset_id="TEST_AAPL",
        event_type=RegulatoryActivity.EARNINGS_REPORT,
        date="2024-01-15",
        description="Q4 2023 Earnings Report",
        impact_score=0.8,
        related_assets=["TEST_BOND", "TEST_GOLD"],
    )


@pytest.fixture
def empty_graph():
    """Create an empty asset relationship graph."""
    return AssetRelationshipGraph()


@pytest.fixture
def populated_graph(sample_equity, sample_bond, sample_commodity, sample_currency):
    """Create a populated asset relationship graph."""
    graph = AssetRelationshipGraph()
    graph.add_asset(sample_equity)
    graph.add_asset(sample_bond)
    graph.add_asset(sample_commodity)
    graph.add_asset(sample_currency)
    return graph


@pytest.fixture
def _reset_graph():
    """Reset the graph singleton between tests."""
    from api.main import reset_graph

    reset_graph()
    yield
    reset_graph()
