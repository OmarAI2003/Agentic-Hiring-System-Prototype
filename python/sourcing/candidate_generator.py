"""
Mock Candidate Data Generator
Generates realistic candidate profiles for testing
Uses Faker library (completely free)
Also supports real candidate sourcing from GitHub
"""
from faker import Faker
import random
from typing import List, Dict
from datetime import datetime, timedelta
from python.utils.helpers import get_logger, ConfigManager
from python.sourcing.github_searcher import GitHubSearcher

logger = get_logger(__name__)
fake = Faker()


class CandidateGenerator:
    """
    Generates mock candidate profiles with realistic data
    """
    
    # Skill pools by category
    PROGRAMMING_LANGUAGES = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go',
        'Rust', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R'
    ]
    
    WEB_FRAMEWORKS = [
        'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring Boot',
        'Express.js', 'FastAPI', 'Ruby on Rails', 'ASP.NET', 'Laravel'
    ]
    
    DATABASES = [
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
        'Oracle', 'SQL Server', 'DynamoDB', 'Neo4j'
    ]
    
    CLOUD_DEVOPS = [
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI',
        'GitHub Actions', 'Terraform', 'Ansible', 'CircleCI'
    ]
    
    DATA_ML_SKILLS = [
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
        'Pandas', 'NumPy', 'Data Analysis', 'Statistics', 'NLP', 'Computer Vision',
        'Keras', 'XGBoost', 'Spark'
    ]
    
    SOFT_SKILLS = [
        'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Agile',
        'Scrum', 'Project Management', 'Critical Thinking', 'Adaptability'
    ]
    
    JOB_TITLES = {
        'entry': [
            'Junior Software Engineer', 'Associate Developer', 'Junior Data Analyst',
            'Entry Level Developer', 'Graduate Software Engineer', 'Intern Developer'
        ],
        'mid': [
            'Software Engineer', 'Full Stack Developer', 'Backend Developer',
            'Frontend Developer', 'Data Scientist', 'DevOps Engineer',
            'Mobile Developer', 'QA Engineer'
        ],
        'senior': [
            'Senior Software Engineer', 'Lead Developer', 'Principal Engineer',
            'Senior Data Scientist', 'Staff Engineer', 'Engineering Manager',
            'Tech Lead', 'Solutions Architect'
        ]
    }
    
    EDUCATION_LEVELS = [
        "Bachelor's Degree in Computer Science",
        "Bachelor's Degree in Software Engineering",
        "Master's Degree in Computer Science",
        "Bachelor's Degree in Information Technology",
        "Master's Degree in Data Science",
        "Bachelor's Degree in Mathematics",
        "Ph.D. in Computer Science",
        "Bachelor's Degree in Engineering"
    ]
    
    LOCATIONS = [
        'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX',
        'Boston, MA', 'Remote', 'Chicago, IL', 'Los Angeles, CA',
        'Denver, CO', 'Portland, OR', 'Remote - USA', 'London, UK',
        'Toronto, Canada', 'Berlin, Germany', 'Amsterdam, Netherlands'
    ]
    
    VISA_STATUSES = [
        'US Citizen', 'Green Card Holder', 'H1B Visa', 'Work Permit Required',
        'No Visa Required', 'Canadian Citizen', 'EU Citizen'
    ]
    
    SOURCES = ['LinkedIn', 'GitHub', 'Job Board', 'Referral', 'Company Website']
    
    def __init__(self):
        self.generated_emails = set()
    
    def generate_candidate(self, experience_level: str = None, 
                          skills_pool: List[str] = None) -> Dict:
        """
        Generate a single candidate profile
        
        Args:
            experience_level: 'entry', 'mid', or 'senior' (random if None)
            skills_pool: Specific skills to potentially include
        
        Returns:
            Dictionary with candidate data
        """
        # Determine experience level
        if not experience_level:
            experience_level = random.choice(['entry', 'mid', 'senior'])
        
        # Generate basic info
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        # Unique email
        email = self._generate_unique_email(first_name, last_name)
        
        # Experience years based on level
        if experience_level == 'entry':
            experience_years = random.randint(0, 2)
        elif experience_level == 'mid':
            experience_years = random.randint(3, 7)
        else:  # senior
            experience_years = random.randint(8, 15)
        
        # Skills - mix from different categories
        skills = self._generate_skills(experience_level, skills_pool)
        
        # Current position
        current_position = random.choice(self.JOB_TITLES[experience_level])
        
        # Generate availability
        availability_date = datetime.now() + timedelta(days=random.randint(7, 60))
        
        # Preferred interview times
        preferred_times = self._generate_interview_preferences()
        
        candidate = {
            'full_name': full_name,
            'email': email,
            'phone': fake.phone_number()[:20],  # Limit length
            'location': random.choice(self.LOCATIONS),
            'age': random.randint(22, 55),
            'nationality': fake.country(),
            'marital_status': random.choice(['Single', 'Married', 'Prefer not to say']),
            'visa_status': random.choice(self.VISA_STATUSES),
            'linkedin_url': f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
            'github_url': f"https://github.com/{first_name.lower()}{last_name[0].lower()}",
            'portfolio_url': f"https://{first_name.lower()}{last_name.lower()}.dev" if random.random() > 0.5 else None,
            'resume_url': f"https://storage.example.com/resumes/{email.split('@')[0]}.pdf",
            'skills': skills,
            'experience_years': experience_years,
            'current_position': current_position,
            'education': random.choice(self.EDUCATION_LEVELS),
            'availability_date': availability_date.date(),
            'preferred_interview_times': preferred_times,
            'source': random.choice(self.SOURCES)
        }
        
        return candidate
    
    def generate_candidates(self, count: int, 
                           experience_distribution: Dict[str, float] = None,
                           skills_pool: List[str] = None) -> List[Dict]:
        """
        Generate multiple candidate profiles
        
        Args:
            count: Number of candidates to generate
            experience_distribution: Dict with 'entry', 'mid', 'senior' percentages
            skills_pool: Skills to focus on
        
        Returns:
            List of candidate dictionaries
        """
        if not experience_distribution:
            experience_distribution = {
                'entry': 0.3,
                'mid': 0.5,
                'senior': 0.2
            }
        
        candidates = []
        for _ in range(count):
            # Randomly select experience level based on distribution
            rand = random.random()
            if rand < experience_distribution['entry']:
                level = 'entry'
            elif rand < experience_distribution['entry'] + experience_distribution['mid']:
                level = 'mid'
            else:
                level = 'senior'
            
            candidate = self.generate_candidate(level, skills_pool)
            candidates.append(candidate)
        
        logger.info(f"Generated {count} mock candidates")
        return candidates
    
    def generate_for_job(self, job_data: Dict, count: int = None, use_github: bool = True, github_count: int = 5) -> List[Dict]:
        """
        Generate candidates tailored to a specific job posting
        Supports both real GitHub search and mock candidate generation
        
        Args:
            job_data: Job information
            count: Total number of candidates (uses config default if None)
            use_github: If True, fetch real candidates from GitHub first
            github_count: Number of real candidates to fetch from GitHub (default 5)
        
        Returns:
            List of candidate dictionaries (mix of real + fake)
        """
        if count is None:
            count = ConfigManager.get_candidate_pool_size()
        
        # Extract job requirements
        required_skills = job_data.get('required_skills', [])
        experience_level = job_data.get('experience_level', 'mid')
        location = job_data.get('location', 'United States')
        
        candidates = []
        
        # Phase 1: Fetch real candidates from GitHub
        if use_github and github_count > 0:
            logger.info(f"🔍 Searching GitHub for {github_count} real candidates...")
            try:
                github_searcher = GitHubSearcher()
                real_candidates = github_searcher.search_developers(
                    skills=required_skills,
                    location=location,
                    max_results=github_count
                )
                candidates.extend(real_candidates)
                logger.info(f"✓ Found {len(real_candidates)} real candidates from GitHub")
            except Exception as e:
                logger.warning(f"GitHub search failed: {e}. Falling back to mock data only.")
        
        # Phase 2: Generate mock candidates to fill remaining slots
        remaining_count = count - len(candidates)
        if remaining_count > 0:
            logger.info(f"🎭 Generating {remaining_count} mock candidates...")
            
            # Generate candidates with varied skill matches
            # 30% - high match (most required skills)
            # 50% - medium match (some required skills)
            # 20% - low match (few required skills)
            
            high_match_count = int(remaining_count * 0.3)
            medium_match_count = int(remaining_count * 0.5)
            low_match_count = remaining_count - high_match_count - medium_match_count
            
            # High match candidates
            for _ in range(high_match_count):
                candidate = self.generate_candidate(experience_level, required_skills)
                candidates.append(candidate)
            
            # Medium match - some skills overlap
            for _ in range(medium_match_count):
                # Mix required skills with random skills
                mixed_skills = required_skills[:len(required_skills)//2]
                candidate = self.generate_candidate(experience_level, mixed_skills)
                candidates.append(candidate)
            
            # Low match - minimal overlap
            for _ in range(low_match_count):
                candidate = self.generate_candidate(experience_level)
                candidates.append(candidate)
            
            logger.info(f"✓ Generated {remaining_count} mock candidates")
        
        # Shuffle to randomize (mix real + fake)
        random.shuffle(candidates)
        
        logger.info(f"✓ Total candidates prepared: {len(candidates)} ({len(candidates) - remaining_count} real + {remaining_count} mock)")
        return candidates
    
    def _generate_unique_email(self, first_name: str, last_name: str) -> str:
        """Generate a unique email address"""
        base = f"{first_name.lower()}.{last_name.lower()}"
        domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'email.com'])
        
        email = f"{base}@{domain}"
        counter = 1
        
        while email in self.generated_emails:
            email = f"{base}{counter}@{domain}"
            counter += 1
        
        self.generated_emails.add(email)
        return email
    
    def _generate_skills(self, experience_level: str, 
                        focus_skills: List[str] = None) -> List[str]:
        """Generate skill set for a candidate"""
        skills = []
        
        # Number of skills based on experience
        if experience_level == 'entry':
            skill_count = random.randint(4, 8)
        elif experience_level == 'mid':
            skill_count = random.randint(8, 15)
        else:  # senior
            skill_count = random.randint(12, 20)
        
        # If focus skills provided, include some of them
        if focus_skills:
            # Include 50-80% of focus skills
            include_count = int(len(focus_skills) * random.uniform(0.5, 0.8))
            skills.extend(random.sample(focus_skills, min(include_count, len(focus_skills))))
        
        # Add skills from various categories
        all_skills = (
            self.PROGRAMMING_LANGUAGES + 
            self.WEB_FRAMEWORKS + 
            self.DATABASES + 
            self.CLOUD_DEVOPS + 
            self.DATA_ML_SKILLS + 
            self.SOFT_SKILLS
        )
        
        # Fill remaining slots
        while len(skills) < skill_count:
            skill = random.choice(all_skills)
            if skill not in skills:
                skills.append(skill)
        
        return skills
    
    def _generate_interview_preferences(self) -> Dict:
        """Generate preferred interview time slots"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = ['9:00 AM', '10:00 AM', '2:00 PM', '3:00 PM', '4:00 PM']
        
        preferred_count = random.randint(3, 5)
        preferences = []
        
        for _ in range(preferred_count):
            day = random.choice(days)
            time = random.choice(times)
            preferences.append(f"{day} {time}")
        
        return {
            'slots': preferences,
            'timezone': random.choice(['PST', 'EST', 'CST', 'MST', 'UTC'])
        }


if __name__ == '__main__':
    # Test the generator
    generator = CandidateGenerator()
    
    # Generate sample candidates
    candidates = generator.generate_candidates(5)
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n=== Candidate {i} ===")
        print(f"Name: {candidate['full_name']}")
        print(f"Email: {candidate['email']}")
        print(f"Experience: {candidate['experience_years']} years")
        print(f"Position: {candidate['current_position']}")
        print(f"Skills: {', '.join(candidate['skills'][:5])}...")
        print(f"Location: {candidate['location']}")
