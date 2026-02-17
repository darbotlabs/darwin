"""
Darwin FastAPI Main Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routers import session, mcp, agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"MCP Server: {'Enabled' if settings.enable_mcp_server else 'Disabled'}")
    logger.info(f"Agent Swarm: {'Enabled' if settings.enable_agent_swarm else 'Disabled'}")
    
    # Startup logic
    yield
    
    # Shutdown logic
    logger.info("Shutting down Darwin API")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(session.router, prefix="/api/v1", tags=["sessions"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])

if settings.enable_mcp_server:
    app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "features": {
            "mcp_server": settings.enable_mcp_server,
            "agent_swarm": settings.enable_agent_swarm,
            "authentication": settings.enable_authentication,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version,
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.api_host == "0.0.0.0" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
