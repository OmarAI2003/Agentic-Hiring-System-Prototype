"""
Intelligent Candidate Scoring and Ranking System
Demonstrates agentic AI principles by autonomously determining optimal ranking strategies
"""
from typing import Dict, List, Tuple
import re
import json
from python.utils.helpers import (
    get_logger, calculate_percentage_match, normalize_text, log_decision
)
from python.utils.groq_client import GroqLLM

logger = get_logger(__name__)


class CandidateScorer:
    """
    Scores candidates based on multiple factors with agentic weight adjustment
    """
    
    def __init__(self, use_ai_weights: bool = True):
        """
        Initialize scorer
        
        Args:
            use_ai_weights: Use AI to determine optimal weights (agentic behavior)
        """
        self.use_ai_weights = use_ai_weights
        self.llm = GroqLLM() if use_ai_weights else None
        self.weights = None
    
    def score_candidate(self, candidate: Dict, job: Dict) -> Tuple[float, Dict]:
        """
        Score a single candidate against a job posting
        
        Args:
            candidate: Candidate information
            job: Job posting information
        
        Returns:
            (overall_score, detailed_breakdown)
        """
        # Calculate individual factor scores
        skills_score = self._score_skills_match(candidate, job)
        experience_score = self._score_experience(candidate, job)
        location_score = self._score_location(candidate, job)
        education_score = self._score_education(candidate, job)
        
        # Get or determine weights (agentic decision)
        if not self.weights:
            self.weights = self._determine_weights(job)
        
        # Calculate weighted overall score
        overall_score = (
            skills_score * self.weights['skills_match'] +
            experience_score * self.weights['experience_match'] +
            location_score * self.weights['location_match'] +
            education_score * self.weights['education_match']
        )
        
        # Detailed breakdown
        breakdown = {
            'overall_score': round(overall_score, 2),
            'skills_score': round(skills_score, 2),
            'experience_score': round(experience_score, 2),
            'location_score': round(location_score, 2),
            'education_score': round(education_score, 2),
            'weights_used': self.weights.copy(),
            'skills_matched': self._get_matched_skills(candidate, job),
            'skills_missing': self._get_missing_skills(candidate, job)
        }
        
        return overall_score, breakdown
    
    def _determine_weights(self, job: Dict) -> Dict[str, float]:
        """
        AGENTIC BEHAVIOR: Intelligently determine scoring weights based on job characteristics
        
        This is where autonomous decision-making happens!
        """
        if self.use_ai_weights and self.llm:
            # AI makes the decision autonomously
            logger.info("🤖 AI autonomously determining ranking weights...")
            
            try:
                # Construct prompt for AI to determine weights
                prompt = f"""Analyze this job posting and determine optimal scoring weights for candidate ranking.

Job Title: {job.get('title', 'Unknown')}
Required Skills: {', '.join(job.get('required_skills', []))}
Experience Level: {job.get('experience_level', 'mid')}
Location: {job.get('location', 'Any')}

Return ONLY a JSON object with these 4 weights (must sum to 1.0):
{{
  "skills_match": <weight 0-1>,
  "experience_match": <weight 0-1>,
  "location_match": <weight 0-1>,
  "education_match": <weight 0-1>
}}"""

                response = self.llm.generate(prompt, temperature=0.3)
                
                # Parse JSON response
                import json
                # Extract JSON from response
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    weights = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
                
                # Validate and normalize weights
                total = sum([
                    weights.get('skills_match', 0.4),
                    weights.get('experience_match', 0.3),
                    weights.get('location_match', 0.15),
                    weights.get('education_match', 0.15)
                ])
                
                if total > 0:
                    # Normalize to sum to 1.0
                    normalized_weights = {
                        'skills_match': weights.get('skills_match', 0.4) / total,
                        'experience_match': weights.get('experience_match', 0.3) / total,
                        'location_match': weights.get('location_match', 0.15) / total,
                        'education_match': weights.get('education_match', 0.15) / total
                    }
                    
                    log_decision(
                        'candidate_scoring',
                        f"AI determined weights for {job.get('title')}: {normalized_weights}",
                        {'reasoning': weights.get('reasoning', 'N/A')}
                    )
                    
                    return normalized_weights
            except Exception as e:
                logger.error(f"Error in AI weight determination: {str(e)}")
        
        # Fallback: Rule-based adaptive weights (still somewhat intelligent)
        return self._adaptive_rule_based_weights(job)
    
    def _adaptive_rule_based_weights(self, job: Dict) -> Dict[str, float]:
        """
        Fallback intelligent weight adjustment based on job characteristics
        """
        experience_level = job.get('experience_level', 'mid').lower()
        title_lower = job.get('title', '').lower()
        
        # Base weights
        weights = {
            'skills_match': 0.40,
            'experience_match': 0.30,
            'location_match': 0.15,
            'education_match': 0.15
        }
        
        # Adjust based on experience level
        if experience_level == 'senior':
            # For senior roles, prioritize experience more
            weights['experience_match'] = 0.35
            weights['skills_match'] = 0.40
            weights['education_match'] = 0.10
            weights['location_match'] = 0.15
        elif experience_level == 'entry':
            # For entry roles, education and skills matter more
            weights['education_match'] = 0.25
            weights['skills_match'] = 0.45
            weights['experience_match'] = 0.15
            weights['location_match'] = 0.15
        
        # Adjust for remote positions
        location = job.get('location', '').lower()
        if 'remote' in location:
            # Location matters less for remote jobs
            weights['location_match'] = 0.05
            # Redistribute to skills
            weights['skills_match'] += 0.10
        
        # Adjust for technical roles
        if any(kw in title_lower for kw in ['engineer', 'developer', 'architect', 'scientist']):
            weights['skills_match'] = min(0.50, weights['skills_match'] + 0.05)
            weights['education_match'] = max(0.10, weights['education_match'] - 0.05)
        
        log_decision(
            'candidate_scoring',
            f"Rule-based weights for {job.get('title')}: {weights}",
            {'experience_level': experience_level, 'title': title_lower}
        )
        
        return weights
    
    def _score_skills_match(self, candidate: Dict, job: Dict) -> float:
        """Score skills alignment (0-100)"""
        required_skills = job.get('required_skills', [])
        candidate_skills = candidate.get('skills', [])
        
        if not required_skills:
            return 100.0
        
        # Basic percentage match
        base_score = calculate_percentage_match(required_skills, candidate_skills)
        
        # Bonus for additional relevant skills (shows initiative)
        if len(candidate_skills) > len(required_skills):
            bonus = min(10, (len(candidate_skills) - len(required_skills)) * 2)
            base_score = min(100, base_score + bonus)
        
        return base_score
    
    def _score_experience(self, candidate: Dict, job: Dict) -> float:
        """Score experience level match (0-100)"""
        candidate_years = candidate.get('experience_years', 0)
        required_level = job.get('experience_level', 'mid').lower()
        
        # Define ideal ranges
        level_ranges = {
            'entry': (0, 2),
            'mid': (3, 7),
            'senior': (8, 15)
        }
        
        min_years, max_years = level_ranges.get(required_level, (3, 7))
        
        if min_years <= candidate_years <= max_years:
            # Perfect match
            return 100.0
        elif candidate_years < min_years:
            # Under-qualified (penalize more)
            gap = min_years - candidate_years
            return max(0, 100 - (gap * 20))
        else:
            # Over-qualified (penalize less - could be good)
            gap = candidate_years - max_years
            return max(50, 100 - (gap * 10))
    
    def _score_location(self, candidate: Dict, job: Dict) -> float:
        """Score location match (0-100)"""
        job_location = normalize_text(job.get('location', ''))
        candidate_location = normalize_text(candidate.get('location', ''))
        
        # Remote jobs - location doesn't matter much
        if 'remote' in job_location:
            return 100.0
        
        # Exact match
        if job_location == candidate_location:
            return 100.0
        
        # Same city/state partial match
        job_parts = job_location.split(',')
        candidate_parts = candidate_location.split(',')
        
        matches = sum(1 for jp in job_parts if any(jp.strip() in cp for cp in candidate_parts))
        
        if matches > 0:
            return 70.0 + (matches * 10)
        
        # Candidate is remote
        if 'remote' in candidate_location:
            return 80.0
        
        # Different location
        return 40.0
    
    def _score_education(self, candidate: Dict, job: Dict) -> float:
        """Score education level (0-100)"""
        education = candidate.get('education', '')
        
        # Handle None or missing education
        if education is None or education == '':
            return 60.0  # Default score for unknown education
        
        education = normalize_text(education)
        
        # Simple scoring based on degree level
        if 'phd' in education or 'ph.d' in education or 'doctorate' in education:
            return 100.0
        elif 'master' in education or "master's" in education:
            return 90.0
        elif 'bachelor' in education or "bachelor's" in education:
            return 80.0
        else:
            return 60.0
    
    def _get_matched_skills(self, candidate: Dict, job: Dict) -> List[str]:
        """Get list of skills that match between candidate and job"""
        required = set([normalize_text(s) for s in job.get('required_skills', [])])
        candidate_skills = set([normalize_text(s) for s in candidate.get('skills', [])])
        return list(required.intersection(candidate_skills))
    
    def _get_missing_skills(self, candidate: Dict, job: Dict) -> List[str]:
        """Get list of required skills the candidate is missing"""
        required = set([normalize_text(s) for s in job.get('required_skills', [])])
        candidate_skills = set([normalize_text(s) for s in candidate.get('skills', [])])
        return list(required - candidate_skills)


