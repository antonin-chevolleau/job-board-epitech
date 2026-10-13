from fastapi import APIRouter

from app.api.routes import advertisements, applications, auth, companies, users

api_router = APIRouter(prefix="/api")
for module in (auth, companies, advertisements, users, applications):
    api_router.include_router(module.router)
