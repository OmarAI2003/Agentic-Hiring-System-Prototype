"""
Phase 5: Post-Interview Evaluation & AI Recommendation System
Analyzes feedback and generates intelligent hiring recommendations
"""
import json
from typing import Dict, List
from datetime import datetime
from python.utils.helpers import get_logger, save_json, log_decision, log_action
from python.utils.groq_client import GroqLLM
from database.models import (
    InterviewFeedback, AIRecommendation, JobApplication, 
    Candidate, Job, get_session
)

logger = get_logger(__name__)


class FeedbackAnalyzer:
    """
    Analyzes interview feedback and generates AI-powered recommendations
    Demonstrates agentic AI through holistic candidate assessment
    """
    
    RECOMMENDATION_LEVELS = ['strong_hire', 'hire', 'consider', 'reject']
    
    def __init__(self):
        self.llm = GroqLLM()
        logger.info("Feedback Analyzer initialized")
    
    def analyze_feedback(self, feedback: Dict, candidate: Dict, job: Dict) -> Dict:
        """
        Analyze interview feedback and generate recommendation
        
        Args:
            feedback: Interview feedback data
            candidate: Candidate information
            job: Job posting information
        
        Returns:
            Dictionary with recommendation and analysis
        """
        logger.info(f"🤖 Analyzing feedback for {candidate.get('full_name')}...")
        
        # Calculate aggregate scores
        aggregate_scores = self._calculate_aggregate_scores(feedback)
        
        # AGENTIC DECISION: AI analyzes holistically (not just averaging)
        recommendation = self._generate_ai_recommendation(
            feedback, aggregate_scores, candidate, job
        )
        
        log_decision(
            'evaluation',
            f"AI recommendation for {candidate.get('full_name')}: {recommendation['overall_recommendation']}",
            {
                'confidence': recommendation.get('confidence_score'),
                'reasoning': recommendation.get('justification')[:100]
            }
        )
        
        logger.info(f"✓ Analysis complete: {recommendation['overall_recommendation']} (confidence: {recommendation.get('confidence_score')}%)")
        
        return recommendation
    
    def _calculate_aggregate_scores(self, feedback: Dict) -> Dict:
        """Calculate aggregate scores from feedback"""
        ratings = {
            'technical_skills': feedback.get('technical_skills_rating', 0),
            'communication_skills': feedback.get('communication_skills_rating', 0),
            'culture_fit': feedback.get('culture_fit_rating', 0),
            'problem_solving': feedback.get('problem_solving_rating', 0)
        }
        
        # Simple average
        average = sum(ratings.values()) / len(ratings) if ratings else 0
        
        # Weighted average (technical and problem-solving more important)
        weighted = (
            ratings['technical_skills'] * 0.35 +
            ratings['problem_solving'] * 0.35 +
            ratings['communication_skills'] * 0.15 +
            ratings['culture_fit'] * 0.15
        )
        
        return {
            'individual_ratings': ratings,
            'simple_average': round(average, 2),
            'weighted_average': round(weighted, 2),
            'max_rating': max(ratings.values()) if ratings else 0,
            'min_rating': min(ratings.values()) if ratings else 0
        }
    
    def _generate_ai_recommendation(self, feedback: Dict, aggregate_scores: Dict,
                                   candidate: Dict, job: Dict) -> Dict:
        """
        AGENTIC BEHAVIOR: AI makes holistic hiring recommendation
        Goes beyond simple score averaging - considers context, patterns, concerns
        """
        # Build comprehensive context
        context = self._build_context(feedback, aggregate_scores, candidate, job)
        
        prompt = f"""You are an expert HR AI making a final hiring recommendation.

INTERVIEW FEEDBACK ANALYSIS

Job Position: {job.get('title')} ({job.get('experience_level')} level)
Candidate: {candidate.get('full_name')} ({candidate.get('experience_years')} years experience)

Ratings (out of 10):
- Technical Skills: {feedback.get('technical_skills_rating')}/10
- Communication: {feedback.get('communication_skills_rating')}/10
- Culture Fit: {feedback.get('culture_fit_rating')}/10
- Problem Solving: {feedback.get('problem_solving_rating')}/10

Weighted Average: {aggregate_scores['weighted_average']}/10

Interviewer's Comments:
Strengths: {feedback.get('strengths', 'N/A')}
Concerns: {feedback.get('concerns', 'N/A')}
Additional Notes: {feedback.get('qualitative_comments', 'N/A')}

Candidate Background:
- Current Position: {candidate.get('current_position')}
- Education: {candidate.get('education')}
- Key Skills: {', '.join(candidate.get('skills', [])[:5])}

TASK: Make a hiring recommendation. Consider:
1. Not just scores, but patterns (e.g., low culture fit vs low technical)
2. Severity of concerns mentioned
3. Candidate's potential for growth
4. Alignment with job requirements
5. Risk vs opportunity assessment

Respond in JSON:
{{
    "overall_recommendation": "strong_hire|hire|consider|reject",
    "confidence_score": 85,
    "justification": "2-3 sentence explanation of the recommendation",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "key_weaknesses": ["weakness1", "weakness2"],
    "suggested_next_steps": "What should HR do next",
    "risk_assessment": "Low|Medium|High risk of bad hire",
    "growth_potential": "Assessment of candidate's growth potential"
}}
"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.3, max_tokens=1500)
            recommendation = json.loads(response)
            
            # Validate recommendation level
            if recommendation.get('overall_recommendation') not in self.RECOMMENDATION_LEVELS:
                recommendation['overall_recommendation'] = self._fallback_recommendation(
                    aggregate_scores['weighted_average']
                )
            
            # Ensure confidence is in valid range
            confidence = recommendation.get('confidence_score', 50)
            recommendation['confidence_score'] = max(0, min(100, confidence))
            
            return recommendation
            
        except Exception as e:
            logger.error(f"AI recommendation failed: {str(e)}")
            return self._rule_based_recommendation(feedback, aggregate_scores)
    
    def _build_context(self, feedback: Dict, aggregate_scores: Dict,
                      candidate: Dict, job: Dict) -> Dict:
        """Build comprehensive context for AI analysis"""
        return {
            'feedback': feedback,
            'scores': aggregate_scores,
            'candidate_summary': {
                'name': candidate.get('full_name'),
                'experience': candidate.get('experience_years'),
                'position': candidate.get('current_position'),
                'education': candidate.get('education')
            },
            'job_summary': {
                'title': job.get('title'),
                'level': job.get('experience_level'),
                'department': job.get('department')
            }
        }
    
    def _rule_based_recommendation(self, feedback: Dict, aggregate_scores: Dict) -> Dict:
        """Fallback rule-based recommendation"""
        weighted_avg = aggregate_scores['weighted_average']
        
        # Determine recommendation based on scores
        if weighted_avg >= 8.5:
            recommendation = 'strong_hire'
            confidence = 90
            justification = "Exceptional performance across all evaluation criteria."
        elif weighted_avg >= 7.0:
            recommendation = 'hire'
            confidence = 75
            justification = "Strong performance with solid skills and good fit."
        elif weighted_avg >= 5.5:
            recommendation = 'consider'
            confidence = 60
            justification = "Mixed results. Further discussion recommended."
        else:
            recommendation = 'reject'
            confidence = 70
            justification = "Performance below required standards for the role."
        
        # Extract strengths and concerns
        strengths_text = feedback.get('strengths', '')
        concerns_text = feedback.get('concerns', '')
        
        return {
            'overall_recommendation': recommendation,
            'confidence_score': confidence,
            'justification': justification,
            'key_strengths': [s.strip() for s in strengths_text.split(',')[:3]] if strengths_text else ['Good performance'],
            'key_weaknesses': [c.strip() for c in concerns_text.split(',')[:3]] if concerns_text else ['No major concerns'],
            'suggested_next_steps': self._get_next_steps(recommendation),
            'analysis_method': 'rule_based'
        }
    
    def _fallback_recommendation(self, score: float) -> str:
        """Simple score-based recommendation"""
        if score >= 8.5:
            return 'strong_hire'
        elif score >= 7.0:
            return 'hire'
        elif score >= 5.5:
            return 'consider'
        else:
            return 'reject'
    
    def _get_next_steps(self, recommendation: str) -> str:
        """Get suggested next steps based on recommendation"""
        next_steps = {
            'strong_hire': "Proceed with offer. Prepare compensation package.",
            'hire': "Move forward with offer after team discussion.",
            'consider': "Schedule additional interview or assessment. Discuss concerns with hiring manager.",
            'reject': "Send polite rejection email. Keep in talent pool for future opportunities."
        }
        return next_steps.get(recommendation, "Review and discuss with hiring team.")
    
    def save_recommendation_to_db(self, recommendation: Dict, job_id: int,
                                 candidate_id: int) -> int:
        """
        Save AI recommendation to database
        
        Returns:
            Recommendation ID
        """
        logger.info("💾 Saving recommendation to database...")
        
        session = get_session()
        
        try:
            ai_rec = AIRecommendation(
                job_id=job_id,
                candidate_id=candidate_id,
                overall_recommendation=recommendation['overall_recommendation'],
                confidence_score=recommendation.get('confidence_score'),
                justification=recommendation.get('justification'),
                key_strengths=recommendation.get('key_strengths', []),
                key_weaknesses=recommendation.get('key_weaknesses', []),
                suggested_next_steps=recommendation.get('suggested_next_steps'),
                analysis_data=recommendation
            )
            session.add(ai_rec)
            session.commit()
            
            rec_id = ai_rec.recommendation_id
            session.close()
            
            logger.info(f"✓ Saved recommendation (ID: {rec_id})")
            return rec_id
            
        except Exception as e:
            session.rollback()
            session.close()
            logger.error(f"Error saving recommendation: {str(e)}")
            raise
    
    def generate_report(self, recommendation: Dict, candidate: Dict, 
                       job: Dict, feedback: Dict) -> Dict:
        """Generate comprehensive evaluation report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'candidate': {
                'name': candidate.get('full_name'),
                'email': candidate.get('email'),
                'experience': candidate.get('experience_years'),
                'current_position': candidate.get('current_position')
            },
            'job': {
                'title': job.get('title'),
                'level': job.get('experience_level'),
                'job_id': job.get('job_id')
            },
            'interview_ratings': {
                'technical_skills': feedback.get('technical_skills_rating'),
                'communication': feedback.get('communication_skills_rating'),
                'culture_fit': feedback.get('culture_fit_rating'),
                'problem_solving': feedback.get('problem_solving_rating')
            },
            'recommendation': {
                'decision': recommendation['overall_recommendation'],
                'confidence': recommendation.get('confidence_score'),
                'justification': recommendation.get('justification'),
                'strengths': recommendation.get('key_strengths', []),
                'weaknesses': recommendation.get('key_weaknesses', []),
                'next_steps': recommendation.get('suggested_next_steps')
            },
            'interviewer_feedback': {
                'strengths': feedback.get('strengths'),
                'concerns': feedback.get('concerns'),
                'comments': feedback.get('qualitative_comments')
            }
        }


