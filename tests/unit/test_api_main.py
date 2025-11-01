"""Unit tests for API main module.

This module contains unit tests for the FastAPI application including:
- Graph initialization at module load
"""


class TestAPIMain:
    """Test cases for the API main module."""

    def test_graph_initialization(self):
        """Test graph is initialized at module load."""
        import api.main
        assert api.main.graph is not None
        assert hasattr(api.main.graph, 'assets')
        assert hasattr(api.main.graph, 'relationships')
