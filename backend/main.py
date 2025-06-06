import certifi
from contextlib import asynccontextmanager
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from app.api.routes import api_router
from app.models.jobs import Job
from app.models.users import User
from app.models.links import JobUserLink
from app.core.config import settings

MONGO_URI = settings.MONGO_URI

client = AsyncIOMotorClient(
        MONGO_URI, tlsCAFile=certifi.where()
    )

db = client['jobs_db']

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,  
        document_models=[
            Job,
            User,
            JobUserLink
        ],
    )
    yield

app = FastAPI(
    title='Job Search API',
    description='API for programmatically fetching and evaluating jobs',
    version='0.1.0',
    lifespan=lifespan
)

app.include_router(router=api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
