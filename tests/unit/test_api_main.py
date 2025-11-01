"""Comprehensive unit tests for the FastAPI backend.

This module contains thorough unit tests for all API endpoints including:
- Root and health check endpoints
- Asset CRUD operations with filtering
- Relationship queries and traversal
- Metrics calculation and aggregation
- Visualization data generation
- Asset class and sector metadata
- CORS origin validation
- Error handling and edge cases
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from api.main import app, validate_origin, get_graph
from src.models.financial_models import AssetClass, Equity, Bond
from src.logic.asset_graph import AssetRelationshipGraph


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_graph():
    """Create a mock AssetRelationshipGraph for testing."""
    graph = Mock(spec=AssetRelationshipGraph)
    
    # Create sample assets
    equity = Equity(
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
        book_value=3.50,
        currency="USD"
    )
    
    bond = Bond(
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
        currency="USD"
    )
    
    graph.assets = {
        "TEST_AAPL": equity,
        "TEST_BOND": bond
    }
    
    # Mock relationships
    graph.relationships = {
        "TEST_AAPL": [("TEST_BOND", "issues", 0.9)],
        "TEST_BOND": []
    }
    
    # Mock metrics
    graph.calculate_metrics.return_value = {
        "total_assets": 2,
        "total_relationships": 1,
        "avg_degree": 0.5,
        "max_degree": 1,
        "network_density": 0.5
    }
    
    # Mock visualization data
    graph.get_3d_visualization_data.return_value = {
        "nodes": [
            {
                "id": "TEST_AAPL",
                "name": "Apple Inc.",
                "symbol": "AAPL",
                "asset_class": "EQUITY",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "color": "#1f77b4",
                "size": 5
            },
            {
                "id": "TEST_BOND",
                "name": "Apple Corporate Bond",
                "symbol": "AAPL_BOND",
                "asset_class": "FIXED_INCOME",
                "x": 1.0,
                "y": 1.0,
                "z": 1.0,
                "color": "#ff7f0e",
                "size": 5
            }
        ],
        "edges": [
            {
                "source": "TEST_AAPL",
                "target": "TEST_BOND",
                "relationship_type": "issues",
                "strength": 0.9
            }
        ]
    }
    
    return graph


class TestCORSValidation:
    """Test cases for CORS origin validation."""
    
    def test_validate_localhost(self):
        """Test that localhost origins are accepted."""
        assert validate_origin("http://localhost:3000") is True
        assert validate_origin("http://localhost:8000") is True
        assert validate_origin("https://localhost:3000") is True
        
    def test_validate_127_0_0_1(self):
        """Test that 127.0.0.1 origins are accepted."""
        assert validate_origin("http://127.0.0.1:3000") is True
        assert validate_origin("https://127.0.0.1:8000") is True
        
    def test_validate_vercel_domains(self):
        """Test that Vercel domains are accepted."""
        assert validate_origin("https://my-app.vercel.app") is True
        assert validate_origin("https://my-app-git-main.vercel.app") is True
        assert validate_origin("https://my-app-user-123.vercel.app") is True
        
    def test_reject_invalid_origins(self):
        """Test that invalid origins are rejected."""
        assert validate_origin("http://malicious.com") is False
        assert validate_origin("https://not-vercel.com") is False
        assert validate_origin("ftp://localhost:3000") is False
        assert validate_origin("javascript:alert(1)") is False
        
    def test_reject_malformed_origins(self):
        """Test that malformed origins are rejected."""
        assert validate_origin("not-a-url") is False
        assert validate_origin("") is False
        assert validate_origin("http://") is False


class TestRootEndpoints:
    """Test cases for root and health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"
        
    def test_root_endpoint_structure(self, client):
        """Test that root endpoint has all expected fields."""
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "assets" in endpoints
        assert "relationships" in endpoints
        assert "metrics" in endpoints
        assert "visualization" in endpoints
        
    @patch("api.main.graph", None)
    def test_health_check_no_graph(self, client):
        """Test health check when graph is not initialized."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["graph_initialized"] is False
        
    @patch("api.main.graph")
    def test_health_check_with_graph(self, mock_graph_global, client):
        """Test health check when graph is initialized."""
        mock_graph_global.return_value = MagicMock()
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAssetEndpoints:
    """Test cases for asset-related endpoints."""
    
    @patch("api.main.get_graph")
    def test_get_all_assets(self, mock_get_graph, mock_graph, client):
        """Test getting all assets without filters."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(asset["symbol"] == "AAPL" for asset in data)
        assert any(asset["symbol"] == "AAPL_BOND" for asset in data)
        
    @patch("api.main.get_graph")
    def test_get_assets_with_class_filter(self, mock_get_graph, mock_graph, client):
        """Test filtering assets by asset class."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets?asset_class=EQUITY")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"
        assert data[0]["asset_class"] == "EQUITY"
        
    @patch("api.main.get_graph")
    def test_get_assets_with_sector_filter(self, mock_get_graph, mock_graph, client):
        """Test filtering assets by sector."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets?sector=Technology")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(asset["sector"] == "Technology" for asset in data)
        
    @patch("api.main.get_graph")
    def test_get_assets_with_combined_filters(self, mock_get_graph, mock_graph, client):
        """Test filtering assets by both class and sector."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets?asset_class=EQUITY&sector=Technology")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"
        
    @patch("api.main.get_graph")
    def test_get_assets_no_matches(self, mock_get_graph, mock_graph, client):
        """Test filtering with no matching results."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets?sector=NonExistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
    @patch("api.main.get_graph")
    def test_get_asset_detail(self, mock_get_graph, mock_graph, client):
        """Test getting detailed information for a specific asset."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "TEST_AAPL"
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert data["price"] == 150.00
        assert "pe_ratio" in data["additional_fields"]
        
    @patch("api.main.get_graph")
    def test_get_asset_detail_not_found(self, mock_get_graph, mock_graph, client):
        """Test getting asset detail for non-existent asset."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/NONEXISTENT")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        
    @patch("api.main.get_graph")
    def test_get_asset_additional_fields(self, mock_get_graph, mock_graph, client):
        """Test that asset-specific fields are included in additional_fields."""
        mock_get_graph.return_value = mock_graph
        
        # Test equity fields
        response = client.get("/api/assets/TEST_AAPL")
        data = response.json()
        assert "pe_ratio" in data["additional_fields"]
        assert data["additional_fields"]["pe_ratio"] == 25.5
        assert "dividend_yield" in data["additional_fields"]
        
        # Test bond fields
        response = client.get("/api/assets/TEST_BOND")
        data = response.json()
        assert "yield_to_maturity" in data["additional_fields"]
        assert "coupon_rate" in data["additional_fields"]
        assert "credit_rating" in data["additional_fields"]
        
    @patch("api.main.get_graph")
    def test_get_assets_error_handling(self, mock_get_graph, client):
        """Test error handling when graph operations fail."""
        mock_get_graph.side_effect = Exception("Database error")
        
        response = client.get("/api/assets")
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower() or "database error" in response.json()["detail"].lower()


