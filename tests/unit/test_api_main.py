"""Comprehensive unit tests for the FastAPI backend (api/main.py).

This module tests all API endpoints, CORS configuration, error handling,
thread-safe graph initialization, and edge cases.
"""

import pytest
import threading
import time
from unittest.mock import patch
from fastapi.testclient import TestClient

from api.main import (
    app,
    validate_origin,
    get_graph,
    ENV,
    graph,
    graph_lock
)
from src.models.financial_models import Bond
from src.logic.asset_graph import AssetRelationshipGraph


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_graph():
    """Reset the global graph instance before and after tests."""
    global graph
    original_graph = graph
    graph = None
    yield
    graph = original_graph


class TestValidateOrigin:
    """Test cases for the validate_origin function."""

    def test_validate_http_localhost_development(self):
        """Test that HTTP localhost is allowed in development."""
        with patch('api.main.ENV', 'development'):
            assert validate_origin('http://localhost:3000') is True
            assert validate_origin('http://127.0.0.1:8000') is True
            assert validate_origin('http://localhost') is True

    def test_validate_http_localhost_production(self):
        """Test that HTTP localhost is rejected in production."""
        with patch('api.main.ENV', 'production'):
            assert validate_origin('http://localhost:3000') is False
            assert validate_origin('http://127.0.0.1:8000') is False

    def test_validate_https_localhost(self):
        """Test that HTTPS localhost is always allowed."""
        with patch('api.main.ENV', 'production'):
            assert validate_origin('https://localhost:3000') is True
            assert validate_origin('https://127.0.0.1:8000') is True

    def test_validate_vercel_urls(self):
        """Test that Vercel deployment URLs are allowed."""
        assert validate_origin('https://my-app.vercel.app') is True
        assert validate_origin('https://my-app-git-branch-user.vercel.app') is True
        assert validate_origin('https://my-app-123abc.vercel.app') is True

    def test_validate_custom_https_domains(self):
        """Test that valid HTTPS domains are allowed."""
        assert validate_origin('https://example.com') is True
        assert validate_origin('https://api.example.com') is True
        assert validate_origin('https://sub.domain.example.co.uk') is True

    def test_reject_invalid_origins(self):
        """Test that invalid origins are rejected."""
        assert validate_origin('http://evil.com') is False  # HTTP in production context
        assert validate_origin('ftp://example.com') is False
        assert validate_origin('javascript:alert(1)') is False
        assert validate_origin('') is False
        assert validate_origin('not-a-url') is False
        assert validate_origin('https://') is False

    def test_reject_malformed_vercel_urls(self):
        """Test that malformed Vercel URLs are rejected."""
        assert validate_origin('https://vercel.app') is False  # Missing subdomain
        assert validate_origin('http://my-app.vercel.app') is False  # HTTP


