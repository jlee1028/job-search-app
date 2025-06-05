import os
from typing import Annotated, Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from app.models import Job
from app.services.job_search_service import JobSearchService
from app.db import JobsDatabaseService

router = APIRouter()

db = JobsDatabaseService(os.getenv('MONGODB_URI'))

class JobSearchQuery(BaseModel):
    keywords: Optional[str] = ''
    location: Optional[str] = ''
    max_days_since_posted: int = Field(default=1, gt=0, le=120)
    limit: int = Field(default=10, gt=0, le=100)

@router.get('/search')
def search_jobs(q: Annotated[JobSearchQuery, Query()]) -> list[Job]:
    job_search_service = JobSearchService(**q.model_dump())
    return job_search_service.search()


class JobSummary(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None

@router.get('/list')
def list_jobs(limit: int=20):
    jobs = db.get_jobs(filter={}, limit=limit)
    return [
        JobSummary(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location
            ) for job in jobs
        ]

@router.get('/{job_id}')
def get_job_by_id(job_id: int) -> Job:
    job = db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='job not found')
    return job