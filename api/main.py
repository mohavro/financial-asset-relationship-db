"""FastAPI backend for Financial Asset Relationship Database"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
# Remove the unused import statement for threading

from src.logic.asset_graph import AssetRelationshipGraph
# from src.data.real_data_fetcher import create_real_database
from src.models.financial_models import AssetClass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Asset Relationship API",
    description="REST API for Financial Asset Relationship Database",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
# Note: Update allowed origins for production deployment
import os
import re

# Determine environment (default to 'development' if not set)
ENV = os.getenv("ENV", "development").lower()

def validate_origin(origin: str) -> bool:
    """
    Check whether the provided origin URL is allowed by the application's CORS rules.
    
    Accepted origins include:
    - HTTPS origins for any localhost or 127.0.0.1 (with optional port).
    - HTTP localhost origins when ENV is "development" (with optional port).
    - Vercel preview deployment URLs (domains ending with `.vercel.app`).
    - Other well-formed HTTPS domains (standard domain names with a TLD).
    
    Parameters:
        origin (str): The origin URL to validate (e.g., "https://example.com" or "http://localhost:3000").
    
    Returns:
        bool: `True` if the origin matches an allowed pattern, `False` otherwise.
    """
    # Allow HTTP localhost only in development
    if ENV == "development" and re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
        return True
    # Allow HTTPS localhost in any environment
    if re.match(r'^https://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
        return True
    # Allow Vercel preview deployment URLs (e.g., https://project-git-branch-user.vercel.app)
    if re.match(r'^https://[a-zA-Z0-9\-_\.]+\.vercel\.app$', origin):
        return True
    # Allow valid HTTPS URLs with proper domains
    if re.match(r'^https://[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$', origin):
        return True
    return False

# Set allowed_origins based on environment
allowed_origins = []
if ENV == "development":
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:7860",
        "https://localhost:3000",
        "https://localhost:7860",
    ])
else:
    # In production, only allow HTTPS localhost (if needed for testing)
    allowed_origins.extend([
        "https://localhost:3000",
        "https://localhost:7860",
    ])

# Add production origins from environment variable if set
if os.getenv("ALLOWED_ORIGINS"):
    additional_origins = os.getenv("ALLOWED_ORIGINS").split(",")
    for origin in additional_origins:
        stripped_origin = origin.strip()
        if validate_origin(stripped_origin):
            allowed_origins.append(stripped_origin)
        else:
            logger.warning(f"Skipping invalid CORS origin: {stripped_origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph instance with thread-safe initialization
graph: Optional[AssetRelationshipGraph] = None
# Remove global graph instance and lazy initializer.
# Each request should instantiate its own AssetRelationshipGraph.


# Pydantic models for API responses
class AssetResponse(BaseModel):
    id: str
    symbol: str
    name: str
    asset_class: str
    sector: str
    price: float
    market_cap: Optional[float] = None
    currency: str = "USD"
    additional_fields: Dict[str, Any] = {}


class RelationshipResponse(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    strength: float


class MetricsResponse(BaseModel):
    total_assets: int
    total_relationships: int
    asset_classes: Dict[str, int]
    avg_degree: float
    max_degree: int
    network_density: float


class VisualizationDataResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


@app.get("/")
async def root():
    """
    Provide basic API information including the API title, version, and available endpoint paths.
    
    Returns:
        dict: A mapping with keys:
            - "message": brief API title string,
            - "version": API version string,
            - "endpoints": dict mapping endpoint names to their URL paths.
    """
    return {
        "message": "Financial Asset Relationship API",
        "version": "1.0.0",
        "endpoints": {
            "assets": "/api/assets",
            "asset_detail": "/api/assets/{asset_id}",
            "relationships": "/api/relationships",
            "metrics": "/api/metrics",
            "visualization": "/api/visualization"
        }
    }


@app.get("/api/health")
async def health_check():
    """
    Report the API health and whether the in-memory asset relationship graph is initialized.
    
    Returns:
        dict: A mapping with keys:
            - "status" (str): Health status string, e.g., "healthy".
            - "graph_initialized" (bool): `True` if the in-memory graph instance exists, `False` otherwise.
    """
    return {"status": "healthy", "graph_initialized": graph is not None}


@app.get("/api/assets", response_model=List[AssetResponse])
async def get_assets(
    asset_class: Optional[str] = None,
    sector: Optional[str] = None
):
    """
    Return a list of assets, optionally filtered by asset class and sector.
    
    Parameters:
        asset_class (Optional[str]): If provided, include only assets whose asset_class.value equals this string.
        sector (Optional[str]): If provided, include only assets whose sector equals this string.
    
    Returns:
        List[AssetResponse]: A list of AssetResponse objects representing matching assets. Each item includes core fields and an `additional_fields` map of asset-specific attributes when present.
    
    Raises:
        HTTPException: Raised with status code 500 if an unexpected error occurs while retrieving assets.
    """
    try:
        g = get_graph()
        assets = []
        
        for asset_id, asset in g.assets.items():
            # Apply filters
            if asset_class and asset.asset_class.value != asset_class:
                continue
            if sector and asset.sector != sector:
                continue
            
            # Build response
            asset_dict = {
                "id": asset.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_class": asset.asset_class.value,
                "sector": asset.sector,
                "price": asset.price,
                "market_cap": asset.market_cap,
                "currency": asset.currency,
                "additional_fields": {}
            }
            
            # Add asset-specific fields
            for field in ["pe_ratio", "dividend_yield", "earnings_per_share", "book_value",
                         "yield_to_maturity", "coupon_rate", "maturity_date", "credit_rating",
                         "contract_size", "delivery_date", "volatility",
                         "exchange_rate", "country", "central_bank_rate"]:
                if hasattr(asset, field):
                    value = getattr(asset, field)
                    if value is not None:
                        asset_dict["additional_fields"][field] = value
            
            assets.append(AssetResponse(**asset_dict))
        
        return assets
    except Exception as e:
        logger.error(f"Error getting assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assets/{asset_id}", response_model=AssetResponse)
async def get_asset_detail(asset_id: str):
    """
    Retrieve detailed information for the asset identified by `asset_id`.
    
    Returns:
        AssetResponse: Detailed asset data including core fields and an `additional_fields`
        mapping of asset-specific attributes (e.g., `pe_ratio`, `dividend_yield`, `issuer_id`).
    
    Raises:
        HTTPException: Status 404 if the asset is not found.
        HTTPException: Status 500 for unexpected server errors.
    """
    try:
        g = get_graph()
        
        if asset_id not in g.assets:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        asset = g.assets[asset_id]
        
        asset_dict = {
            "id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "asset_class": asset.asset_class.value,
            "sector": asset.sector,
            "price": asset.price,
            "market_cap": asset.market_cap,
            "currency": asset.currency,
            "additional_fields": {}
        }
        
        # Add all asset-specific fields
        for field in ["pe_ratio", "dividend_yield", "earnings_per_share", "book_value",
                     "yield_to_maturity", "coupon_rate", "maturity_date", "credit_rating",
                     "contract_size", "delivery_date", "volatility",
                     "exchange_rate", "country", "central_bank_rate", "issuer_id"]:
            if hasattr(asset, field):
                value = getattr(asset, field)
                if value is not None:
                    asset_dict["additional_fields"][field] = value
        
        return AssetResponse(**asset_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assets/{asset_id}/relationships", response_model=List[RelationshipResponse])
async def get_asset_relationships(asset_id: str):
    """
    Retrieve relationships originating from the given asset.
    
    Parameters:
        asset_id (str): The asset identifier to retrieve relationships for.
    
    Returns:
        List[RelationshipResponse]: A list of relationship objects representing outgoing relationships from the specified asset.
    """
    try:
        g = get_graph()
        
        if asset_id not in g.assets:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        relationships = []
        
        # Outgoing relationships
        if asset_id in g.relationships:
            for target_id, rel_type, strength in g.relationships[asset_id]:
                relationships.append(RelationshipResponse(
                    source_id=asset_id,
                    target_id=target_id,
                    relationship_type=rel_type,
                    strength=strength
                ))
        
        return relationships
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/relationships", response_model=List[RelationshipResponse])
async def get_all_relationships():
    """
    Retrieve all relationships present in the graph.
    
    Returns:
        List[RelationshipResponse]: A list of RelationshipResponse objects where each item contains the relationship's source_id, target_id, relationship_type, and strength.
    
    Raises:
        HTTPException: Raised with status code 500 if an internal error occurs while retrieving relationships.
    """
    try:
        g = get_graph()
        relationships = []
        
        for source_id, rels in g.relationships.items():
            for target_id, rel_type, strength in rels:
                relationships.append(RelationshipResponse(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=rel_type,
                    strength=strength
                ))
        
        return relationships
    except Exception as e:
        logger.error(f"Error getting relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Produce aggregated network metrics for the asset relationship graph.
    
    Returns:
        metrics (MetricsResponse): Aggregated metrics including:
            - total_assets: total number of assets
            - total_relationships: total number of relationships
            - asset_classes: mapping from asset class name to asset count
            - avg_degree: average degree of nodes
            - max_degree: maximum node degree
            - network_density: density of the network
    
    Raises:
        HTTPException: With status code 500 if metrics cannot be retrieved.
    """
    try:
        g = get_graph()
        metrics = g.calculate_metrics()
        
        # Count assets by class
        asset_classes = {}
        for asset in g.assets.values():
            class_name = asset.asset_class.value
            asset_classes[class_name] = asset_classes.get(class_name, 0) + 1
        
        return MetricsResponse(
            total_assets=metrics.get("total_assets", 0),
            total_relationships=metrics.get("total_relationships", 0),
            asset_classes=asset_classes,
            avg_degree=metrics.get("avg_degree", 0.0),
            max_degree=metrics.get("max_degree", 0),
            network_density=metrics.get("network_density", 0.0)
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visualization", response_model=VisualizationDataResponse)
async def get_visualization_data():
    """
    Return 3D visualization nodes and edges representing the asset graph.
    
    Returns:
        VisualizationDataResponse: An object with:
            - nodes: list of dicts each containing `id`, `name`, `symbol`, `asset_class`, `x`, `y`, `z`, `color`, and `size`.
            - edges: list of dicts each containing `source`, `target`, `relationship_type`, and `strength`.
    
    Raises:
        HTTPException: If visualization data cannot be retrieved or an internal error occurs.
    """
    try:
        g = get_graph()
        viz_data = g.get_3d_visualization_data()
        
        nodes = []
        for node in (viz_data.get("nodes") if isinstance(viz_data.get("nodes"), list) else []):
            nodes.append({
                "id": node["id"],
                "name": node["name"],
                "symbol": node["symbol"],
                "asset_class": node["asset_class"],
                "x": float(node["x"]),
                "y": float(node["y"]),
                "z": float(node["z"]),
                "color": node.get("color", "#1f77b4"),
                "size": node.get("size", 5)
            })
        
        edges = []
        for edge in viz_data.get("edges", []):
            edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "relationship_type": edge.get("relationship_type", "unknown"),
                "strength": edge.get("strength", 0.5)
            })
        
        return VisualizationDataResponse(nodes=nodes, edges=edges)
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/asset-classes")
async def get_asset_classes():
    """
    Return the available asset class values.
    
    Returns:
        dict: Mapping with key "asset_classes" to a list of asset class values as strings.
    """
    return {
        "asset_classes": [ac.value for ac in AssetClass]
    }


@app.get("/api/sectors")
async def get_sectors():
    """
    Return a sorted list of unique sector names present in the graph.
    
    Returns:
        dict: A mapping with key "sectors" to a sorted list of sector names (List[str]).
    
    Raises:
        HTTPException: Raised with status_code 500 if an unexpected error occurs while retrieving sectors.
    """
    try:
        g = get_graph()
        sectors = set()
        for asset in g.assets.values():
            if asset.sector:
                sectors.add(asset.sector)
        return {"sectors": sorted(list(sectors))}
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)