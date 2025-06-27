from pydantic import BaseModel, ConfigDict, computed_field, Field
from beanie import Document
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

class JobPosting(BaseModel):
    job_id: int = Field(alias='id')
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    benefits: Optional[str] = None
    date_posted: Optional[str] = None
    time_since_posted: Optional[str] = None

class JobCriteriaItems(BaseModel):
    seniority_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_function: Optional[str] = None
    industries: Optional[str] = None
    
    model_config = ConfigDict(extra='allow')

class JobStatus(str, Enum):
    NOT_APPLIED = 'Not Applied'
    APPLIED = 'Applied'
    REJECTED = 'Rejected'
    INTERVIEW = 'Interview'
    OFFER = 'Offer'
    CLOSED = 'Closed'

class Job(Document):
    job_id: int
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_criteria_items: Optional[JobCriteriaItems] = None
    benefits: Optional[str] = None
    date_posted: Optional[datetime] = None
    # time_since_posted: Optional[str] = None
    num_applicants: Optional[str] = None
    description: Optional[str] = None
    search_keys: list[str]
    last_updated: datetime = datetime.now(tz=timezone.utc)

    @computed_field
    @property
    def job_link(self) -> str:
        return f'https://www.linkedin.com/jobs/view/{self.job_id}'
    