class TestRelationshipEndpoints:
    """Test cases for relationship-related endpoints."""
    
    @patch("api.main.get_graph")
    def test_get_asset_relationships(self, mock_get_graph, mock_graph, client):
        """Test getting relationships for a specific asset."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_AAPL/relationships")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == "TEST_AAPL"
        assert data[0]["target_id"] == "TEST_BOND"
        assert data[0]["relationship_type"] == "issues"
        assert data[0]["strength"] == 0.9
        
    @patch("api.main.get_graph")
    def test_get_asset_relationships_none(self, mock_get_graph, mock_graph, client):
        """Test getting relationships for asset with no relationships."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_BOND/relationships")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
    @patch("api.main.get_graph")
    def test_get_asset_relationships_not_found(self, mock_get_graph, mock_graph, client):
        """Test getting relationships for non-existent asset."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/NONEXISTENT/relationships")
        assert response.status_code == 404
        
    @patch("api.main.get_graph")
    def test_get_all_relationships(self, mock_get_graph, mock_graph, client):
        """Test getting all relationships in the graph."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/relationships")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == "TEST_AAPL"
        assert data[0]["target_id"] == "TEST_BOND"
        
    @patch("api.main.get_graph")
    def test_get_all_relationships_multiple(self, mock_get_graph, mock_graph, client):
        """Test getting all relationships with multiple sources."""
        # Add more relationships
        mock_graph.relationships = {
            "TEST_AAPL": [
                ("TEST_BOND", "issues", 0.9),
                ("TEST_BOND", "correlates_with", 0.7)
            ],
            "TEST_BOND": [("TEST_AAPL", "issued_by", 0.9)]
        }
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/relationships")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestMetricsEndpoint:
    """Test cases for the metrics endpoint."""
    
    @patch("api.main.get_graph")
    def test_get_metrics(self, mock_get_graph, mock_graph, client):
        """Test getting network metrics."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_assets"] == 2
        assert data["total_relationships"] == 1
        assert data["avg_degree"] == 0.5
        assert data["max_degree"] == 1
        assert data["network_density"] == 0.5
        
    @patch("api.main.get_graph")
    def test_get_metrics_asset_class_counts(self, mock_get_graph, mock_graph, client):
        """Test that metrics include asset class counts."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "asset_classes" in data
        assert "EQUITY" in data["asset_classes"]
        assert "FIXED_INCOME" in data["asset_classes"]
        assert data["asset_classes"]["EQUITY"] == 1
        assert data["asset_classes"]["FIXED_INCOME"] == 1
        
    @patch("api.main.get_graph")
    def test_get_metrics_error_handling(self, mock_get_graph, client):
        """Test error handling in metrics endpoint."""
        mock_get_graph.side_effect = Exception("Calculation error")
        
        response = client.get("/api/metrics")
        assert response.status_code == 500


