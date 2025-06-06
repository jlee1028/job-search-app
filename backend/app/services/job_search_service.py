from datetime import datetime, timezone, timedelta
from app.services.scraping_service import JobPostScraper, JobContentScraper
from app.models import JobPosting, Job
from beanie.odm.operators.update.general import Set
from app.core.config import settings

MONGO_URI = settings.MONGODB_URI

class JobSearchService:
    def __init__(
            self,
            keywords: str='',
            location: str='',
            max_days_since_posted: int=1,
            limit: int=10
            ):
        self._job_post_scraper = JobPostScraper()
        self._job_content_scraper = JobContentScraper()
        self._keywords = keywords
        self._location = location
        self._max_days_since_posted = max_days_since_posted
        self._limit = limit
        
    @property
    def keywords(self) -> str:
        return self._keywords
    
    @keywords.setter
    def keywords(self, new_keywords: str):
        if not isinstance(new_keywords, str):
            raise TypeError(f'"keywords" must be a str: {new_keywords} is not the right type')
        self._keywords = new_keywords

    @property
    def location(self) -> str:
        return self._location
    
    @location.setter
    def location(self, new_location: str):
        if not isinstance(new_location, str):
            raise TypeError(f'"location" must be a str: {new_location} is not the right type')
        self._location = new_location

    @property
    def search_key(self) -> str:
        return self._keywords.lower().strip()+self._location.lower().strip()
    
    @property
    def max_days_since_posted(self) -> int:
        return self._max_days_since_posted
    
    @max_days_since_posted.setter
    def max_days_since_posted(self, new_max_days_since_posted: int):
        if not isinstance(new_max_days_since_posted, int):
            raise TypeError(f'"max_days_since_posted" must be an int: {new_max_days_since_posted} is not the right type')
        self._max_days_since_posted = new_max_days_since_posted

    @property
    def limit(self) -> int:
        return self._limit
    
    @limit.setter
    def limit(self, new_limit: int):
        if not isinstance(new_limit, int):
            raise TypeError(f'"limit" must be an int: {new_limit} is not the right type')
        self._limit = new_limit

    def _check_cache(self) -> list[Job]:
        ...

    async def _search_db(self) -> list[Job]:
        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=self.max_days_since_posted)
        jobs = await Job.find(
            # In(Job.search_keys, [self.search_key]),
            Job.search_keys == self.search_key,
            Job.last_updated >= cutoff_date
            ).limit(self.limit).to_list()
        return jobs

    async def _scrape_jobs(self) -> list[Job]:
        job_postings = [
            JobPosting(
                **job_posting
                ) for job_posting in self._job_post_scraper.get_postings(
                    keywords=self.keywords,
                    location=self.location,
                    max_days_since_posted=self.max_days_since_posted,
                    limit=self.limit
                    )
                ]
        jobs = [
            Job(
                **self._job_content_scraper.get_job_content(job_id=job_posting.job_id),
                benefits=job_posting.benefits,
                date_posted=job_posting.date_posted,
                search_keys=[self.search_key],
                ) for job_posting in job_postings
            ]
        for job in jobs:
            await Job.find_one(Job.job_id == job.job_id).upsert(
                Set(
                    {
                        'last_updated': datetime.now(tz=timezone.utc),
                        'date_posted': job.date_posted,
                        'num_applicants': job.num_applicants
                        }
                ),
                on_insert=job
            )
        return jobs

    async def search(self) -> list[Job]:
        # check the db
        jobs = await self._search_db()
        job_count = len(jobs)
        if job_count == self.limit:
            print(f'all {self.limit} results returned from database')
            return jobs
        elif job_count > self.limit:
            print(f'limit not properly implemented, {self.limit} jobs requested but {len(jobs)} returned')
            return jobs
        elif job_count > 0:
            print('partial results returned from database')
            # if returns less postings than requested,
            # scrape the minimum required and combine with db ones
            original_limit = self.limit
            self.limit = self.limit - len(jobs)
            jobs.extend(await self._scrape_jobs())
            self.limit = original_limit
            return jobs[:self.limit]
        else:
            print('no results returned from database')
        
        # scrape jobs and write to db
        jobs = await self._scrape_jobs()
        print(f'{len(jobs)} documents returned from scraper and upserted into the db')
        return jobs

    async def get_by_id(self, job_id) -> Job | None:
        return Job.find_one(filter={'job_id': job_id})
