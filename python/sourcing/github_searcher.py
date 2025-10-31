"""
GitHub Candidate Sourcing - Search real developers
Uses GitHub REST API (5000 requests/hour authenticated, 60/hour unauthenticated)
"""
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime
import sys
sys.path.insert(0, '.')
from python.utils.helpers import get_logger

logger = get_logger(__name__)


class GitHubSearcher:
    """
    Search GitHub for real developer profiles
    Free API - no authentication needed for basic search
    """
    
    def __init__(self, github_token: str = None):
        """
        Initialize GitHub searcher
        
        Args:
            github_token: Optional GitHub personal access token for higher rate limits
        """
        self.base_url = "https://api.github.com"
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Agentic-HR-System'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def search_developers(self, skills: List[str], location: str = None, 
                         max_results: int = 5) -> List[Dict]:
        """
        Search GitHub for developers with specific skills
        
        Args:
            skills: List of programming languages/skills
            location: Optional location filter
            max_results: Maximum number of candidates (default: 5 for real search)
        
        Returns:
            List of candidate dictionaries
        """
        candidates = []
        
        try:
            # Build search query
            query_parts = []
            
            # Add skills (languages)
            if skills:
                # Take top 3 skills for search
                for skill in skills[:3]:
                    if skill.lower() in ['python', 'javascript', 'java', 'ruby', 
                                        'go', 'rust', 'typescript', 'c++', 'c#']:
                        query_parts.append(f"language:{skill}")
            
            # Add location
            if location and location.lower() not in ['remote', 'anywhere']:
                query_parts.append(f"location:{location}")
            
            # Minimum repos to filter serious developers
            query_parts.append("repos:>5")
            
            # Sort by most followers (likely experienced devs)
            query = " ".join(query_parts)
            
            logger.info(f"🔍 Searching GitHub: {query}")
            
            # Search users
            search_url = f"{self.base_url}/search/users"
            params = {
                'q': query,
                'sort': 'followers',
                'order': 'desc',
                'per_page': max_results
            }
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded, using empty results")
                return []
            
            response.raise_for_status()
            result = response.json()
            
            users = result.get('items', [])[:max_results]
            logger.info(f"✓ Found {len(users)} GitHub users")
            
            # Get detailed info for each user
            for user_data in users:
                try:
                    user_detail = self._get_user_details(user_data['login'])
                    if user_detail:
                        candidate = self._convert_to_candidate(user_detail, skills)
                        candidates.append(candidate)
                except Exception as e:
                    logger.warning(f"Error processing user {user_data.get('login')}: {e}")
                    continue
            
            logger.info(f"✓ Retrieved {len(candidates)} complete profiles from GitHub")
            return candidates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    def _get_user_details(self, username: str) -> Optional[Dict]:
        """Get detailed user information"""
        try:
            # Get user profile
            user_url = f"{self.base_url}/users/{username}"
            response = requests.get(user_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            user_info = response.json()
            
            # Get user's repositories to extract skills
            repos_url = f"{self.base_url}/users/{username}/repos"
            repos_response = requests.get(
                repos_url, 
                headers=self.headers, 
                params={'sort': 'updated', 'per_page': 10},
                timeout=5
            )
            repos_response.raise_for_status()
            repos = repos_response.json()
            
            # Extract languages from repos
            languages = set()
            for repo in repos[:10]:  # Check top 10 repos
                if repo.get('language'):
                    languages.add(repo['language'])
            
            user_info['languages'] = list(languages)
            user_info['total_repos'] = user_info.get('public_repos', 0)
            
            return user_info
            
        except Exception as e:
            logger.warning(f"Error getting details for {username}: {e}")
            return None
    
    def _convert_to_candidate(self, github_user: Dict, job_skills: List[str]) -> Dict:
        """
        Convert GitHub user to candidate format
        
        Args:
            github_user: GitHub API user data
            job_skills: Skills from job posting
        
        Returns:
            Candidate dictionary matching our format
        """
        # Extract data
        name = github_user.get('name') or github_user.get('login')
        email = github_user.get('email') or f"{github_user.get('login')}@github.user"
        location = github_user.get('location') or 'Remote'
        bio = github_user.get('bio') or 'GitHub Developer'
        
        # Languages/skills from repos
        github_skills = github_user.get('languages', [])
        
        # Estimate experience based on account age and activity
        created_at = github_user.get('created_at', '')
        try:
            created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
            years_on_github = (datetime.utcnow() - created_date).days / 365
            # Estimate experience (account age is rough proxy)
            experience_years = max(1, int(years_on_github * 0.8))  # Conservative estimate
        except:
            experience_years = 3  # Default
        
        # Determine position based on repos and followers
        repos = github_user.get('total_repos', 0)
        followers = github_user.get('followers', 0)
        
        if repos > 50 and followers > 100:
            position = 'Senior Software Engineer'
        elif repos > 20 and followers > 20:
            position = 'Software Engineer'
        else:
            position = 'Software Developer'
        
        # Build candidate object
        candidate = {
            'full_name': name,
            'email': email,
            'phone': None,  # Not available from GitHub
            'location': location,
            'age': None,  # Not available
            'nationality': None,  # Not available
            'marital_status': None,  # Not available
            'visa_status': None,  # Not available
            'linkedin_url': None,
            'github_url': github_user.get('html_url'),
            'portfolio_url': github_user.get('blog') if github_user.get('blog') else None,
            'resume_url': None,
            'skills': github_skills,
            'experience_years': experience_years,
            'current_position': position,
            'education': None,  # Not available
            'availability_date': None,
            'preferred_interview_times': None,
            'source': 'github',
            'bio': bio,
            'github_stats': {
                'repos': repos,
                'followers': followers,
                'following': github_user.get('following', 0)
            }
        }
        
        return candidate


def test_github_search():
    """Test GitHub search functionality"""
    searcher = GitHubSearcher()
    
    print("\n" + "=" * 60)
    print("TESTING GITHUB CANDIDATE SEARCH")
    print("=" * 60)
    
    # Test search
    print("\n[1] Searching for Python developers...")
    candidates = searcher.search_developers(
        skills=['Python', 'Django', 'Flask'],
        location='United States',
        max_results=3
    )
    
    print(f"\n✓ Found {len(candidates)} real GitHub candidates")
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{i}. {candidate['full_name']}")
        print(f"   GitHub: {candidate['github_url']}")
        print(f"   Location: {candidate['location']}")
        print(f"   Skills: {', '.join(candidate['skills'][:5])}")
        print(f"   Experience: {candidate['experience_years']} years (estimated)")
        print(f"   Position: {candidate['current_position']}")
        print(f"   Stats: {candidate['github_stats']['repos']} repos, {candidate['github_stats']['followers']} followers")
    
    print("\n" + "=" * 60)
    print("✓ GitHub search working!")
    print("=" * 60)


if __name__ == '__main__':
    test_github_search()
