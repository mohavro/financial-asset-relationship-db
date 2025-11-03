# Comprehensive test coverage available in tests/unit/test_api_main.py
"""FastAPI backend for Financial Asset Relationship Database"""

from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import logging
import os
import re
import threading

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from .auth import Token, User, authenticate_user, create_access_token, get_current_active_user
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.logic.asset_graph import AssetRelationshipGraph
from src.data.real_data_fetcher import RealDataFetcher
from src.models.financial_models import AssetClass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global graph instance with thread-safe initialization
graph: Optional[AssetRelationshipGraph] = None
graph_lock = threading.Lock()


def get_graph() -> AssetRelationshipGraph:
    """
    Get or create the global graph instance with thread-safe initialization.

    Uses double-check locking pattern for efficiency in concurrent environments.
    The graph is lazily initialized on first access or during application startup.

    Returns:
        AssetRelationshipGraph: The initialized graph instance.
    """
    global graph
    if graph is None:
        with graph_lock:
            if graph is None:
                fetcher = RealDataFetcher()
                graph = fetcher.create_real_database()
                logger.info("Graph initialized successfully")
    return graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler.

    Initializes the graph during startup and handles cleanup on shutdown.
    This ensures the database is ready before handling any requests.
    """
    # Startup
    try:
        get_graph()
        logger.info("Application startup complete - graph initialized")
    except Exception:
        logger.exception("Failed to initialize graph during startup")
        raise

    yield

    # Shutdown (cleanup if needed)
    logger.info("Application shutdown")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title="Financial Asset Relationship API",
    description="REST API for Financial Asset Relationship Database",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS for Next.js frontend
# Note: Update allowed origins for production deployment


# Determine environment (default to 'development' if not set)
ENV = os.getenv("ENV", "development").lower()



@app.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate JWT token for authenticated users"""
    from .auth import fake_users_db  # Import here to avoid circular imports
    
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def validate_origin(origin: str) -> bool:
    """Validate that an origin matches expected patterns"""
    # Use module-level ENV variable for environment
    current_env = ENV
    
    # Get allowed origins from environment variable or use default
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    # If origin is in explicitly allowed list, return True
    if origin in allowed_origins and origin:
        return True
        
    # Allow HTTP localhost only in development
    if current_env == "development" and re.match(r"^http://(localhost|127\.0\.0\.1)(:\d+)?$", origin):
        return True
    # Allow HTTPS localhost in any environment
    if re.match(r"^https://(localhost|127\.0\.0\.1)(:\d+)?$", origin):
        return True
    # Allow Vercel preview deployment URLs (e.g., https://project-git-branch-user.vercel.app)
    if re.match(r"^https://[a-zA-Z0-9\-\.]+\.vercel\.app$", origin):
        return True
    # Allow valid HTTPS URLs with proper domains
    if re.match(
        r"^https://[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$",
        origin,
    ):
        return True
    return False


# Set allowed_origins based on environment
allowed_origins = []
if ENV == "development":
    allowed_origins.extend(
        [
            "http://localhost:3000",
            "http://localhost:7860",
            "https://localhost:3000",
            "https://localhost:7860",
        ]
    )
else:
    # In production, only allow HTTPS localhost (if needed for testing)
    allowed_origins.extend(
        [
            "https://localhost:3000",
            "https://localhost:7860",
        ]
    )

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


def raise_asset_not_found(asset_id: str, resource_type: str = "Asset") -> None:
    """
    Raise HTTPException for missing resources.

    Args:
        asset_id (str): ID of the asset that was not found.
        resource_type (str): Type of resource (default: "Asset").
    """
    raise HTTPException(status_code=404, detail=f"{resource_type} {asset_id} not found")


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
        Dict[str, Union[str, Dict[str, str]]]: A mapping containing:
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
            "visualization": "/api/visualization",
        },
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "graph_initialized": True}


