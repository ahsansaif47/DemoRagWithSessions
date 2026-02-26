from fastapi import APIRouter
from app.api.router.auth import router as auth_router
from app.api.router.document import router as document_router

api_router = APIRouter(prefix="/api")  # root prefix

# Mount feature routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(document_router, prefix="/documents", tags=["Documents"])