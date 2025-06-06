from typing import Annotated, Optional

from fastapi import APIRouter, Query, HTTPException
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
async def search_jobs(q: Annotated[JobSearchQuery, Query()]) -> list[Job]:
    job_search_service = JobSearchService(**q.model_dump())
    return await job_search_service.search()


class JobSummary(BaseModel):
    job_id: int
    title: str
    company: str
    location: Optional[str] = None

@router.get('/list')
async def list_jobs(limit: int=20) -> list[JobSummary]:
    jobs: list[Job] = await Job.find({}).limit(limit).to_list()
    return [
        JobSummary(
            job_id=job.job_id,
            title=job.title,
            company=job.company,
            location=job.location
            ) for job in jobs
        ]


@router.get('/{job_id}')
async def get_job_by_id(job_id: int) -> Job:
    job = await Job.find_one({'job_id': job_id})
    if not job:
        raise HTTPException(status_code=404, detail='job not found')
    return job