@app.get("/api/assets", response_model=List[AssetResponse])
async def get_assets(asset_class: Optional[str] = None, sector: Optional[str] = None):
    """
    List assets, optionally filtered by asset class and sector.

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
                "additional_fields": {},
            }

            # Add asset-specific fields
            for field in [
                "pe_ratio",
                "dividend_yield",
                "earnings_per_share",
                "book_value",
                "yield_to_maturity",
                "coupon_rate",
                "maturity_date",
                "credit_rating",
                "contract_size",
                "delivery_date",
                "volatility",
                "exchange_rate",
                "country",
                "central_bank_rate",
            ]:
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
            raise_asset_not_found(asset_id)

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
            "additional_fields": {},
        }

        # Add all asset-specific fields
        for field in [
            "pe_ratio",
            "dividend_yield",
            "earnings_per_share",
            "book_value",
            "yield_to_maturity",
            "coupon_rate",
            "maturity_date",
            "credit_rating",
            "contract_size",
            "delivery_date",
            "volatility",
            "exchange_rate",
            "country",
            "central_bank_rate",
            "issuer_id",
        ]:
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
    """
    List outgoing relationships for the specified asset.

    Parameters:
        asset_id (str): Identifier of the asset whose outgoing relationships are requested.

    Returns:
        List[RelationshipResponse]: Outgoing relationship records for the asset (each with source_id, target_id, relationship_type, and strength).

    Raises:
        HTTPException: 404 if the asset is not found; 500 for unexpected errors.
    """
    try:
        g = get_graph()
        if asset_id not in g.assets:
            raise_asset_not_found(asset_id)

        relationships = []

        # Outgoing relationships
        if asset_id in g.relationships:
            for target_id, rel_type, strength in g.relationships[asset_id]:
                relationships.append(
                    RelationshipResponse(
                        source_id=asset_id, target_id=target_id, relationship_type=rel_type, strength=strength
                    )
                )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception("Error getting asset relationships:")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return relationships


@app.get("/api/relationships", response_model=List[RelationshipResponse])
async def get_all_relationships():
    """
    List all directed relationships in the initialized asset graph.

    Returns:
        List[RelationshipResponse]: List of relationships where each item contains `source_id`, `target_id`, `relationship_type`, and `strength`.
    """
    try:
        g = get_graph()
        relationships = []

        for source_id, rels in g.relationships.items():
            for target_id, rel_type, strength in rels:
                relationships.append(
                    RelationshipResponse(
                        source_id=source_id, target_id=target_id, relationship_type=rel_type, strength=strength
                    )
                )
    except Exception as e:
        logger.exception("Error getting relationships:")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return relationships


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Return aggregated network metrics and counts of assets grouped by asset class.

    Builds a MetricsResponse containing overall network statistics and a mapping from asset class name to the number of assets in that class.

    Returns:
        MetricsResponse: Object with the following fields:
            - total_assets: total number of assets in the graph.
            - total_relationships: total number of directed relationships in the graph.
            - asset_classes: dict mapping asset class name (str) to its asset count (int).
            - avg_degree: average node degree (float).
            - max_degree: maximum node degree (int).
            - network_density: network density (float).

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
            network_density=metrics.get("network_density", 0.0),
        )
    except Exception as e:
        logger.exception("Error getting metrics:")
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        # get_3d_visualization_data returns: (positions, asset_ids, asset_colors, asset_text, (edges_x, edges_y, edges_z)), but edge coordinates are not used in this endpoint
        positions, asset_ids, asset_colors, asset_text = g.get_3d_visualization_data()[:4]

        nodes = []
        for i, asset_id in enumerate(asset_ids):
            asset = g.assets[asset_id]
            nodes.append(
                {
                    "id": asset_id,
                    "name": asset.name,
                    "symbol": asset.symbol,
                    "asset_class": asset.asset_class.value,
                    "x": float(positions[i, 0]),
                    "y": float(positions[i, 1]),
                    "z": float(positions[i, 2]),
                    "color": asset_colors[i],
                    "size": 5,
                }
            )

        edges = []
        # Build edges directly from graph.relationships to avoid rebuilding from intermediate data structures
        # Only include edges where both source and target are in the asset_ids list
        asset_id_set = set(asset_ids)
        for source_id in g.relationships:
            if source_id not in asset_id_set:
                continue
            for target_id, rel_type, strength in g.relationships[source_id]:
                if target_id in asset_id_set:
                    edges.append(
                        {
                            "source": source_id,
                            "target": target_id,
                            "relationship_type": rel_type,
                            "strength": float(strength),
                        }
                    )

        return VisualizationDataResponse(nodes=nodes, edges=edges)
    except Exception as e:
        logger.exception("Error getting visualization data:")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/asset-classes")
async def get_asset_classes():
    """
    List available asset classes.

    Returns:
        Dict[str, List[str]]: A mapping with key "asset_classes" whose value is a list of asset class string values.
    """
    return {"asset_classes": [ac.value for ac in AssetClass]}


@app.get("/api/sectors")
async def get_sectors():
    """
    List unique sector names present in the global asset graph in sorted order.

    Returns:
        Dict[str, List[str]]: Mapping with key "sectors" to a sorted list of unique sector names.

    Raises:
        HTTPException: Raised with status code 500 if an unexpected error occurs while retrieving sectors.
    """
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
