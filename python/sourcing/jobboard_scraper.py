"""
Job Board Scraper - Fetch Real Job Postings
Uses free public APIs to get actual job listings
"""
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
from python.utils.helpers import get_logger

logger = get_logger(__name__)


class JobBoardScraper:
    """
    Scrapes job postings from free public job boards
    Uses Remotive API (completely free, no auth required)
    """
    
    def __init__(self):
        # Remotive API - Free, no authentication required
        self.remotive_url = "https://remotive.com/api/remote-jobs"
        
    def search_jobs(self, keywords: List[str], category: str = None, max_results: int = 5) -> List[Dict]:
        """
        Search for real job postings
        
        Args:
            keywords: List of keywords to search for (e.g., ['Python', 'Django'])
            category: Job category (e.g., 'software-dev')
            max_results: Maximum number of jobs to return
            
        Returns:
            List of job posting dictionaries
        """
        logger.info(f"🔍 Searching job boards for: {', '.join(keywords)}")
        
        jobs = []
        
        try:
            # Fetch from Remotive API
            jobs.extend(self._fetch_remotive_jobs(keywords, category, max_results))
        except Exception as e:
            logger.warning(f"Remotive API failed: {e}")
        
        logger.info(f"✓ Found {len(jobs)} real job postings")
        return jobs[:max_results]
    
    def _fetch_remotive_jobs(self, keywords: List[str], category: str, max_results: int) -> List[Dict]:
        """Fetch jobs from Remotive API"""
        jobs = []
        
        try:
            # Build query parameters
            params = {}
            if category:
                params['category'] = category
            
            logger.info(f"📡 Fetching from Remotive API...")
            response = requests.get(self.remotive_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            all_jobs = data.get('jobs', [])
            
            # Filter by keywords
            keyword_lower = [k.lower() for k in keywords]
            
            for job in all_jobs:
                if len(jobs) >= max_results:
                    break
                
                # Check if any keyword matches in title, description, or tags
                title = job.get('title', '').lower()
                description = job.get('description', '').lower()
                tags = ' '.join(job.get('tags', [])).lower()
                
                match = any(
                    keyword in title or 
                    keyword in description or 
                    keyword in tags
                    for keyword in keyword_lower
                )
                
                if match:
                    converted_job = self._convert_remotive_job(job)
                    if converted_job:
                        jobs.append(converted_job)
            
            logger.info(f"✓ Retrieved {len(jobs)} jobs from Remotive")
            
        except Exception as e:
            logger.error(f"Error fetching from Remotive: {e}")
        
        return jobs
    
    def _convert_remotive_job(self, job: Dict) -> Optional[Dict]:
        """Convert Remotive job format to our standard format"""
        try:
            # Extract company info
            company_name = job.get('company_name', 'Unknown Company')
            company_logo = job.get('company_logo', '')
            
            # Extract job details
            title = job.get('title', 'Unknown Title')
            description = job.get('description', '')
            url = job.get('url', '')
            
            # Parse job type
            job_type = job.get('job_type', 'Full-time')
            employment_type = 'full-time'
            if 'contract' in job_type.lower():
                employment_type = 'contract'
            elif 'part' in job_type.lower():
                employment_type = 'part-time'
            
            # Extract location (usually "remote" for Remotive)
            candidate_location = job.get('candidate_required_location', 'Remote')
            
            # Extract salary info
            salary_info = job.get('salary', '')
            salary_range = None
            if salary_info:
                salary_range = salary_info
            
            # Parse tags as skills
            tags = job.get('tags', [])
            
            # Determine experience level from title
            title_lower = title.lower()
            if 'senior' in title_lower or 'lead' in title_lower or 'principal' in title_lower:
                experience_level = 'senior'
            elif 'junior' in title_lower or 'entry' in title_lower:
                experience_level = 'entry'
            else:
                experience_level = 'mid'
            
            # Build standardized job object
            standardized_job = {
                'title': title,
                'company': company_name,
                'company_logo': company_logo,
                'description': description[:500],  # Truncate long descriptions
                'required_skills': tags[:10],  # Use tags as skills
                'experience_level': experience_level,
                'location': candidate_location,
                'employment_type': employment_type,
                'salary_range': salary_range,
                'url': url,
                'source': 'remotive',
                'posted_date': job.get('publication_date', datetime.now().isoformat()),
                'department': 'Engineering'  # Default
            }
            
            return standardized_job
            
        except Exception as e:
            logger.error(f"Error converting job: {e}")
            return None
    
    def generate_mock_job(self, base_job: Dict = None) -> Dict:
        """
        Generate a mock job posting based on templates
        
        Args:
            base_job: Optional base job to use as template
            
        Returns:
            Mock job posting dictionary
        """
        from faker import Faker
        import random
        
        fake = Faker()
        
        # Job title templates
        job_titles = [
            'Senior Python Developer',
            'Full Stack Engineer',
            'Backend Developer',
            'Software Engineer',
            'Senior Software Engineer',
            'Lead Developer',
            'Engineering Manager',
            'DevOps Engineer',
            'Data Engineer',
            'Machine Learning Engineer'
        ]
        
        # Skill sets by role
        skill_sets = {
            'python': ['Python', 'Django', 'Flask', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS', 'Redis'],
            'fullstack': ['JavaScript', 'React', 'Node.js', 'TypeScript', 'MongoDB', 'Express.js', 'Docker'],
            'devops': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible', 'Linux'],
            'data': ['Python', 'Spark', 'Airflow', 'SQL', 'Kafka', 'Elasticsearch', 'Pandas', 'NumPy'],
            'ml': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'MLOps', 'Docker']
        }
        
        # Pick random role
        title = random.choice(job_titles)
        
        # Determine skill set based on title
        if 'python' in title.lower() or 'backend' in title.lower():
            skills = random.sample(skill_sets['python'], random.randint(5, 8))
        elif 'full stack' in title.lower():
            skills = random.sample(skill_sets['fullstack'], random.randint(5, 8))
        elif 'devops' in title.lower():
            skills = random.sample(skill_sets['devops'], random.randint(5, 7))
        elif 'data' in title.lower():
            skills = random.sample(skill_sets['data'], random.randint(5, 7))
        elif 'machine learning' in title.lower() or 'ml' in title.lower():
            skills = random.sample(skill_sets['ml'], random.randint(5, 7))
        else:
            skills = random.sample(skill_sets['python'], random.randint(4, 6))
        
        # Experience level
        title_lower = title.lower()
        if 'senior' in title_lower or 'lead' in title_lower:
            experience_level = 'senior'
        elif 'junior' in title_lower or 'entry' in title_lower:
            experience_level = 'entry'
        else:
            experience_level = 'mid'
        
        # Generate mock job
        mock_job = {
            'title': title,
            'company': fake.company(),
            'company_logo': f'https://via.placeholder.com/100?text={fake.company()[:2]}',
            'description': f'We are looking for a talented {title} to join our growing team. '
                          f'You will work on exciting projects using {", ".join(skills[:3])} and more.',
            'required_skills': skills,
            'experience_level': experience_level,
            'location': random.choice(['Remote', 'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA']),
            'employment_type': random.choice(['full-time', 'contract', 'part-time']),
            'salary_range': f'${random.randint(80, 180)}k - ${random.randint(180, 250)}k',
            'url': f'https://jobs.example.com/{fake.uuid4()}',
            'source': 'mock',
            'posted_date': datetime.now().isoformat(),
            'department': random.choice(['Engineering', 'Product', 'Data', 'Infrastructure'])
        }
        
        return mock_job


def test_job_board_scraper():
    """Test job board scraping functionality"""
    scraper = JobBoardScraper()
    
    print("\n" + "="*70)
    print("JOB BOARD SCRAPER TEST")
    print("="*70)
    
    # Test 1: Search real jobs
    print("\n1. Searching for Python developer jobs...")
    real_jobs = scraper.search_jobs(['Python', 'Django'], category='software-dev', max_results=3)
    
    print(f"\nFound {len(real_jobs)} real jobs:\n")
    for i, job in enumerate(real_jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Skills: {', '.join(job['required_skills'][:5])}")
        print(f"   Experience: {job['experience_level']}")
        print(f"   Source: {job['source']}")
        print(f"   URL: {job['url'][:50]}...")
        print()
    
    # Test 2: Generate mock jobs
    print("\n2. Generating mock job postings...")
    mock_jobs = [scraper.generate_mock_job() for _ in range(3)]
    
    print(f"\nGenerated {len(mock_jobs)} mock jobs:\n")
    for i, job in enumerate(mock_jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Skills: {', '.join(job['required_skills'][:5])}")
        print(f"   Salary: {job.get('salary_range', 'Not specified')}")
        print(f"   Source: {job['source']}")
        print()
    
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == '__main__':
    test_job_board_scraper()