class EvaluationEngine:
    """
    Main engine for Phase 5: Evaluation and Recommendations
    """
    
    def __init__(self):
        self.analyzer = FeedbackAnalyzer()
        logger.info("🚀 Evaluation Engine initialized")
    
    def process_feedback(self, feedback: Dict, job_id: int, candidate_id: int,
                        save_to_db: bool = True) -> Dict:
        """
        Complete feedback processing pipeline
        
        Args:
            feedback: Feedback data
            job_id: Job ID
            candidate_id: Candidate ID
            save_to_db: Save to database
        
        Returns:
            Complete evaluation results
        """
        logger.info("=" * 60)
        logger.info("🚀 PHASE 5: EVALUATION & RECOMMENDATION PIPELINE")
        logger.info("=" * 60)
        
        # Get candidate and job data
        session = get_session()
        candidate = session.query(Candidate).filter_by(candidate_id=candidate_id).first()
        job = session.query(Job).filter_by(job_id=job_id).first()
        session.close()
        
        if not candidate or not job:
            raise ValueError("Invalid candidate_id or job_id")
        
        # Convert to dict
        candidate_dict = {
            'full_name': candidate.full_name,
            'email': candidate.email,
            'experience_years': candidate.experience_years,
            'current_position': candidate.current_position,
            'education': candidate.education,
            'skills': candidate.skills
        }
        
        job_dict = {
            'job_id': job.job_id,
            'title': job.title,
            'experience_level': job.experience_level,
            'department': job.department
        }
        
        # Analyze feedback
        recommendation = self.analyzer.analyze_feedback(feedback, candidate_dict, job_dict)
        
        # Save to database
        if save_to_db:
            rec_id = self.analyzer.save_recommendation_to_db(
                recommendation, job_id, candidate_id
            )
            recommendation['recommendation_id'] = rec_id
        
        # Generate report
        report = self.analyzer.generate_report(
            recommendation, candidate_dict, job_dict, feedback
        )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_json(report, f"reports/evaluation_report_{timestamp}.json")
        
        log_action(
            'evaluation',
            f"Completed evaluation for {candidate_dict['full_name']}",
            {'recommendation': recommendation['overall_recommendation']}
        )
        
        logger.info("=" * 60)
        logger.info("✓ PHASE 5 PIPELINE COMPLETED")
        logger.info("=" * 60)
        
        return {
            'recommendation': recommendation,
            'report': report
        }


