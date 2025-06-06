import os
import certifi
from contextlib import asynccontextmanager
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from app.api.routes import api_router
from app.models import Job

MONGO_URI = os.getenv('MONGODB_URI')

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
        ],
    )
    yield

app = FastAPI(
    title='Job Search API',
    description='API for programmatically fetching and evaluating jobs',
    version='0.1.0',
    lifespan=lifespan
)

app.include_router(router=api_router, prefix='/api')

if __name__ == "__main__":
    import uvicorn

    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
