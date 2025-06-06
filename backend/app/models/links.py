from pydantic import computed_field
from beanie import Document
import uuid
from datetime import datetime, timezone

JOB_USER_NAMESPACE = uuid.UUID('f27dcd16-431c-11f0-93a8-02b932676a17')

def make_job_user_link_id(job_id: int, user_id: uuid.UUID) -> uuid.UUID:
    return uuid.uuid5(JOB_USER_NAMESPACE, f"{job_id}:{user_id}")


class JobUserLink(Document):
    job_id: int
    user_id: uuid.UUID
    last_updated: datetime = datetime.now(tz=timezone.utc)
    
    @computed_field
    def link_id(self) -> uuid.UUID:
        return make_job_user_link_id(self.job_id, self.user_id)
    