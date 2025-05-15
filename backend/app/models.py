from pydantic import BaseModel, ConfigDict, computed_field
from enum import Enum
from typing import Optional

class JobPosting(BaseModel):
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    benefits: Optional[str] = None
    date_posted: Optional[str] = None
    time_since_posted: Optional[str] = None
    # search_keys: list[str]

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

class Job(BaseModel):
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_criteria_items: Optional[JobCriteriaItems] = None
    benefits: Optional[str] = None
    date_posted: Optional[str] = None
    time_since_posted: Optional[str] = None
    num_applicants: Optional[str] = None
    description: Optional[str] = None
    status: JobStatus = JobStatus.NOT_APPLIED
    search_keys: list[str]

    @computed_field
    @property
    def job_link(self) -> str:
        return f'https://www.linkedin.com/jobs/view/{self.id}'