class TestVisualizationEndpoint:
    """Test cases for the visualization endpoint."""
    
    @patch("api.main.get_graph")
    def test_get_visualization_data(self, mock_get_graph, mock_graph, client):
        """Test getting 3D visualization data."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/visualization")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        
    @patch("api.main.get_graph")
    def test_get_visualization_node_structure(self, mock_get_graph, mock_graph, client):
        """Test that visualization nodes have correct structure."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/visualization")
        data = response.json()
        node = data["nodes"][0]
        assert "id" in node
        assert "name" in node
        assert "symbol" in node
        assert "asset_class" in node
        assert "x" in node
        assert "y" in node
        assert "z" in node
        assert "color" in node
        assert "size" in node
        
    @patch("api.main.get_graph")
    def test_get_visualization_edge_structure(self, mock_get_graph, mock_graph, client):
        """Test that visualization edges have correct structure."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/visualization")
        data = response.json()
        edge = data["edges"][0]
        assert "source" in edge
        assert "target" in edge
        assert "relationship_type" in edge
        assert "strength" in edge
        assert 0 <= edge["strength"] <= 1
        
    @patch("api.main.get_graph")
    def test_get_visualization_coordinates_are_floats(self, mock_get_graph, mock_graph, client):
        """Test that visualization coordinates are properly converted to floats."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/visualization")
        data = response.json()
        for node in data["nodes"]:
            assert isinstance(node["x"], float)
            assert isinstance(node["y"], float)
            assert isinstance(node["z"], float)


