from typing import Annotated, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.models import Job
from app.services.job_search_service import JobSearchService

router = APIRouter()

class JobSearchQuery(BaseModel):
    keywords: Optional[str] = ''
    location: Optional[str] = ''
    max_days_since_posted: int = Field(default=1, gt=0, le=120)
    limit: int = Field(default=10, gt=0, le=100)

@router.get('/search')
def search_jobs(q: Annotated[JobSearchQuery, Query()]) -> list[Job]:
    job_search_service = JobSearchService(**q.model_dump())
    return job_search_service.search()