class CandidateRanker:
    """
    Ranks and shortlists candidates based on scoring
    """
    
    def __init__(self, use_ai_weights: bool = True):
        self.scorer = CandidateScorer(use_ai_weights)
    
    def rank_candidates(self, candidates: List[Dict], job: Dict, 
                       top_n: int = None) -> List[Dict]:
        """
        Score and rank all candidates for a job
        
        Args:
            candidates: List of candidate dictionaries
            job: Job posting dictionary
            top_n: Number of top candidates to return (None = all)
        
        Returns:
            List of candidates with scores, sorted by rank
        """
        logger.info(f"Ranking {len(candidates)} candidates for job: {job.get('title')}")
        
        scored_candidates = []
        
        for candidate in candidates:
            score, breakdown = self.scorer.score_candidate(candidate, job)
            
            candidate_with_score = candidate.copy()
            candidate_with_score['match_score'] = score
            candidate_with_score['match_details'] = breakdown
            
            scored_candidates.append(candidate_with_score)
        
        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Assign rankings
        for rank, candidate in enumerate(scored_candidates, 1):
            candidate['ranking'] = rank
        
        # Apply AI-based assessment for top candidates
        if self.scorer.use_ai_weights and top_n:
            scored_candidates = self._enhance_top_candidates(
                scored_candidates[:top_n], 
                job
            ) + scored_candidates[top_n:]
        
        logger.info(f"✓ Ranked candidates. Top score: {scored_candidates[0]['match_score']:.2f}")
        
        return scored_candidates[:top_n] if top_n else scored_candidates
    
    def _enhance_top_candidates(self, top_candidates: List[Dict], job: Dict) -> List[Dict]:
        """
        Use AI to provide additional assessment for top candidates
        """
        logger.info("🤖 AI enhancing assessment of top candidates...")
        
        for candidate in top_candidates:
            try:
                # Construct assessment prompt
                prompt = f"""Assess this candidate's fit for the job:

Job: {job.get('title')}
Required Skills: {', '.join(job.get('required_skills', [])[:5])}

Candidate: {candidate.get('full_name')}
Skills: {', '.join(candidate.get('skills', [])[:5])}
Experience: {candidate.get('experience_years')} years
Position: {candidate.get('current_position')}
Match Score: {candidate.get('match_score', 0):.2f}

Provide a brief (2-3 sentence) assessment of their fit. Be honest about strengths and potential concerns."""

                assessment = self.scorer.llm.generate(prompt, temperature=0.5)
                candidate['ai_assessment'] = assessment
            except Exception as e:
                logger.error(f"Error in AI assessment: {str(e)}")
                candidate['ai_assessment'] = None
        
        return top_candidates
    
    def get_shortlist(self, candidates: List[Dict], job: Dict, 
                     count: int = 10) -> List[Dict]:
        """
        Get shortlist of best candidates
        
        Args:
            candidates: All candidates
            job: Job posting
            count: Number to shortlist
        
        Returns:
            Shortlisted candidates with scores
        """
        ranked = self.rank_candidates(candidates, job, top_n=count)
        
        logger.info(f"📋 Shortlisted top {len(ranked)} candidates")
        
        return ranked


if __name__ == '__main__':
    # Test the scoring system
    print("Testing Candidate Scoring System...")
    
    # Mock data
    job = {
        'title': 'Senior Python Developer',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
        'experience_level': 'senior',
        'location': 'San Francisco, CA'
    }
    
    candidates = [
        {
            'full_name': 'Alice Johnson',
            'skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes'],
            'experience_years': 8,
            'location': 'San Francisco, CA',
            'education': "Master's Degree in Computer Science"
        },
        {
            'full_name': 'Bob Smith',
            'skills': ['Python', 'Flask', 'MySQL', 'GCP'],
            'experience_years': 5,
            'location': 'Remote',
            'education': "Bachelor's Degree in Computer Science"
        }
    ]
    
    ranker = CandidateRanker(use_ai_weights=False)
    ranked = ranker.rank_candidates(candidates, job)
    
    for candidate in ranked:
        print(f"\n{candidate['full_name']} - Rank: {candidate['ranking']}")
        print(f"Score: {candidate['match_score']:.2f}")
        print(f"Skills match: {candidate['match_details']['skills_score']:.2f}")
