from datetime import datetime, timezone
import certifi
from pymongo import MongoClient
from app.models import Job

class JobsDatabaseService:
    def __init__(self, uri: str):
        self.client = MongoClient(uri, tlsCAFile=certifi.where())
        self.db = self.client['jobs_db']

    def upsert_job(self, job: Job) -> bool:
        result= self.db['jobs'].update_one(
            filter= {'id': job.id},
            update = {
                '$set': job.model_dump(exclude={'search_keys'}) | {'last_updated': datetime.now(tz=timezone.utc)},
                '$addToSet': {'search_keys': job.search_keys[0]}
                },
            upsert=True
        )
        return True if result else False
    
    def bulk_upsert_jobs(self, jobs: list[Job]):
        # docs: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/bulk-write/
        ...
    
    def get_jobs(self, filter: dict, limit: int=10) -> list[Job] | None:
        if limit:
            return [Job(**job) for job in self.db['jobs'].find(filter).limit(limit)]
        return [Job(**job) for job in self.db['jobs'].find(filter)]
    
    def get_job_by_id(self, job_id: int) -> Job | None:
        job = self.db['jobs'].find_one(filter={'id': job_id})
        return Job(**job) if job else None
    
    def delete_jobs(self, filter: dict) -> bool:
        result = self.db['jobs'].delete_many(filter)
        return True if result else False
    