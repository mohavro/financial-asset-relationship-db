"""FastAPI backend for Financial Asset Relationship Database"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
import os
import re
import threading

from src.logic.asset_graph import AssetRelationshipGraph
from src.data.real_data_fetcher import RealDataFetcher
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

# Determine environment (default to 'development' if not set)
ENV = os.getenv("ENV", "development").lower()

def validate_origin(origin: str) -> bool:
    """Validate that an origin matches expected patterns"""
    # Allow HTTP localhost only in development
    if ENV == "development" and re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
        return True
    # Allow HTTPS localhost in any environment
    if re.match(r'^https://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
        return True
    # Allow Vercel preview deployment URLs (e.g., https://project-git-branch-user.vercel.app)
    if re.match(r'^https://[a-zA-Z0-9\-\.]+\.vercel\.app$', origin):
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
graph_lock = threading.Lock()

def get_graph() -> AssetRelationshipGraph:
    """Get or create the global graph instance with thread-safe initialization.
    
    Uses double-check locking pattern for efficiency in serverless environments.
    """
    global graph
    if graph is None:
        with graph_lock:
            # Double-check inside lock
            if graph is None:
                try:
                    fetcher = RealDataFetcher()
                    graph = fetcher.create_real_database()
                except Exception as e:
                    logger.error(f"Failed to initialize graph: {str(e)}")
                    raise
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
    """Root endpoint"""
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
    """Health check endpoint"""
    try:
        g = get_graph()
        return {"status": "healthy", "graph_initialized": True}
    except Exception:
        return {"status": "unhealthy", "graph_initialized": False}


@app.get("/api/assets", response_model=List[AssetResponse])
async def get_assets(
    asset_class: Optional[str] = None,
    sector: Optional[str] = None
):
    """Get all assets with optional filters"""
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
    except Exception as e:
        logger.exception("Error getting assets:")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return assets


@app.get("/api/assets/{asset_id}", response_model=AssetResponse)
async def get_asset_detail(asset_id: str):
    """Get detailed information about a specific asset"""
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
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Error getting asset detail:")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/assets/{asset_id}/relationships", response_model=List[RelationshipResponse])
async def get_asset_relationships(asset_id: str):
    """Get all relationships for a specific asset"""
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
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Error getting asset relationships:")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return relationships


@app.get("/api/relationships", response_model=List[RelationshipResponse])
async def get_all_relationships():
    """Get all relationships in the graph"""
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
    except Exception as e:
        logger.exception("Error getting relationships:")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return relationships


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get network metrics"""
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
        logger.exception("Error getting metrics:")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/visualization", response_model=VisualizationDataResponse)
async def get_visualization_data():
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
        logger.exception("Error getting visualization data:")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/asset-classes")
async def get_asset_classes():
    """Get list of available asset classes"""
    return {
        "asset_classes": [ac.value for ac in AssetClass]
    }


@app.get("/api/sectors")
async def get_sectors():
    """Get list of unique sectors in the graph"""
    try:
        g = get_graph()
        sectors = set()
        for asset in g.assets.values():
            if asset.sector:
                sectors.add(asset.sector)
        return {"sectors": sorted(list(sectors))}
    except Exception as e:
        logger.exception("Error getting sectors:")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)