def main():
    """Demo the evaluation system"""
    # Sample feedback
    feedback = {
        'technical_skills_rating': 9,
        'communication_skills_rating': 8,
        'culture_fit_rating': 9,
        'problem_solving_rating': 8,
        'strengths': 'Strong Python skills, excellent problem-solving, great communication',
        'concerns': 'Limited experience with distributed systems',
        'qualitative_comments': 'Very impressive candidate. Would be a great fit for the team.'
    }
    
    # Sample data
    candidate = {
        'full_name': 'Alice Johnson',
        'experience_years': 8,
        'current_position': 'Senior Software Engineer',
        'education': "Master's in Computer Science",
        'skills': ['Python', 'Django', 'PostgreSQL', 'AWS']
    }
    
    job = {
        'title': 'Senior Python Developer',
        'experience_level': 'senior',
        'department': 'Engineering'
    }
    
    analyzer = FeedbackAnalyzer()
    recommendation = analyzer.analyze_feedback(feedback, candidate, job)
    
    print("\n" + "=" * 60)
    print("AI RECOMMENDATION")
    print("=" * 60)
    print(f"Decision: {recommendation['overall_recommendation'].upper()}")
    print(f"Confidence: {recommendation.get('confidence_score')}%")
    print(f"\nJustification:")
    print(f"  {recommendation.get('justification')}")
    print(f"\nKey Strengths:")
    for s in recommendation.get('key_strengths', [])[:3]:
        print(f"  • {s}")
    print(f"\nNext Steps:")
    print(f"  {recommendation.get('suggested_next_steps')}")


if __name__ == '__main__':
    main()
