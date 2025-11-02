"""Unit tests for API main module.

This module contains unit tests for the FastAPI application including:
- Graph initialization during app startup
"""

from fastapi.testclient import TestClient


class TestAPIMain:
    """Test cases for the API main module."""

    def test_graph_initialization(self):
        """Test graph is initialized during app startup."""
        from api.main import app
        
        # Create TestClient which triggers startup events
        with TestClient(app):
            # Import api.main to access the graph
            import api.main
            assert api.main.graph is not None
            assert hasattr(api.main.graph, 'assets')
            assert hasattr(api.main.graph, 'relationships')
