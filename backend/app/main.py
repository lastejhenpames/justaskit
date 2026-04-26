from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, query, health
from app.core.middleware import RequestIDMiddleware, ErrorHandlingMiddleware
from app.core.logging_config import setup_logging
import logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Analytics Copilot API",
    description="AI-powered data analytics with multi-agent orchestration",
    version="0.1.0"
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(health.router, tags=["health"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", extra={
        "service": "multi-agent-analytics",
        "version": "0.1.0"
    })

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Analytics Copilot API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
