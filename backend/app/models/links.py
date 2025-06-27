from beanie import Document
import uuid
from datetime import datetime, timezone

class JobUserLink(Document):
    id: uuid.UUID
    job_id: int
    user_id: uuid.UUID
    last_updated: datetime = datetime.now(tz=timezone.utc)
    