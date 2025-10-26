import logging
from src.logic.asset_graph import AssetRelationshipGraph
from src.models.financial_models import Equity, Bond, Commodity, Currency, RegulatoryEvent, AssetClass, RegulatoryActivity

logger = logging.getLogger(__name__)

def create_sample_database() -> AssetRelationshipGraph:
    """Create sample financial database"""
    try:
        logger.info("Creating sample financial database")
        graph = AssetRelationshipGraph()

        # Equities
        apple = Equity(
            id="AAPL", symbol="AAPL", name="Apple Inc.",
            asset_class=AssetClass.EQUITY, sector="Technology",
            price=150.00, market_cap=2.4e12, pe_ratio=25.5, dividend_yield=0.005,
            earnings_per_share=5.89
        )

        exxon = Equity(
            id="XOM", symbol="XOM", name="Exxon Mobil",
            asset_class=AssetClass.EQUITY, sector="Energy",
            price=110.00, market_cap=450e9, pe_ratio=12.3, dividend_yield=0.035,
            earnings_per_share=8.95
        )

        # Bonds
        apple_bond = Bond(
            id="AAPL_BOND_2030", symbol="AAPL30", name="Apple Inc. 2030 Bond",
            asset_class=AssetClass.FIXED_INCOME, sector="Technology",
            price=102.50, yield_to_maturity=0.025, coupon_rate=0.02,
            maturity_date="2030-01-15", credit_rating="AA+", issuer_id="AAPL"
        )

        us_10y = Bond(
            id="US10Y", symbol="US10Y", name="US 10-Year Treasury",
            asset_class=AssetClass.FIXED_INCOME, sector="Government",
            price=98.50, yield_to_maturity=0.042, coupon_rate=0.035,
            maturity_date="2034-02-15", credit_rating="AAA"
        )

        # Commodities
        crude_oil = Commodity(
            id="CL_CRUDE", symbol="CL", name="WTI Crude Oil",
            asset_class=AssetClass.COMMODITY, sector="Energy",
            price=88.50, contract_size=1000, volatility=0.35
        )

        gold = Commodity(
            id="GC_GOLD", symbol="GC", name="COMEX Gold",
            asset_class=AssetClass.COMMODITY, sector="Precious Metals",
            price=2050.00, contract_size=100, volatility=0.15
        )

        # Currencies
        usd_eur = Currency(
            id="EURUSD", symbol="EUR", name="Euro",
            asset_class=AssetClass.CURRENCY, sector="Forex",
            price=1.10, exchange_rate=1.10, country="EU", central_bank_rate=0.035
        )

        # Add all assets
        for asset in [apple, exxon, apple_bond, us_10y, crude_oil, gold, usd_eur]:
            graph.add_asset(asset)

        # Add regulatory events
        earnings_event = RegulatoryEvent(
            id="AAPL_Q4_2024", asset_id="AAPL", event_type=RegulatoryActivity.EARNINGS_REPORT,
            date="2024-01-25", description="Q4 2024 Earnings Beat", impact_score=0.15,
            related_assets=["AAPL_BOND_2030", "US10Y"]
        )

        dividend_event = RegulatoryEvent(
            id="XOM_DIV_2024", asset_id="XOM", event_type=RegulatoryActivity.DIVIDEND_ANNOUNCEMENT,
            date="2024-02-10", description="Quarterly Dividend Increase", impact_score=0.10,
            related_assets=["CL_CRUDE"]
        )

        graph.add_regulatory_event(earnings_event)
        graph.add_regulatory_event(dividend_event)

        # Build all relationships
        graph.build_relationships()

        logger.info(f"Sample database created with {len(graph.assets)} assets and {sum(len(rels) for rels in graph.relationships.values())} relationships")
        return graph
    except Exception as e:
        logger.error(f"Failed to create sample database: {e}")
        raise