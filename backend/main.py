from fastapi import FastAPI
from app.api.routes import api_router

app = FastAPI(
    title='Job Search API',
    description='API for programmatically fetching and evaluating jobs',
    version='0.1.0'
)

app.include_router(router=api_router, prefix='/api')

if __name__ == "__main__":
    import uvicorn

    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
