from fastapi import APIRouter
from app.api.endpoints import jobs, users, login
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)
api_router.include_router(jobs.router, prefix='/jobs', tags=['jobs'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(login.router, prefix='/login', tags=['login'])
