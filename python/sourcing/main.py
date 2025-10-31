"""
Phase 1: Candidate Sourcing Main Orchestrator
Coordinates job parsing, candidate generation, scoring, and ranking
"""
from typing import Dict, List
from datetime import datetime
from python.sourcing.job_parser import JobParser
from python.sourcing.candidate_generator import CandidateGenerator
from python.sourcing.candidate_scorer import CandidateRanker
from python.utils.helpers import (
    get_logger, ConfigManager, save_json, ensure_directories, log_action
)
from database.models import Job, Candidate, JobApplication, get_session

logger = get_logger(__name__)


class CandidateSourcingEngine:
    """
    Main engine for Phase 1: Job Matching & Candidate Sourcing
    Demonstrates agentic AI principles through intelligent candidate discovery and ranking
    """
    
    def __init__(self, use_ai_weights: bool = True, use_mock_data: bool = None):
        """
        Initialize the sourcing engine
        
        Args:
            use_ai_weights: Enable AI-driven adaptive ranking (agentic behavior)
            use_mock_data: Use mock data generation (defaults to config)
        """
        self.job_parser = JobParser()
        self.candidate_generator = CandidateGenerator()
        self.ranker = CandidateRanker(use_ai_weights=use_ai_weights)
        
        self.use_mock_data = use_mock_data if use_mock_data is not None else ConfigManager.is_mock_data_enabled()
        self.use_ai = use_ai_weights
        
        ensure_directories()
        
        logger.info("🚀 Candidate Sourcing Engine initialized")
        logger.info(f"   AI-driven ranking: {'✓' if use_ai_weights else '✗'}")
        logger.info(f"   Mock data: {'✓' if self.use_mock_data else '✗'}")
    
    def process_job_posting(self, job_data: Dict, save_to_db: bool = True) -> Dict:
        """
        Process a new job posting
        
        Args:
            job_data: Raw job posting data
            save_to_db: Save to database
        
        Returns:
            Processed job data with ID
        """
        logger.info(f"📝 Processing job posting: {job_data.get('title')}")
        
        # Parse and validate job
        parsed_job = self.job_parser.parse(job_data)
        is_valid, errors = self.job_parser.validate(parsed_job)
        
        if not is_valid:
            logger.error(f"Job validation failed: {errors}")
            raise ValueError(f"Invalid job data: {errors}")
        
        # Save to database
        if save_to_db:
            job_id = self._save_job_to_db(parsed_job)
            parsed_job['job_id'] = job_id
            
            log_action('candidate_sourcing', 
                      f"Created new job posting: {parsed_job['title']}", 
                      {'job_id': job_id})
        
        # Save to JSON for n8n integration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_json(parsed_job, f"data/jobs/job_{timestamp}.json")
        
        logger.info(f"✓ Job processed successfully: {parsed_job.get('title')}")
        return parsed_job
    
    def source_candidates(self, job: Dict, candidate_count: int = None, use_github: bool = True) -> List[Dict]:
        """
        Source candidates for a job (GitHub real data + mock data)
        
        Args:
            job: Job posting data
            candidate_count: Number of candidates to source (default from config)
            use_github: If True, fetch real candidates from GitHub first (default True)
        
        Returns:
            List of candidate dictionaries (mix of real + mock)
        """
        if candidate_count is None:
            candidate_count = ConfigManager.get_candidate_pool_size()
        
        logger.info(f"🔍 Sourcing {candidate_count} candidates for: {job['title']}")
        
        # Determine GitHub search count (25% of total, max 5)
        github_count = min(int(candidate_count * 0.25), 5) if use_github else 0
        
        if self.use_mock_data or not use_github:
            # Pure mock mode
            candidates = self.candidate_generator.generate_for_job(job, candidate_count, use_github=False)
            log_action('candidate_sourcing', 
                      f"Generated {len(candidates)} mock candidates", 
                      {'job_title': job['title']})
        else:
            # Hybrid mode: Real GitHub + Mock
            candidates = self.candidate_generator.generate_for_job(
                job, 
                candidate_count, 
                use_github=True, 
                github_count=github_count
            )
            
            real_count = sum(1 for c in candidates if c.get('source') == 'github')
            mock_count = len(candidates) - real_count
            
            log_action('candidate_sourcing', 
                      f"Sourced {len(candidates)} candidates ({real_count} real + {mock_count} mock)", 
                      {'job_title': job['title'], 'real': real_count, 'mock': mock_count})
        
        logger.info(f"✓ Sourced {len(candidates)} candidates")
        return candidates
    
    def rank_and_shortlist(self, candidates: List[Dict], job: Dict, 
                          top_n: int = None) -> List[Dict]:
        """
        Rank candidates and create shortlist
        
        Args:
            candidates: List of candidates
            job: Job posting
            top_n: Number of top candidates to shortlist
        
        Returns:
            Ranked and scored candidates
        """
        if top_n is None:
            top_n = ConfigManager.get_top_candidates_count()
        
        logger.info(f"📊 Ranking {len(candidates)} candidates...")
        logger.info(f"   Using {'AI-driven adaptive' if self.use_ai else 'rule-based'} ranking")
        
        # Rank candidates
        shortlist = self.ranker.get_shortlist(candidates, job, count=top_n)
        
        log_action('candidate_sourcing', 
                  f"Created shortlist of {len(shortlist)} candidates", 
                  {
                      'job_title': job['title'],
                      'top_score': shortlist[0]['match_score'] if shortlist else 0,
                      'avg_score': sum(c['match_score'] for c in shortlist) / len(shortlist) if shortlist else 0
                  })
        
        logger.info(f"✓ Shortlisted top {len(shortlist)} candidates")
        return shortlist
    
    def save_candidates_to_db(self, candidates: List[Dict], job_id: int) -> List[int]:
        """
        Save candidates and their applications to database
        
        Args:
            candidates: List of candidate dictionaries (with scores)
            job_id: Job ID
        
        Returns:
            List of application IDs
        """
        logger.info(f"💾 Saving {len(candidates)} candidates to database...")
        
        session = get_session()
        application_ids = []
        
        try:
            for candidate_data in candidates:
                # Check if candidate exists
                existing = session.query(Candidate).filter_by(
                    email=candidate_data['email']
                ).first()
                
                if existing:
                    candidate = existing
                else:
                    # Create new candidate
                    candidate = Candidate(
                        full_name=candidate_data['full_name'],
                        email=candidate_data['email'],
                        phone=candidate_data.get('phone'),
                        location=candidate_data.get('location'),
                        age=candidate_data.get('age'),
                        nationality=candidate_data.get('nationality'),
                        marital_status=candidate_data.get('marital_status'),
                        visa_status=candidate_data.get('visa_status'),
                        linkedin_url=candidate_data.get('linkedin_url'),
                        github_url=candidate_data.get('github_url'),
                        portfolio_url=candidate_data.get('portfolio_url'),
                        resume_url=candidate_data.get('resume_url'),
                        skills=candidate_data.get('skills', []),
                        experience_years=candidate_data.get('experience_years'),
                        current_position=candidate_data.get('current_position'),
                        education=candidate_data.get('education'),
                        availability_date=candidate_data.get('availability_date'),
                        preferred_interview_times=candidate_data.get('preferred_interview_times'),
                        source=candidate_data.get('source', 'system')
                    )
                    session.add(candidate)
                    session.flush()
                
                # Create application
                application = JobApplication(
                    job_id=job_id,
                    candidate_id=candidate.candidate_id,
                    status='shortlisted',
                    match_score=candidate_data.get('match_score'),
                    match_details=candidate_data.get('match_details'),
                    ranking=candidate_data.get('ranking')
                )
                session.add(application)
                session.flush()
                application_ids.append(application.application_id)
            
            session.commit()
            logger.info(f"✓ Saved {len(candidates)} candidates to database")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            raise
        finally:
            session.close()
        
        return application_ids
    
    def run_full_pipeline(self, job_data: Dict) -> Dict:
        """
        Run the complete Phase 1 pipeline
        
        Args:
            job_data: Raw job posting data
        
        Returns:
            Dictionary with results including job, candidates, and shortlist
        """
        logger.info("=" * 60)
        logger.info("🚀 STARTING PHASE 1: CANDIDATE SOURCING PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Process job posting
        job = self.process_job_posting(job_data, save_to_db=True)
        
        # Step 2: Source candidates
        candidates = self.source_candidates(job)
        
        # Step 3: Rank and shortlist
        shortlist = self.rank_and_shortlist(candidates, job)
        
        # Step 4: Save to database
        application_ids = self.save_candidates_to_db(shortlist, job['job_id'])
        
        # Step 5: Generate report
        report = self._generate_report(job, shortlist)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_json(report, f"reports/sourcing_report_{timestamp}.json")
        
        logger.info("=" * 60)
        logger.info("✓ PHASE 1 PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return {
            'job': job,
            'total_candidates_sourced': len(candidates),
            'shortlist_count': len(shortlist),
            'shortlist': shortlist,
            'application_ids': application_ids,
            'report': report
        }
    
    def _save_job_to_db(self, job_data: Dict) -> int:
        """Save job to database and return ID"""
        session = get_session()
        
        try:
            job = Job(
                title=job_data['title'],
                description=job_data['description'],
                required_skills=job_data['required_skills'],
                experience_level=job_data['experience_level'],
                location=job_data.get('location'),
                employment_type=job_data.get('employment_type'),
                salary_range=job_data.get('salary_range'),
                department=job_data.get('department'),
                status='active'
            )
            session.add(job)
            session.commit()
            job_id = job.job_id
            session.close()
            return job_id
        except Exception as e:
            session.rollback()
            session.close()
            raise e
    
    def _generate_report(self, job: Dict, shortlist: List[Dict]) -> Dict:
        """Generate sourcing report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'job_title': job['title'],
            'job_id': job.get('job_id'),
            'shortlist_size': len(shortlist),
            'top_candidates': [
                {
                    'rank': c['ranking'],
                    'name': c['full_name'],
                    'email': c['email'],
                    'score': c['match_score'],
                    'experience_years': c['experience_years'],
                    'current_position': c['current_position'],
                    'skills_matched': c['match_details']['skills_matched'],
                    'skills_missing': c['match_details']['skills_missing']
                }
                for c in shortlist[:5]
            ],
            'statistics': {
                'average_score': sum(c['match_score'] for c in shortlist) / len(shortlist) if shortlist else 0,
                'highest_score': shortlist[0]['match_score'] if shortlist else 0,
                'lowest_score': shortlist[-1]['match_score'] if shortlist else 0,
                'average_experience': sum(c['experience_years'] for c in shortlist) / len(shortlist) if shortlist else 0
            }
        }


def main():
    """
    Main function to demonstrate Phase 1
    """
    from python.sourcing.job_parser import create_sample_jobs
    
    # Initialize engine with AI-driven ranking
    engine = CandidateSourcingEngine(use_ai_weights=True, use_mock_data=True)
    
    # Get sample job
    sample_jobs = create_sample_jobs()
    job_data = sample_jobs[0]  # Senior Python Developer
    
    # Run pipeline
    results = engine.run_full_pipeline(job_data)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Job: {results['job']['title']}")
    print(f"Total Candidates Sourced: {results['total_candidates_sourced']}")
    print(f"Shortlisted: {results['shortlist_count']}")
    print(f"\nTop 5 Candidates:")
    
    for candidate in results['shortlist'][:5]:
        print(f"\n  {candidate['ranking']}. {candidate['full_name']}")
        print(f"     Score: {candidate['match_score']:.2f} | Experience: {candidate['experience_years']} years")
        print(f"     Position: {candidate['current_position']}")
        print(f"     Matched Skills: {', '.join(candidate['match_details']['skills_matched'][:3])}")


if __name__ == '__main__':
    main()
