"""FastAPI backend for Financial Asset Relationship Database"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from src.logic.asset_graph import AssetRelationshipGraph
from src.data.real_data_fetcher import create_real_database
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

def validate_origin(origin: str) -> bool:
    """
    Check whether an origin URL is allowed for CORS.
    
    Valid origins include localhost/127.0.0.1 (optional port), Vercel preview deployments, and configured production domains such as `*.vercel.app` and `*.yourdomain.com`.
    
    Parameters:
        origin (str): The origin URL to validate (including scheme).
    
    Returns:
        `True` if the origin matches allowed development, Vercel preview, or production domain patterns, `False` otherwise.
    """
    # Allow localhost and 127.0.0.1 for development
    if re.match(r'^https?://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
        return True
    # Allow Vercel preview deployment URLs (e.g., https://project-git-branch-user.vercel.app)
    if re.match(r'^https://[a-zA-Z0-9\-_\.]+\.vercel\.app$', origin):
        return True
    # Allow specific production domains (update for your deployment)
    allowed_domains = [
        r'^https://[\w-]+\.vercel\.app$',
        r'^https://[\w-]+\.yourdomain\.com$'
    ]
    return any(re.match(pattern, origin) for pattern in allowed_domains)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:7860",
]
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

# Global graph instance
graph: Optional[AssetRelationshipGraph] = None


def get_graph() -> AssetRelationshipGraph:
    """
    Provide the singleton AssetRelationshipGraph instance, initializing it on first use.
    
    If the global graph has not been created, this function initializes it by creating the real database and building relationships.
    
    Returns:
        The initialized AssetRelationshipGraph instance.
    """
    global graph
    if graph is None:
        logger.info("Initializing asset relationship graph")
        graph = create_real_database()
        graph.build_relationships()
    return graph


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
    Provide basic API metadata and a listing of available endpoints.
    
    Returns:
        dict: A mapping containing:
            - "message": short API description string.
            - "version": API version string.
            - "endpoints": dict mapping endpoint keys to their URL paths (e.g., "assets": "/api/assets").
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
    Return API health status and whether the global graph has been initialized.
    
    Returns:
        dict: A dictionary with the following keys:
            - status (str): String indicating overall service health ("healthy").
            - graph_initialized (bool): True if the global graph has been created, False otherwise.
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
        asset_class (Optional[str]): Filter to include only assets whose `asset_class.value` equals this string.
        sector (Optional[str]): Filter to include only assets whose `sector` equals this string.
    
    Returns:
        List[AssetResponse]: AssetResponse objects matching the filters. Each object's `additional_fields` contains any non-null, asset-type-specific attributes as defined in the respective asset model classes.
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
    
    Parameters:
        asset_id (str): Identifier of the asset whose details are requested.
    
    Returns:
        AssetResponse: Detailed asset information as defined in the AssetResponse model, including core fields and an `additional_fields` map containing any asset-specific attributes that are present and non-null.
    
    Raises:
        HTTPException: 404 if the asset is not found.
        HTTPException: 500 for unexpected errors while retrieving the asset.
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
    Return all outgoing relationships for the asset identified by `asset_id`.
    
    Parameters:
        asset_id (str): Identifier of the asset whose relationships are requested.
    
    Returns:
        List[RelationshipResponse]: A list of relationship records (source_id, target_id, relationship_type, strength).
    
    Raises:
        HTTPException: 404 if the asset is not found; 500 for other errors.
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
    Return a list of all relationships present in the initialized asset graph.
    
    Returns:
        List[RelationshipResponse]: List of directed relationships; each item contains `source_id`, `target_id`, `relationship_type`, and `strength`.
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
    Retrieve network metrics and counts of assets grouped by asset class from the global graph.
    
    Builds a MetricsResponse containing aggregated network statistics and a mapping of asset class names to their asset counts.
    
    Returns:
        MetricsResponse: Object with fields:
            - total_assets: total number of assets in the graph.
            - total_relationships: total number of relationships in the graph.
            - asset_classes: dict mapping asset class name to count of assets.
            - avg_degree: average node degree in the network.
            - max_degree: maximum node degree in the network.
            - network_density: density of the network.
    
    Raises:
        HTTPException: with status code 500 if metrics cannot be obtained.
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
    Provide nodes and edges prepared for 3D visualization of the asset graph.
    
    Builds a list of node dictionaries (each with id, name, symbol, asset_class, x, y, z, color, size) and a list of edge dictionaries (each with source, target, relationship_type, strength) suitable for the API response.
    
    Returns:
        VisualizationDataResponse: An object with `nodes` (list of node dicts) and `edges` (list of edge dicts).
    
    Raises:
        HTTPException: If visualization data cannot be retrieved or processed; results in a 500 status with the error detail.
    """
    try:
        g = get_graph()
        positions, asset_ids, asset_colors, asset_text, edges_xyz = g.get_3d_visualization_data()
        
        nodes = []
        for i, asset_id in enumerate(asset_ids):
            asset = g.assets[asset_id]
            nodes.append({
                "id": asset_id,
                "name": asset.name,
                "symbol": asset.symbol,
                "asset_class": asset.asset_class.value,
                "x": float(positions[i, 0]),
                "y": float(positions[i, 1]),
                "z": float(positions[i, 2]),
                "color": asset_colors[i],
                "size": 5
            })
    except Exception as e: print(f"An error occurred: {e}")
    """Get 3D visualization data"""
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
    List available asset classes.
    
    Returns:
        dict: A mapping with key "asset_classes" whose value is a list of asset class string values.
    """
    return {
        "asset_classes": [ac.value for ac in AssetClass]
    }


@app.get("/api/sectors")
async def get_sectors():
    """
    Return a sorted list of unique sectors present in the asset graph.
    
    Returns:
        dict: A mapping with key "sectors" to a sorted list of unique sector names (List[str]).
    
    Raises:
        HTTPException: If an error occurs while retrieving sectors (responds with status 500).
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