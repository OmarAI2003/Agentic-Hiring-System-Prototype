"""
Job Description Parser
Extracts and structures information from job postings
Supports both manual job creation and fetching from real job boards
"""
import re
from typing import Dict, List, Optional
from python.utils.helpers import get_logger, parse_skills_list
from python.sourcing.jobboard_scraper import JobBoardScraper

logger = get_logger(__name__)


class JobParser:
    """
    Intelligently parses job descriptions and extracts structured data
    """
    
    # Common experience level keywords
    EXPERIENCE_KEYWORDS = {
        'entry': ['entry', 'junior', 'graduate', 'intern', '0-2 years', 'beginner', 'fresher'],
        'mid': ['mid', 'intermediate', '3-5 years', '2-5 years', 'experienced'],
        'senior': ['senior', 'lead', 'principal', 'staff', '5+ years', 'expert', 'architect']
    }
    
    # Common employment types
    EMPLOYMENT_TYPES = ['full-time', 'part-time', 'contract', 'internship', 'temporary', 'freelance']
    
    # Technical skills database (common skills)
    COMMON_SKILLS = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
        'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind',
        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
        'oracle', 'sql server', 'sqlite',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
        'terraform', 'ansible', 'ci/cd', 'devops',
        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'pandas', 'numpy', 'data analysis', 'statistics', 'nlp', 'computer vision',
        # Soft Skills
        'communication', 'leadership', 'teamwork', 'problem-solving', 'agile', 'scrum',
        'project management', 'analytical thinking'
    ]
    
    def parse(self, job_data: Dict) -> Dict:
        """
        Parse and enhance job data
        
        Args:
            job_data: Raw job data with at least 'title' and 'description'
        
        Returns:
            Enhanced structured job data
        """
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        
        # Extract or infer fields
        parsed = {
            'title': title,
            'description': description,
            'required_skills': self._extract_skills(job_data, description),
            'experience_level': self._determine_experience_level(job_data, title, description),
            'location': self._extract_location(job_data, description),
            'employment_type': self._extract_employment_type(job_data, description),
            'department': job_data.get('department', self._infer_department(title)),
            'salary_range': job_data.get('salary_range'),
            'status': 'active'
        }
        
        logger.info(f"Parsed job: {title} - {parsed['experience_level']} level")
        return parsed
    
    def _extract_skills(self, job_data: Dict, description: str) -> List[str]:
        """Extract required skills from job description"""
        # If explicitly provided, use that
        if 'required_skills' in job_data:
            skills = job_data['required_skills']
            if isinstance(skills, str):
                return parse_skills_list(skills)
            return skills
        
        # Otherwise, extract from description
        description_lower = description.lower()
        found_skills = []
        
        for skill in self.COMMON_SKILLS:
            # Look for skill mentions
            if re.search(r'\b' + re.escape(skill) + r'\b', description_lower):
                found_skills.append(skill)
        
        # Also look for common patterns
        # "Experience with X, Y, and Z"
        exp_pattern = r'experience (?:with|in) ([^.]+)'
        matches = re.findall(exp_pattern, description_lower)
        for match in matches:
            skills_in_match = [s.strip() for s in match.split(',')]
            found_skills.extend([s for s in skills_in_match if len(s) > 2])
        
        # Remove duplicates and limit
        found_skills = list(set(found_skills))[:15]
        
        logger.info(f"Extracted {len(found_skills)} skills from description")
        return found_skills if found_skills else ['general']
    
    def _determine_experience_level(self, job_data: Dict, title: str, description: str) -> str:
        """Determine experience level from job data"""
        # If explicitly provided
        if 'experience_level' in job_data:
            return job_data['experience_level'].lower()
        
        # Check title and description
        text = (title + ' ' + description).lower()
        
        for level, keywords in self.EXPERIENCE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        
        # Default to mid if unclear
        return 'mid'
    
    def _extract_location(self, job_data: Dict, description: str) -> str:
        """Extract or infer location"""
        if 'location' in job_data:
            return job_data['location']
        
        # Look for common location indicators
        location_patterns = [
            r'location[:\s]+([^.\n]+)',
            r'based in ([^.\n]+)',
            r'office in ([^.\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Check for remote
        if re.search(r'\b(remote|work from home|wfh)\b', description, re.IGNORECASE):
            return 'Remote'
        
        return 'Not specified'
    
    def _extract_employment_type(self, job_data: Dict, description: str) -> str:
        """Extract employment type"""
        if 'employment_type' in job_data:
            return job_data['employment_type']
        
        text = description.lower()
        for emp_type in self.EMPLOYMENT_TYPES:
            if emp_type in text:
                return emp_type
        
        return 'full-time'  # Default
    
    def _infer_department(self, title: str) -> str:
        """Infer department from job title"""
        title_lower = title.lower()
        
        departments = {
            'Engineering': ['engineer', 'developer', 'programmer', 'software', 'devops', 'sre'],
            'Data Science': ['data scientist', 'data analyst', 'ml engineer', 'ai', 'machine learning'],
            'Product': ['product manager', 'product owner', 'pm'],
            'Design': ['designer', 'ux', 'ui', 'graphic'],
            'Marketing': ['marketing', 'seo', 'content', 'social media'],
            'Sales': ['sales', 'account executive', 'business development'],
            'HR': ['hr', 'recruiter', 'talent acquisition', 'people'],
            'Finance': ['finance', 'accountant', 'controller', 'cfo']
        }
        
        for dept, keywords in departments.items():
            if any(kw in title_lower for kw in keywords):
                return dept
        
        return 'General'
    
    def validate(self, job_data: Dict) -> tuple[bool, List[str]]:
        """
        Validate job data
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not job_data.get('title'):
            errors.append("Job title is required")
        
        if not job_data.get('description'):
            errors.append("Job description is required")
        
        if not job_data.get('required_skills'):
            errors.append("Required skills must be specified")
        
        return (len(errors) == 0, errors)


def create_sample_jobs() -> List[Dict]:
    """Create sample job postings for testing"""
    return [
        {
            'title': 'Senior Python Developer',
            'description': '''We are looking for a Senior Python Developer with 5+ years of experience.
            Must have strong experience with Python, Django, Flask, PostgreSQL, and AWS.
            Experience with Docker and Kubernetes is a plus.
            This is a full-time remote position.''',
            'required_skills': 'Python, Django, Flask, PostgreSQL, AWS, Docker',
            'experience_level': 'senior',
            'location': 'Remote',
            'employment_type': 'full-time',
            'salary_range': '$120,000 - $160,000',
            'department': 'Engineering'
        },
        {
            'title': 'Data Scientist - Machine Learning',
            'description': '''Seeking a talented Data Scientist to join our ML team.
            Requirements: Python, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn.
            3-5 years experience in machine learning and data analysis.
            Strong background in statistics and mathematics required.
            Location: San Francisco, CA''',
            'required_skills': 'Python, Machine Learning, TensorFlow, PyTorch, Statistics',
            'experience_level': 'mid',
            'location': 'San Francisco, CA',
            'department': 'Data Science'
        },
        {
            'title': 'Junior Frontend Developer',
            'description': '''Entry-level position for a Frontend Developer.
            Required skills: HTML, CSS, JavaScript, React.
            0-2 years experience. Great opportunity for recent graduates.
            Full-time position in New York office.''',
            'required_skills': 'HTML, CSS, JavaScript, React',
            'experience_level': 'entry',
            'location': 'New York, NY',
            'employment_type': 'full-time'
        }
    ]


def fetch_real_jobs(keywords: List[str], max_results: int = 5) -> List[Dict]:
    """
    Fetch real job postings from job boards
    
    Args:
        keywords: Keywords to search for (e.g., ['Python', 'Django'])
        max_results: Maximum number of jobs to fetch
        
    Returns:
        List of real job postings
    """
    scraper = JobBoardScraper()
    return scraper.search_jobs(keywords, category='software-dev', max_results=max_results)


def generate_mock_jobs(count: int = 5) -> List[Dict]:
    """
    Generate mock job postings
    
    Args:
        count: Number of mock jobs to generate
        
    Returns:
        List of mock job postings
    """
    scraper = JobBoardScraper()
    return [scraper.generate_mock_job() for _ in range(count)]


if __name__ == '__main__':
    # Test the parser
    parser = JobParser()
    sample_jobs = create_sample_jobs()
    
    for job in sample_jobs:
        parsed = parser.parse(job)
        print(f"\n=== {parsed['title']} ===")
        print(f"Level: {parsed['experience_level']}")
        print(f"Skills: {', '.join(parsed['required_skills'][:5])}")
        print(f"Location: {parsed['location']}")
        
        is_valid, errors = parser.validate(parsed)
        print(f"Valid: {is_valid}")
        if errors:
            print(f"Errors: {errors}")
