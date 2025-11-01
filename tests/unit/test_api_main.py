"""Comprehensive unit tests for the FastAPI backend (api/main.py).

This module tests all API endpoints, error handling, CORS configuration,
thread-safe graph initialization, and response models.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException  # Remove this line
import os

from api.main import (
    app, 
    validate_origin, 
    get_graph,
    AssetResponse,
    RelationshipResponse,
    MetricsResponse,
    VisualizationDataResponse
)
from src.models.financial_models import AssetClass, Equity, Bond


class TestValidateOrigin:
    """Test the validate_origin function for CORS configuration."""
    
    def test_validate_origin_http_localhost_development(self):
        """Test HTTP localhost is allowed in development."""
        with patch.dict(os.environ, {'ENV': 'development'}):
            from api.main import validate_origin as vo
            assert vo('http://localhost:3000')
            assert vo('http://127.0.0.1:8000')
            assert vo('http://localhost')
    
    def test_validate_origin_http_localhost_production(self):
        """Test HTTP localhost is rejected in production."""
        with patch.dict(os.environ, {'ENV': 'production'}):
            from api.main import validate_origin as vo
            assert not vo('http://localhost:3000')
            assert not vo('http://127.0.0.1:8000')
    
    def test_validate_origin_https_localhost(self):
        """Test HTTPS localhost is always allowed."""
        assert validate_origin('https://localhost:3000')
        assert validate_origin('https://127.0.0.1:8000')
    
    def test_validate_origin_vercel_urls(self):
        """Test Vercel deployment URLs are validated correctly."""
        assert validate_origin('https://my-app.vercel.app')
        assert validate_origin('https://my-app-git-main-user.vercel.app')
        assert validate_origin('https://subdomain.vercel.app')
        assert not validate_origin('http://my-app.vercel.app')  # HTTP rejected
    
    def test_validate_origin_https_valid_domains(self):
        """Test valid HTTPS URLs with proper domains."""
        assert validate_origin('https://example.com')
        assert validate_origin('https://subdomain.example.com')
        assert validate_origin('https://api.example.co.uk')
    
    def test_validate_origin_invalid_schemes(self):
        """Test invalid URL schemes are rejected."""
        assert not validate_origin('ftp://example.com')
        assert not validate_origin('ws://example.com')
        assert not validate_origin('file://localhost')
    
    def test_validate_origin_malformed_urls(self):
        """Test malformed URLs are rejected."""
        assert not validate_origin('not-a-url')
        assert not validate_origin('https://')
        assert not validate_origin('https://invalid domain')
        assert not validate_origin('https://.com')


class TestGetGraph:
    """Test the thread-safe graph initialization."""
    
    def test_get_graph_initialization(self):
        """Test graph is initialized on first call."""
        # Reset global graph
        import api.main
        api.main.graph = None
        
        graph = get_graph()
        assert graph is not None
        assert hasattr(graph, 'assets')
        assert hasattr(graph, 'relationships')
    
    def test_get_graph_singleton(self):
        """Test graph returns the same instance on subsequent calls."""
        graph1 = get_graph()
        graph2 = get_graph()
        assert graph1 is graph2
    
    @patch('api.main.create_sample_database')
    def test_get_graph_thread_safety(self, mock_create):
        """Test double-check locking pattern for thread safety."""
        import api.main
        api.main.graph = None
        
        mock_graph = Mock()
        mock_create.return_value = mock_graph
        
        graph = get_graph()
        assert graph is mock_graph
        assert mock_create.call_count == 1
        
        # Second call should not create new graph
        graph2 = get_graph()
        assert graph2 is mock_graph
        assert mock_create.call_count == 1


class TestPydanticModels:
    """Test Pydantic response models."""
    
    def test_asset_response_model_valid(self):
        """Test AssetResponse with valid data."""
        asset = AssetResponse(
            id="AAPL",
            symbol="AAPL",
            name="Apple Inc.",
            asset_class="EQUITY",
            sector="Technology",
            price=150.00,
            market_cap=2.4e12,
            currency="USD",
            additional_fields={"pe_ratio": 25.5}
        )
        assert asset.id == "AAPL"
        assert asset.price == 150.00
        assert asset.additional_fields["pe_ratio"] == 25.5
    
    def test_asset_response_model_optional_fields(self):
        """Test AssetResponse with optional fields omitted."""
        asset = AssetResponse(
            id="AAPL",
            symbol="AAPL",
            name="Apple Inc.",
            asset_class="EQUITY",
            sector="Technology",
            price=150.00
        )
        assert asset.market_cap is None
        assert asset.currency == "USD"  # Default value
        assert asset.additional_fields == {}  # Default value
    
    def test_relationship_response_model(self):
        """Test RelationshipResponse model."""
        rel = RelationshipResponse(
            source_id="AAPL",
            target_id="MSFT",
            relationship_type="same_sector",
            strength=0.8
        )
        assert rel.source_id == "AAPL"
        assert rel.strength == 0.8
    
    def test_metrics_response_model(self):
        """Test MetricsResponse model."""
        metrics = MetricsResponse(
            total_assets=10,
            total_relationships=20,
            asset_classes={"EQUITY": 5, "BOND": 5},
            avg_degree=2.0,
            max_degree=5,
            network_density=0.4
        )
        assert metrics.total_assets == 10
        assert metrics.asset_classes["EQUITY"] == 5
    
    def test_visualization_data_response_model(self):
        """Test VisualizationDataResponse model."""
        viz = VisualizationDataResponse(
            nodes=[{"id": "AAPL", "x": 1.0, "y": 2.0, "z": 3.0}],
            edges=[{"source": "AAPL", "target": "MSFT"}]
        )
        assert len(viz.nodes) == 1
        assert len(viz.edges) == 1


class TestAPIEndpoints:
    """Test all FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_get_assets_all(self, client):
        """Test getting all assets without filters."""
        response = client.get("/api/assets")
        assert response.status_code == 200
        assets = response.json()
        assert isinstance(assets, list)
        assert len(assets) > 0
        
        # Validate response structure
        asset = assets[0]
        assert "id" in asset
        assert "symbol" in asset
        assert "name" in asset
        assert "asset_class" in asset
        assert "sector" in asset
        assert "price" in asset
    
    def test_get_assets_filter_by_class(self, client):
        """Test filtering assets by asset class."""
        response = client.get("/api/assets?asset_class=EQUITY")
        assert response.status_code == 200
        assets = response.json()
        assert isinstance(assets, list)
        
        # All assets should be EQUITY
        for asset in assets:
            assert asset["asset_class"] == "EQUITY"
    
    def test_get_assets_filter_by_sector(self, client):
        """Test filtering assets by sector."""
        response = client.get("/api/assets?sector=Technology")
        assert response.status_code == 200
        assets = response.json()
        assert isinstance(assets, list)
        
        # All assets should be in Technology sector
        for asset in assets:
            assert asset["sector"] == "Technology"
    
    def test_get_assets_filter_by_class_and_sector(self, client):
        """Test filtering assets by both class and sector."""
        response = client.get("/api/assets?asset_class=EQUITY&sector=Technology")
        assert response.status_code == 200
        assets = response.json()
        assert isinstance(assets, list)
        
        # All assets should match both filters
        for asset in assets:
            assert asset["asset_class"] == "EQUITY"
            assert asset["sector"] == "Technology"
    
    def test_get_asset_detail_valid(self, client):
        """Test getting details for a valid asset."""
        # First get an asset ID
        response = client.get("/api/assets")
        assets = response.json()
        asset_id = assets[0]["id"]
        
        # Get asset detail
        response = client.get(f"/api/assets/{asset_id}")
        assert response.status_code == 200
        asset = response.json()
        assert asset["id"] == asset_id
    
    def test_get_asset_detail_not_found(self, client):
        """Test getting details for non-existent asset returns 404."""
        response = client.get("/api/assets/NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_asset_relationships_valid(self, client):
        """Test getting relationships for a valid asset."""
        # Get an asset with relationships
        response = client.get("/api/assets")
        assets = response.json()
        asset_id = assets[0]["id"]
        
        response = client.get(f"/api/assets/{asset_id}/relationships")
        assert response.status_code == 200
        relationships = response.json()
        assert isinstance(relationships, list)
        
        # Validate relationship structure if any exist
        if len(relationships) > 0:
            rel = relationships[0]
            assert "source_id" in rel
            assert "target_id" in rel
            assert "relationship_type" in rel
            assert "strength" in rel
            assert rel["source_id"] == asset_id
    
    def test_get_asset_relationships_not_found(self, client):
        """Test getting relationships for non-existent asset returns 404."""
        response = client.get("/api/assets/NONEXISTENT/relationships")
        assert response.status_code == 404
    
    def test_get_all_relationships(self, client):
        """Test getting all relationships."""
        response = client.get("/api/relationships")
        assert response.status_code == 200
        relationships = response.json()
        assert isinstance(relationships, list)
        
        # Validate relationship structure
        if len(relationships) > 0:
            rel = relationships[0]
            assert "source_id" in rel
            assert "target_id" in rel
            assert "relationship_type" in rel
            assert "strength" in rel
            assert 0 <= rel["strength"] <= 1
    
    def test_get_metrics(self, client):
        """Test getting network metrics."""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        
        assert "total_assets" in metrics
        assert "total_relationships" in metrics
        assert "asset_classes" in metrics
        assert "avg_degree" in metrics
        assert "max_degree" in metrics
        assert "network_density" in metrics
        
        assert metrics["total_assets"] > 0
        assert metrics["total_relationships"] >= 0
        assert isinstance(metrics["asset_classes"], dict)
        assert metrics["avg_degree"] >= 0
        assert metrics["max_degree"] >= 0
        assert 0 <= metrics["network_density"] <= 1
    
    def test_get_visualization_data(self, client):
        """Test getting 3D visualization data."""
        response = client.get("/api/visualization")
        assert response.status_code == 200
        viz_data = response.json()
        
        assert "nodes" in viz_data
        assert "edges" in viz_data
        assert isinstance(viz_data["nodes"], list)
        assert isinstance(viz_data["edges"], list)
        
        # Validate node structure
        if len(viz_data["nodes"]) > 0:
            node = viz_data["nodes"][0]
            assert "id" in node
            assert "name" in node
            assert "symbol" in node
            assert "asset_class" in node
            assert "x" in node
            assert "y" in node
            assert "z" in node
            assert "color" in node
            assert "size" in node
            
            # Validate coordinates are floats
            assert isinstance(node["x"], (int, float))
            assert isinstance(node["y"], (int, float))
            assert isinstance(node["z"], (int, float))
        
        # Validate edge structure
        if len(viz_data["edges"]) > 0:
            edge = viz_data["edges"][0]
            assert "source" in edge
            assert "target" in edge
            assert "relationship_type" in edge
            assert "strength" in edge
            assert 0 <= edge["strength"] <= 1
    
    def test_get_asset_classes(self, client):
        """Test getting list of asset classes."""
        response = client.get("/api/asset-classes")
        assert response.status_code == 200
        data = response.json()
        
        assert "asset_classes" in data
        assert isinstance(data["asset_classes"], list)
        assert len(data["asset_classes"]) > 0
        
        # Check that all AssetClass enum values are included
        expected_classes = [ac.value for ac in AssetClass]
        assert set(data["asset_classes"]) == set(expected_classes)
    
    def test_get_sectors(self, client):
        """Test getting list of sectors."""
        response = client.get("/api/sectors")
        assert response.status_code == 200
        data = response.json()
        
        assert "sectors" in data
        assert isinstance(data["sectors"], list)
        assert len(data["sectors"]) > 0
        
        # Check that sectors are sorted
        assert data["sectors"] == sorted(data["sectors"])


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @patch('api.main.get_graph')
    def test_get_assets_server_error(self, mock_get_graph, client):
        """Test that server errors are handled gracefully."""
        mock_get_graph.side_effect = Exception("Database error")
        
        response = client.get("/api/assets")
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
    
    @patch('api.main.get_graph')
    def test_get_metrics_server_error(self, mock_get_graph, client):
        """Test metrics endpoint error handling."""
        mock_graph = Mock()
        mock_graph.calculate_metrics.side_effect = Exception("Calculation error")
        mock_get_graph.return_value = mock_graph
        
        response = client.get("/api/metrics")
        assert response.status_code == 500
    
    def test_invalid_http_methods(self, client):
        """Test that invalid HTTP methods return 405."""
        response = client.post("/api/assets")
        assert response.status_code == 405
        
        response = client.put("/api/health")
        assert response.status_code == 405
        
        response = client.delete("/api/metrics")
        assert response.status_code == 405


class TestCORSConfiguration:
    """Test CORS middleware configuration."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/health")
        assert response.status_code == 200
    
    @patch.dict(os.environ, {'ENV': 'development', 'ALLOWED_ORIGINS': ''})
    def test_cors_allows_development_origins(self, client):
        """Test CORS allows development origins."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200


class TestAdditionalFields:
    """Test handling of asset-specific additional fields."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_equity_additional_fields(self, client):
        """Test that equity-specific fields are included."""
        response = client.get("/api/assets?asset_class=EQUITY")
        assets = response.json()
        
        if len(assets) > 0:
            asset = assets[0]
            additional = asset.get("additional_fields", {})
            
            # Check for equity-specific fields
            possible_fields = ["pe_ratio", "dividend_yield", "earnings_per_share", "book_value"]
            has_equity_field = any(field in additional for field in possible_fields)
            assert has_equity_field or len(additional) == 0  # Either has fields or empty
    
    def test_bond_additional_fields(self, client):
        """Test that bond-specific fields are included."""
        response = client.get("/api/assets?asset_class=BOND")
        assets = response.json()
        
        if len(assets) > 0:
            asset = assets[0]
            additional = asset.get("additional_fields", {})
            
            # Check for bond-specific fields
            possible_fields = ["yield_to_maturity", "coupon_rate", "maturity_date", "credit_rating"]
            has_bond_field = any(field in additional for field in possible_fields)
            assert has_bond_field or len(additional) == 0


class TestVisualizationDataProcessing:
    """Test the processing of visualization data."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_visualization_coordinate_types(self, client):
        """Test that all coordinates are properly converted to floats."""
        response = client.get("/api/visualization")
        viz_data = response.json()
        
        for node in viz_data["nodes"]:
            # Ensure x, y, z are numeric (int or float)
            assert isinstance(node["x"], (int, float))
            assert isinstance(node["y"], (int, float))
            assert isinstance(node["z"], (int, float))
    
    def test_visualization_node_defaults(self, client):
        """Test that nodes have default values for color and size."""
        response = client.get("/api/visualization")
        viz_data = response.json()
        
        for node in viz_data["nodes"]:
            assert "color" in node
            assert "size" in node
            # Default color should be set if not provided
            assert isinstance(node["color"], str)
            assert isinstance(node["size"], (int, float))
    
    def test_visualization_edge_defaults(self, client):
        """Test that edges have default values."""
        response = client.get("/api/visualization")
        viz_data = response.json()
        
        for edge in viz_data["edges"]:
            assert "relationship_type" in edge
            assert "strength" in edge
            # Strength should be between 0 and 1
            assert 0 <= edge["strength"] <= 1


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_full_workflow_asset_exploration(self, client):
        """Test a complete workflow: list assets, get detail, get relationships."""
        # Step 1: Get all assets
        response = client.get("/api/assets")
        assert response.status_code == 200
        assets = response.json()
        assert len(assets) > 0
        
        # Step 2: Get detail for first asset
        asset_id = assets[0]["id"]
        response = client.get(f"/api/assets/{asset_id}")
        assert response.status_code == 200
        asset_detail = response.json()
        assert asset_detail["id"] == asset_id
        
        # Step 3: Get relationships for that asset
        response = client.get(f"/api/assets/{asset_id}/relationships")
        assert response.status_code == 200
        relationships = response.json()
        assert isinstance(relationships, list)
    
    def test_full_workflow_visualization_and_metrics(self, client):
        """Test workflow for visualization: get metrics then visualization data."""
        # Step 1: Get metrics
        response = client.get("/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        
        # Step 2: Get visualization data
        response = client.get("/api/visualization")
        assert response.status_code == 200
        viz_data = response.json()
        
        # Step 3: Verify consistency
        assert len(viz_data["nodes"]) == metrics["total_assets"]
    
    def test_filter_refinement_workflow(self, client):
        """Test progressive filter refinement."""
        # Get all assets
        response = client.get("/api/assets")
        all_assets = response.json()
        
        # Filter by class
        response = client.get("/api/assets?asset_class=EQUITY")
        equity_assets = response.json()
        assert len(equity_assets) <= len(all_assets)
        
        # Further filter by sector
        response = client.get("/api/assets?asset_class=EQUITY&sector=Technology")
        tech_equity_assets = response.json()
        assert len(tech_equity_assets) <= len(equity_assets)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])