from temporalio.client import Client
from fastapi import Request, HTTPException


async def init_temporal_client():
    """Initialize Temporal client connection"""
    return await Client.connect("localhost:7233")


async def get_temporal_client(request: Request) -> Client:
    """Get Temporal client from app state"""
    client = request.app.state.temporal_client
    if not client:
        raise HTTPException(status_code=503, detail="Temporal client not initialized")
    return client