class TestMetadataEndpoints:
    """Test cases for metadata endpoints."""
    
    def test_get_asset_classes(self, client):
        """Test getting list of available asset classes."""
        response = client.get("/api/asset-classes")
        assert response.status_code == 200
        data = response.json()
        assert "asset_classes" in data
        assert isinstance(data["asset_classes"], list)
        assert "EQUITY" in data["asset_classes"]
        assert "FIXED_INCOME" in data["asset_classes"]
        assert "COMMODITY" in data["asset_classes"]
        assert "CURRENCY" in data["asset_classes"]
        
    @patch("api.main.get_graph")
    def test_get_sectors(self, mock_get_graph, mock_graph, client):
        """Test getting list of unique sectors."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/sectors")
        assert response.status_code == 200
        data = response.json()
        assert "sectors" in data
        assert isinstance(data["sectors"], list)
        assert "Technology" in data["sectors"]
        
    @patch("api.main.get_graph")
    def test_get_sectors_sorted(self, mock_get_graph, mock_graph, client):
        """Test that sectors are returned sorted."""
        # Add more sectors
        equity2 = Equity(
            id="TEST_MSFT",
            symbol="MSFT",
            name="Microsoft",
            asset_class=AssetClass.EQUITY,
            sector="Technology",
            price=300.00,
            market_cap=2.2e12,
            currency="USD"
        )
        equity3 = Equity(
            id="TEST_JPM",
            symbol="JPM",
            name="JPMorgan",
            asset_class=AssetClass.EQUITY,
            sector="Finance",
            price=150.00,
            market_cap=400e9,
            currency="USD"
        )
        mock_graph.assets["TEST_MSFT"] = equity2
        mock_graph.assets["TEST_JPM"] = equity3
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/sectors")
        data = response.json()
        sectors = data["sectors"]
        assert sectors == sorted(sectors)
        assert "Finance" in sectors
        assert "Technology" in sectors
        
    @patch("api.main.get_graph")
    def test_get_sectors_empty_graph(self, mock_get_graph, client):
        """Test getting sectors from empty graph."""
        empty_graph = Mock(spec=AssetRelationshipGraph)
        empty_graph.assets = {}
        mock_get_graph.return_value = empty_graph
        
        response = client.get("/api/sectors")
        assert response.status_code == 200
        data = response.json()
        assert data["sectors"] == []


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""
    
    @patch("api.main.get_graph")
    def test_asset_with_none_market_cap(self, mock_get_graph, mock_graph, client):
        """Test handling of assets with None market_cap."""
        equity = Equity(
            id="TEST_SMALL",
            symbol="SMALL",
            name="Small Company",
            asset_class=AssetClass.EQUITY,
            sector="Technology",
            price=1.00,
            market_cap=None,
            currency="USD"
        )
        mock_graph.assets["TEST_SMALL"] = equity
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_SMALL")
        assert response.status_code == 200
        data = response.json()
        assert data["market_cap"] is None
        
    @patch("api.main.get_graph")
    def test_asset_with_none_optional_fields(self, mock_get_graph, mock_graph, client):
        """Test that None values are not included in additional_fields."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_AAPL")
        data = response.json()
        # Check that only non-None fields are included
        for _key, value in data["additional_fields"].items():
            assert value is not None
            
    @patch("api.main.get_graph")
    def test_empty_relationship_list(self, mock_get_graph, mock_graph, client):
        """Test asset with relationships key but empty list."""
        mock_graph.relationships["TEST_AAPL"] = []
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets/TEST_AAPL/relationships")
        assert response.status_code == 200
        data = response.json()
        assert data == []
        
    @patch("api.main.get_graph")
    def test_relationship_strength_bounds(self, mock_get_graph, mock_graph, client):
        """Test that relationship strength is within valid bounds."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/relationships")
        data = response.json()
        for relationship in data:
            assert 0 <= relationship["strength"] <= 1


class TestGraphInitialization:
    """Test cases for graph initialization."""
    
    @patch("api.main.graph", None)
    @patch("api.main.create_real_database")
    def test_lazy_graph_initialization(self, mock_create_db, client):
        """Test that graph is initialized on first access."""
        mock_graph = Mock(spec=AssetRelationshipGraph)
        mock_graph.assets = {}
        mock_graph.relationships = {}
        mock_create_db.return_value = mock_graph
        
        # First request should initialize graph
        response = client.get("/api/assets")
        assert response.status_code == 200
        mock_create_db.assert_called_once()
        mock_graph.build_relationships.assert_called_once()
        
    @patch("api.main.get_graph")
    def test_graph_persists_across_requests(self, mock_get_graph, mock_graph, client):
        """Test that graph instance persists across requests."""
        mock_get_graph.return_value = mock_graph
        
        # Make multiple requests
        client.get("/api/assets")
        client.get("/api/metrics")
        client.get("/api/relationships")
        
        # Verify graph was accessed but not recreated
        assert mock_get_graph.call_count == 3


class TestResponseModels:
    """Test cases for response model validation."""
    
    @patch("api.main.get_graph")
    def test_asset_response_schema(self, mock_get_graph, mock_graph, client):
        """Test that asset responses match the AssetResponse model."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/assets")
        data = response.json()
        for asset in data:
            assert "id" in asset
            assert "symbol" in asset
            assert "name" in asset
            assert "asset_class" in asset
            assert "sector" in asset
            assert "price" in asset
            assert "currency" in asset
            assert "additional_fields" in asset
            assert isinstance(asset["price"], (int, float))
            
    @patch("api.main.get_graph")
    def test_relationship_response_schema(self, mock_get_graph, mock_graph, client):
        """Test that relationship responses match the RelationshipResponse model."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/relationships")
        data = response.json()
        for rel in data:
            assert "source_id" in rel
            assert "target_id" in rel
            assert "relationship_type" in rel
            assert "strength" in rel
            assert isinstance(rel["strength"], (int, float))
            
    @patch("api.main.get_graph")
    def test_metrics_response_schema(self, mock_get_graph, mock_graph, client):
        """Test that metrics responses match the MetricsResponse model."""
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/metrics")
        data = response.json()
        assert isinstance(data["total_assets"], int)
        assert isinstance(data["total_relationships"], int)
        assert isinstance(data["asset_classes"], dict)
        assert isinstance(data["avg_degree"], (int, float))
        assert isinstance(data["max_degree"], int)
        assert isinstance(data["network_density"], (int, float))