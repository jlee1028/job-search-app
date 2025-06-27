import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

class JobPostScraper:
    def __init__(self):
        self._url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&f_TPR={max_seconds_since_posted}&start={start}'

    def _parse_listing(self, raw_listing: str) -> ResultSet:
        """parse raw html from LinkedIn job list page

        Args:
            raw_listing (str): raw html from LinkedIn job list page

        Returns:
            ResultSet: a list-like object containing li html objects from LinkedIn job list page
        """
        list_soup = BeautifulSoup(raw_listing, 'html.parser')
        parsed_listing = list_soup.find_all('li')
        return parsed_listing

    def _parse_job_post(self, job_post: Tag) -> dict:
        """parse job post data out of a LinkedIn job posting

        Args:
            job_post (Tag): LinkedIn job posting to be parsed

        Returns:
            dict: parsed job post data
        """
        job_data = {}
        base_card_data = job_post.find('div', {'class': 'base-card'}) or job_post.find('a', {'class': 'base-card'})
        job_data['id'] = base_card_data.get('data-entity-urn').split(':')[3]
        try:
            job_data['title'] = base_card_data.find('h3', {'class': 'base-search-card__title'}).text.strip()
        except AttributeError:
            try:
                job_data['title'] = base_card_data.find('span', {'class': 'sr-only'}).text.strip()
            except Exception:
                pass # pydantic will assign it None if not provided
        try:
            job_data['company'] = base_card_data.find('h4', {'class': 'base-search-card__subtitle'}).text.strip()
        except:
            pass # pydantic will assign it None if not provided
        try:
            job_data['location'] = base_card_data.find('span', {'class': 'job-search-card__location'}).text.strip()
        except:
            pass # pydantic will assign it None if not provided
        try:
            job_data['benefits'] = base_card_data.find('span', {'class': 'job-posting-benefits__text'}).text.strip()
        except:
            pass # pydantic will assign it None if not provided
        try:
            job_data['date_posted'] = base_card_data.find('time', {'class': 'job-search-card__listdate'}).attrs['datetime']
            job_data['time_since_posted'] = base_card_data.find('time', {'class': 'job-search-card__listdate'}).text.strip()
        except AttributeError:
            try:
                job_data['date_posted'] = base_card_data.find('time', {'class': 'job-search-card__listdate--new'}).attrs['datetime']
                job_data['time_since_posted'] = base_card_data.find('time', {'class': 'job-search-card__listdate--new'}).text.strip()
            except Exception:
                pass # pydantic will assign them None if not provided
        return job_data

    def get_postings(
            self,
            keywords: str=None,
            location: str=None,
            max_days_since_posted: int=1,
            start: int=0,
            limit: int=10
            ) -> list[dict]:
        """scrape a list of raw html job listings from LinkedIn

        Args:
            keywords (list[str], optional): keywords to search for. Defaults to None.
            location (str, optional): location to search for. Defaults to None.
            days_old (int, optional): filter how many days ago the job was posted. Defaults to 7.
            limit (int, optional): total number of jobs to return. Defaults to 10.

        Raises:
            TypeError: raised on incorrect argument type
            RequestStatusException: raised when request returns a status code outside of the 200s

        Returns:
            list[dict]: a list of job post dictionaries
        """
        limit = limit - limit%10 if limit>9 else limit
        max_seconds_since_posted = f'r{max_days_since_posted * 86400}'
        parsed_job_listings = []
        while len(parsed_job_listings) < limit:
            url = self._url.format(
                keywords=keywords,
                location=location,
                max_seconds_since_posted=max_seconds_since_posted,
                start=start
                )
            resp = requests.get(url=url)
            if 200 > resp.status_code > 299:                
                raise requests.HTTPError(f'error {resp.status_code} - {resp.reason} - {resp.text}')
            parsed_listing = self._parse_listing(resp.text)
            if not parsed_listing:
                return parsed_job_listings
            parsed_job_listings.extend([self._parse_job_post(job_posting) for job_posting in parsed_listing])
            start += 10
        return parsed_job_listings

class JobContentScraper:
    def __init__(self):
        self._url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}'

    def _get_criteria_items(self, job_soup: BeautifulSoup) -> dict:
        """extract job criteria items from a LinkedIn job

        Args:
            job_soup (BeautifulSoup): a BeautifulSoup object containing html from a LinkedIn job page

        Returns:
            dict: a dictionary of job criteria items
        """
        job_criteria_items = job_soup.find_all('li', class_='description__job-criteria-item')
        if job_criteria_items:
            job_criteria_data = {}
            for item in job_criteria_items:
                try:
                    subheader = item.find('h3', class_='description__job-criteria-subheader').text.strip()
                    criteria = item.find('span', class_='description__job-criteria-text').text.strip()
                    job_criteria_data[subheader.lower().replace(' ', '_')] = criteria
                except:
                    continue # don't add anything
            if job_criteria_data:
                return job_criteria_data
        return None
    
    def _parse_job_data(self, job_soup: BeautifulSoup) -> dict:
        """parse key data from a LinkedIn job page

        Args:
            job_soup (BeautifulSoup): a BeautifulSoup object containing html from a LinkedIn job page

        Returns:
            dict: parsed job data
        """
        job_content = {}
        try:
            job_content['title'] = job_soup.find('h2', {'class': 'top-card-layout__title'}).text.strip()
        except:
            pass  # pydantic will assign it None if not provided
        try:
            job_content['company'] = job_soup.find('a', {'class': 'topcard__org-name-link topcard__flavor--black-link'}).text.strip()
        except:
            pass  # pydantic will assign it None if not provided
        try:
            job_content['location'] = job_soup.find('span', {'class': 'topcard__flavor topcard__flavor--bullet'}).text.strip()
        except:
            pass  # pydantic will assign it None if not provided
        try:
            job_content['salary_range'] = job_soup.find('div', {'class': 'salary compensation__salary'}).text.strip()
        except:
            pass  # pydantic will assign it None if not provided

        # self._get_criteria_items handles exceptions
        job_content['job_criteria_items'] = self._get_criteria_items(job_soup)

        try:
            job_content['time_since_posted'] = job_soup.find('span', {'class': 'posted-time-ago__text topcard__flavor--metadata'}).text.strip()
        except AttributeError:
            try:
                job_content['time_since_posted'] = job_soup.find('span', {'class': 'posted-time-ago__text posted-time-ago__text--new topcard__flavor--metadata'}).text.strip()
            except:
                pass  # pydantic will assign it None if not provided
        try:
            job_content['num_applicants'] = job_soup.find('span', {'class': 'num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet'}).text.strip()
        except AttributeError:
            try:
                job_content['num_applicants'] = job_soup.find('figcaption', {'class': 'num-applicants__caption'}).text.strip()
            except:
                pass  # pydantic will assign it None if not provided
        try:
            job_content['description'] = job_soup.find('div', {'class': 'show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden'}).text.strip()
        except:
            pass  # pydantic will assign it None if not provided
        return job_content

    def get_job_content(self, job_id: int) -> dict:
        """scrape job content from a linkedin job page

        Args:
            job_id (int): linkedin job id

        Raises:
            RequestStatusException: raised when request returns a status code outside of the 200s

        Returns:
            dict: parsed job data
        """
        url = self._url.format(id=job_id)
        resp = requests.get(url)
        if 200 > resp.status_code > 299:                
            raise requests.HTTPError(f'error {resp.status_code} - {resp.reason} - {resp.text}')
        job_soup = BeautifulSoup(resp.text, 'html.parser')
        job_content = self._parse_job_data(job_soup)
        job_content.update({'job_id': job_id})
        return job_content
