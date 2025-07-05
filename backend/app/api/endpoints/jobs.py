from typing import Annotated, Optional
from datetime import datetime, timezone
import asyncio
import uuid

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from beanie.operators import In, Set

from app.models.jobs import Job
from app.models.links import JobUserLink
from app.services.job_search_service import JobSearchService

from app.api.deps import CurrentUser

JOB_USER_NAMESPACE = uuid.UUID('f27dcd16-431c-11f0-93a8-02b932676a17')

def make_job_user_link_id(job_id: int, user_id: uuid.UUID) -> uuid.UUID:
    return uuid.uuid5(JOB_USER_NAMESPACE, f"{job_id}:{user_id}")

router = APIRouter()

class JobSearchQuery(BaseModel):
    keywords: Optional[str] = ''
    location: Optional[str] = ''
    max_days_since_posted: int = Field(default=1, gt=0, le=120)
    limit: int = Field(default=10, gt=0, le=100)

@router.get('/search')
async def search_jobs(current_user: CurrentUser, q: Annotated[JobSearchQuery, Query()]) -> list[Job]:
    job_search_service = JobSearchService(**q.model_dump())
    jobs = await job_search_service.search()
    print(f'total jobs returned: {len(jobs)}')

    for job in jobs:
        job_link = JobUserLink(
            id=make_job_user_link_id(job.job_id, current_user.user_id),
            job_id=job.job_id,
            user_id=current_user.user_id
            )
        result = await job_link.save()
    
    # await asyncio.gather(
    #     *[
    #         JobUserLink.find( 
    #             link_id=make_job_user_link_id(job.job_id, current_user.user_id)
    #             ).upsert(
    #                 Set(
    #                     {'last_updated': datetime.now(tz=timezone.utc)}
    #                 ),
    #                 on_insert=JobUserLink(
    #                     link_id=make_job_user_link_id(job.job_id, current_user.user_id),
    #                     job_id=job.job_id,
    #                     user_id=current_user.user_id
    #                 )
    #             )
    #         for job in jobs
    #     ])
    
    return jobs
        

class JobSummary(BaseModel):
    job_id: int
    title: str
    company: str
    location: Optional[str] = None

@router.get('/list')
async def list_jobs(current_user: CurrentUser, limit: int=20) -> list[JobSummary]:
    links = await JobUserLink.find(JobUserLink.user_id == current_user.user_id).limit(limit).to_list()
    job_ids = [link.job_id for link in links]
    jobs = await Job.find(In(Job.job_id, job_ids)).to_list()
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