class TestGetGraph:
    """Test cases for the get_graph function with thread-safety."""

    def test_get_graph_creates_instance(self, _reset_graph):
        """Test that get_graph creates a graph instance."""
        result = get_graph()
        assert isinstance(result, AssetRelationshipGraph)
        assert len(result.assets) > 0

    def test_get_graph_singleton_behavior(self, _reset_graph):
        """Test that get_graph returns the same instance."""
        graph1 = get_graph()
        graph2 = get_graph()
        assert graph1 is graph2

    def test_get_graph_thread_safety(self, _reset_graph):
        """Test that get_graph is thread-safe."""
        results = []
        
        def get_and_store():
            g = get_graph()
            results.append(id(g))
        
        threads = [threading.Thread(target=get_and_store) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should get the same graph instance
        assert len(set(results)) == 1

    @patch('api.main.create_sample_database')
    def test_get_graph_initialization_called_once(self, mock_create, _reset_graph):
        """Test that sample database is created only once."""
        mock_graph = AssetRelationshipGraph()
        mock_create.return_value = mock_graph
        
        # Call multiple times
        get_graph()
        get_graph()
        get_graph()
        
        # Should only be called once
        assert mock_create.call_count == 1


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_endpoint_success(self, client):
        """Test that root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"

    def test_root_endpoint_structure(self, client):
        """Test that root endpoint has correct structure."""
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "assets" in endpoints
        assert "relationships" in endpoints
        assert "metrics" in endpoints
        assert "visualization" in endpoints


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""

    def test_health_check_success(self, client):
        """Test that health check returns healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_check_method_not_allowed(self, client):
        """Test that only GET is allowed for health check."""
        response = client.post("/api/health")
        assert response.status_code == 405


class TestAssetsEndpoint:
    """Test cases for the assets endpoints."""

    def test_get_all_assets_success(self, client):
        """Test getting all assets without filters."""
        response = client.get("/api/assets")
        assert response.status_code == 200
        assets = response.json()
        assert isinstance(assets, list)
        assert len(assets) > 0
        
        # Validate asset structure
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
        
        # All returned assets should be equities
        for asset in assets:
            assert asset["asset_class"] == "EQUITY"

    def test_get_assets_filter_by_sector(self, client):
        """Test filtering assets by sector."""
        # First get all assets to find a valid sector
        all_assets = client.get("/api/assets").json()
        if all_assets:
            sector = all_assets[0]["sector"]
            response = client.get(f"/api/assets?sector={sector}")
            assert response.status_code == 200
            assets = response.json()
            
            # All returned assets should be in the specified sector
            for asset in assets:
                assert asset["sector"] == sector

    def test_get_assets_filter_combined(self, client):
        """Test filtering assets by both class and sector."""
        response = client.get("/api/assets?asset_class=EQUITY&sector=Technology")
        assert response.status_code == 200
        assets = response.json()
        
        for asset in assets:
            assert asset["asset_class"] == "EQUITY"
            # Note: May be empty if no Technology equities exist

    def test_get_assets_invalid_class(self, client):
        """Test filtering with invalid asset class."""
        response = client.get("/api/assets?asset_class=INVALID_CLASS")
        assert response.status_code == 200
        assets = response.json()
        assert len(assets) == 0

    def test_get_asset_detail_success(self, client):
        """Test getting details for a specific asset."""
        # First get list of assets
        assets = client.get("/api/assets").json()
        if assets:
            asset_id = assets[0]["id"]
            response = client.get(f"/api/assets/{asset_id}")
            assert response.status_code == 200
            asset = response.json()
            assert asset["id"] == asset_id
            assert "additional_fields" in asset

    def test_get_asset_detail_not_found(self, client):
        """Test getting details for non-existent asset."""
        response = client.get("/api/assets/NONEXISTENT_ASSET")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_asset_relationships_success(self, client):
        """Test getting relationships for a specific asset."""
        # First get list of assets
        assets = client.get("/api/assets").json()
        if assets:
            asset_id = assets[0]["id"]
            response = client.get(f"/api/assets/{asset_id}/relationships")
            assert response.status_code == 200
            relationships = response.json()
            assert isinstance(relationships, list)
            
            # Validate relationship structure if any exist
            if relationships:
                rel = relationships[0]
                assert "source_id" in rel
                assert "target_id" in rel
                assert "relationship_type" in rel
                assert "strength" in rel
                assert rel["source_id"] == asset_id

    def test_get_asset_relationships_not_found(self, client):
        """Test getting relationships for non-existent asset."""
        response = client.get("/api/assets/NONEXISTENT/relationships")
        assert response.status_code == 404


class TestRelationshipsEndpoint:
    """Test cases for the relationships endpoint."""

    def test_get_all_relationships_success(self, client):
        """Test getting all relationships."""
        response = client.get("/api/relationships")
        assert response.status_code == 200
        relationships = response.json()
        assert isinstance(relationships, list)
        
        # Validate structure if relationships exist
        if relationships:
            rel = relationships[0]
            assert "source_id" in rel
            assert "target_id" in rel
            assert "relationship_type" in rel
            assert "strength" in rel
            assert 0 <= rel["strength"] <= 1


class TestMetricsEndpoint:
    """Test cases for the metrics endpoint."""

    def test_get_metrics_success(self, client):
        """Test getting network metrics."""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        
        # Validate metrics structure
        assert "total_assets" in metrics
        assert "total_relationships" in metrics
        assert "asset_classes" in metrics
        assert "avg_degree" in metrics
        assert "max_degree" in metrics
        assert "network_density" in metrics
        
        # Validate types and ranges
        assert isinstance(metrics["total_assets"], int)
        assert isinstance(metrics["total_relationships"], int)
        assert isinstance(metrics["asset_classes"], dict)
        assert metrics["total_assets"] > 0
        assert metrics["avg_degree"] >= 0
        assert metrics["max_degree"] >= 0
        assert 0 <= metrics["network_density"] <= 1

    def test_metrics_asset_classes_sum(self, client):
        """Test that asset class counts sum to total assets."""
        response = client.get("/api/metrics")
        metrics = response.json()
        
        total_from_classes = sum(metrics["asset_classes"].values())
        assert total_from_classes == metrics["total_assets"]


class TestVisualizationEndpoint:
    """Test cases for the visualization endpoint."""

    def test_get_visualization_data_success(self, client):
        """Test getting 3D visualization data."""
        response = client.get("/api/visualization")
        assert response.status_code == 200
        viz_data = response.json()
        
        # Validate structure
        assert "nodes" in viz_data
        assert "edges" in viz_data
        assert isinstance(viz_data["nodes"], list)
        assert isinstance(viz_data["edges"], list)

    def test_visualization_nodes_structure(self, client):
        """Test that visualization nodes have correct structure."""
        response = client.get("/api/visualization")
        viz_data = response.json()
        
        if viz_data["nodes"]:
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
            
            # Validate types
            assert isinstance(node["x"], (int, float))
            assert isinstance(node["y"], (int, float))
            assert isinstance(node["z"], (int, float))
            assert isinstance(node["size"], (int, float))

    def test_visualization_edges_structure(self, client):
        """Test that visualization edges have correct structure."""
        response = client.get("/api/visualization")
        viz_data = response.json()
        
        if viz_data["edges"]:
            edge = viz_data["edges"][0]
            assert "source" in edge
            assert "target" in edge
            assert "relationship_type" in edge
            assert "strength" in edge
            assert 0 <= edge["strength"] <= 1

    def test_visualization_nodes_match_assets(self, client):
        """Test that visualization nodes count matches total assets."""
        assets_response = client.get("/api/assets")
        viz_response = client.get("/api/visualization")
        
        total_assets = len(assets_response.json())
        total_nodes = len(viz_response.json()["nodes"])
        
        assert total_nodes == total_assets


class TestMetadataEndpoints:
    """Test cases for metadata endpoints."""

    def test_get_asset_classes_success(self, client):
        """Test getting list of asset classes."""
        response = client.get("/api/asset-classes")
        assert response.status_code == 200
        data = response.json()
        
        assert "asset_classes" in data
        assert isinstance(data["asset_classes"], list)
        assert len(data["asset_classes"]) > 0
        
        # Should include standard asset classes
        asset_classes = data["asset_classes"]
        expected_classes = ["EQUITY", "FIXED_INCOME", "COMMODITY", "CURRENCY"]
        for expected in expected_classes:
            assert expected in asset_classes

    def test_get_sectors_success(self, client):
        """Test getting list of sectors."""
        response = client.get("/api/sectors")
        assert response.status_code == 200
        data = response.json()
        
        assert "sectors" in data
        assert isinstance(data["sectors"], list)
        assert len(data["sectors"]) > 0
        
        # Sectors should be sorted
        sectors = data["sectors"]
        assert sectors == sorted(sectors)


class TestCORSConfiguration:
    """Test cases for CORS middleware configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/api/health", headers={
            "Origin": "http://localhost:3000"
        })
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_credentials(self, client):
        """Test that CORS allows credentials."""
        response = client.options("/api/assets", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        # Check if credentials are allowed
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"] == "true"


class TestErrorHandling:
    """Test cases for error handling and edge cases."""

    def test_invalid_endpoint_404(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/api/invalid_endpoint")
        assert response.status_code == 404

    def test_invalid_method_405(self, client):
        """Test that invalid methods return 405."""
        response = client.delete("/api/assets")
        assert response.status_code == 405

    def test_malformed_asset_id_handling(self, client):
        """Test handling of malformed asset IDs."""
        response = client.get("/api/assets/../../../etc/passwd")
        # Should either 404 or sanitize the path
        assert response.status_code in [404, 422]

    @patch('api.main.get_graph')
    def test_api_error_handling(self, mock_get_graph, client):
        """Test that API errors are handled gracefully."""
        mock_get_graph.side_effect = Exception("Database error")
        
        response = client.get("/api/assets")
        assert response.status_code == 500
        assert "detail" in response.json()


class TestPydanticModels:
    """Test cases for Pydantic response models."""

    def test_asset_response_model(self, client):
        """Test that AssetResponse model validates correctly."""
        response = client.get("/api/assets")
        assets = response.json()
        
        if assets:
            asset = assets[0]
            # Required fields
            assert isinstance(asset["id"], str)
            assert isinstance(asset["symbol"], str)
            assert isinstance(asset["name"], str)
            assert isinstance(asset["asset_class"], str)
            assert isinstance(asset["sector"], str)
            assert isinstance(asset["price"], (int, float))
            assert isinstance(asset["currency"], str)
            
            # Optional fields
            if asset.get("market_cap") is not None:
                assert isinstance(asset["market_cap"], (int, float))

    def test_relationship_response_model(self, client):
        """Test that RelationshipResponse model validates correctly."""
        response = client.get("/api/relationships")
        relationships = response.json()
        
        if relationships:
            rel = relationships[0]
            assert isinstance(rel["source_id"], str)
            assert isinstance(rel["target_id"], str)
            assert isinstance(rel["relationship_type"], str)
            assert isinstance(rel["strength"], (int, float))

    def test_metrics_response_model(self, client):
        """Test that MetricsResponse model validates correctly."""
        response = client.get("/api/metrics")
        metrics = response.json()
        
        assert isinstance(metrics["total_assets"], int)
        assert isinstance(metrics["total_relationships"], int)
        assert isinstance(metrics["asset_classes"], dict)
        assert isinstance(metrics["avg_degree"], (int, float))
        assert isinstance(metrics["max_degree"], int)
        assert isinstance(metrics["network_density"], (int, float))


class TestConcurrency:
    """Test cases for concurrent request handling."""

    def test_concurrent_requests(self, client):
        """Test that multiple concurrent requests work correctly."""
        import concurrent.futures
        
        def make_request():
            response = client.get("/api/assets")
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)

    def test_different_endpoints_concurrent(self, client):
        """Test concurrent requests to different endpoints."""
        import concurrent.futures
        
        endpoints = [
            "/api/assets",
            "/api/relationships",
            "/api/metrics",
            "/api/visualization",
            "/api/health"
        ]
        
        def make_request(endpoint):
            response = client.get(endpoint)
            return (endpoint, response.status_code)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints * 3]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for _, status in results)