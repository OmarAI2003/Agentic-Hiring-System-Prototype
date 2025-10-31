"""
Phase 3: Technical Interview Question Generator
Uses AI to generate customized, role-specific interview questions
"""
import json
from typing import Dict, List
from datetime import datetime
from python.utils.helpers import get_logger, save_json, log_decision, log_action
from python.utils.groq_client import GroqLLM
from database.models import InterviewQuestion, get_session

logger = get_logger(__name__)


class InterviewQuestionGenerator:
    """
    Generates intelligent, customized interview questions using AI
    Demonstrates agentic behavior by analyzing job and candidate context
    """
    
    QUESTION_CATEGORIES = [
        'technical_knowledge',
        'problem_solving',
        'coding',
        'system_design',
        'behavioral',
        'situational'
    ]
    
    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']
    
    def __init__(self):
        self.llm = GroqLLM()
        logger.info("🎯 Interview Question Generator initialized")
    
    def generate_question_set(self, job: Dict, candidate: Dict = None, 
                             question_count: int = 10) -> List[Dict]:
        """
        Generate a complete set of interview questions
        
        Args:
            job: Job posting data
            candidate: Candidate data (for personalization)
            question_count: Number of questions to generate
        
        Returns:
            List of question dictionaries
        """
        logger.info(f"🤖 Generating {question_count} interview questions...")
        logger.info(f"   Job: {job.get('title')}")
        if candidate:
            logger.info(f"   Candidate: {candidate.get('full_name')}")
        
        # Autonomous decision: determine question distribution
        distribution = self._decide_question_distribution(job, candidate)
        
        log_decision(
            'interview_prep',
            f"AI determined question distribution for {job.get('title')}",
            distribution
        )
        
        questions = []
        
        # Generate questions by category
        for category, count in distribution.items():
            if count > 0:
                category_questions = self._generate_category_questions(
                    category, count, job, candidate
                )
                questions.extend(category_questions)
        
        # Ensure we have the right number
        questions = questions[:question_count]
        
        log_action(
            'interview_prep',
            f"Generated {len(questions)} interview questions",
            {'job_title': job.get('title'), 'distribution': distribution}
        )
        
        logger.info(f"✓ Generated {len(questions)} questions across {len(distribution)} categories")
        return questions
    
    def _decide_question_distribution(self, job: Dict, candidate: Dict = None) -> Dict[str, int]:
        """
        AGENTIC DECISION: Determine optimal question category distribution
        """
        experience_level = job.get('experience_level', 'mid').lower()
        job_title = job.get('title', '').lower()
        required_skills = job.get('required_skills', [])
        
        # Build context for AI decision
        context = {
            'job_title': job.get('title'),
            'experience_level': experience_level,
            'key_skills': required_skills[:5],
            'department': job.get('department'),
            'total_questions': 10
        }
        
        if candidate:
            context['candidate_experience'] = candidate.get('experience_years')
            context['candidate_position'] = candidate.get('current_position')
        
        prompt = f"""You are designing an interview question set for a technical interview.

Job Context:
- Position: {context['job_title']}
- Experience Level: {context['experience_level']}
- Key Skills: {', '.join(context['key_skills'])}
- Department: {context.get('department', 'Engineering')}

Determine the optimal distribution of 10 interview questions across these categories:
- technical_knowledge: Questions about specific technologies/concepts
- problem_solving: Algorithmic and logical thinking questions
- coding: Hands-on coding challenges
- system_design: Architecture and design questions
- behavioral: Past experience and soft skills
- situational: Hypothetical scenario questions

Consider:
- Entry level: Focus more on fundamentals and learning ability
- Mid level: Balance technical depth with problem-solving
- Senior level: Emphasize system design and leadership

Respond ONLY with valid JSON:
{{
    "technical_knowledge": 3,
    "problem_solving": 2,
    "coding": 2,
    "system_design": 1,
    "behavioral": 1,
    "situational": 1,
    "reasoning": "Brief explanation"
}}
"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.3)
            distribution = json.loads(response)
            
            # Validate and ensure it sums to 10
            total = sum(v for k, v in distribution.items() if k in self.QUESTION_CATEGORIES)
            
            if total == 10:
                return {k: v for k, v in distribution.items() if k in self.QUESTION_CATEGORIES}
        except Exception as e:
            logger.warning(f"AI distribution failed, using rule-based: {str(e)}")
        
        # Fallback: rule-based distribution
        return self._rule_based_distribution(experience_level, job_title)
    
    def _rule_based_distribution(self, experience_level: str, job_title: str) -> Dict[str, int]:
        """Fallback rule-based question distribution"""
        if experience_level == 'senior':
            return {
                'technical_knowledge': 2,
                'problem_solving': 2,
                'coding': 1,
                'system_design': 3,
                'behavioral': 1,
                'situational': 1
            }
        elif experience_level == 'entry':
            return {
                'technical_knowledge': 4,
                'problem_solving': 2,
                'coding': 2,
                'system_design': 0,
                'behavioral': 1,
                'situational': 1
            }
        else:  # mid
            return {
                'technical_knowledge': 3,
                'problem_solving': 2,
                'coding': 2,
                'system_design': 1,
                'behavioral': 1,
                'situational': 1
            }
    
    def _generate_category_questions(self, category: str, count: int, 
                                    job: Dict, candidate: Dict = None) -> List[Dict]:
        """Generate questions for a specific category"""
        logger.info(f"   Generating {count} {category} questions...")
        
        questions = []
        
        for i in range(count):
            question = self._generate_single_question(category, job, candidate, i)
            if question:
                questions.append(question)
        
        return questions
    
    def _generate_single_question(self, category: str, job: Dict, 
                                  candidate: Dict = None, index: int = 0) -> Dict:
        """Generate a single interview question using AI"""
        # Determine difficulty
        difficulty = self._determine_difficulty(job.get('experience_level'), category)
        
        # Build context
        skills = ', '.join(job.get('required_skills', [])[:5])
        experience_level = job.get('experience_level', 'mid')
        
        prompt = f"""Generate 1 {category} interview question for a {experience_level} level {job.get('title')} position.

Required Skills: {skills}
Difficulty: {difficulty}
Category: {category}

Requirements:
- Question should be specific and relevant to the role
- Appropriate for {experience_level} level
- {difficulty} difficulty
- Include expected answer approach
- Include evaluation criteria

Respond in JSON format:
{{
    "question": "The interview question here",
    "expected_answer": "What a good answer should cover",
    "evaluation_criteria": "How to evaluate the response",
    "follow_up_questions": ["Optional follow-up 1", "Optional follow-up 2"]
}}
"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.7)
            question_data = json.loads(response)
            
            return {
                'question_text': question_data.get('question', ''),
                'category': category,
                'difficulty': difficulty,
                'expected_answer': question_data.get('expected_answer', ''),
                'evaluation_criteria': question_data.get('evaluation_criteria', ''),
                'follow_up_questions': question_data.get('follow_up_questions', []),
                'generated_by': 'ai'
            }
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            # Return a fallback question
            return self._fallback_question(category, difficulty, job)
    
    def _determine_difficulty(self, experience_level: str, category: str) -> str:
        """Determine question difficulty based on experience and category"""
        if experience_level == 'senior':
            # Senior roles: mostly medium and hard
            return 'hard' if category in ['system_design', 'problem_solving'] else 'medium'
        elif experience_level == 'entry':
            # Entry roles: mostly easy and medium
            return 'easy' if category in ['technical_knowledge', 'behavioral'] else 'medium'
        else:
            # Mid level: balanced
            return 'medium'
    
    def _fallback_question(self, category: str, difficulty: str, job: Dict) -> Dict:
        """Generate a fallback question when AI fails"""
        fallback_questions = {
            'technical_knowledge': {
                'question_text': f"Explain your experience with {job.get('required_skills', ['relevant technologies'])[0]}",
                'expected_answer': "Should demonstrate understanding and practical experience",
                'evaluation_criteria': "Depth of knowledge, practical examples, problem-solving approach"
            },
            'problem_solving': {
                'question_text': "Describe a complex technical problem you solved recently",
                'expected_answer': "Should include problem analysis, solution approach, and outcome",
                'evaluation_criteria': "Problem complexity, solution creativity, communication clarity"
            },
            'behavioral': {
                'question_text': "Tell me about a time you worked effectively in a team",
                'expected_answer': "Should demonstrate teamwork, communication, and collaboration",
                'evaluation_criteria': "Collaboration skills, conflict resolution, contribution to team success"
            }
        }
        
        template = fallback_questions.get(category, fallback_questions['technical_knowledge'])
        
        return {
            'question_text': template['question_text'],
            'category': category,
            'difficulty': difficulty,
            'expected_answer': template['expected_answer'],
            'evaluation_criteria': template['evaluation_criteria'],
            'generated_by': 'fallback'
        }
    
    def save_questions_to_db(self, questions: List[Dict], job_id: int, 
                            candidate_id: int = None) -> List[int]:
        """
        Save generated questions to database
        
        Args:
            questions: List of question dictionaries
            job_id: Job ID
            candidate_id: Candidate ID (optional, for personalized questions)
        
        Returns:
            List of question IDs
        """
        logger.info(f"💾 Saving {len(questions)} questions to database...")
        
        session = get_session()
        question_ids = []
        
        try:
            for q in questions:
                question = InterviewQuestion(
                    job_id=job_id,
                    candidate_id=candidate_id,
                    question_text=q['question_text'],
                    category=q['category'],
                    difficulty=q['difficulty'],
                    expected_answer=q['expected_answer'],
                    evaluation_criteria=q['evaluation_criteria'],
                    generated_by=q.get('generated_by', 'ai')
                )
                session.add(question)
                session.flush()
                question_ids.append(question.question_id)
            
            session.commit()
            logger.info(f"✓ Saved {len(questions)} questions to database")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving questions: {str(e)}")
            raise
        finally:
            session.close()
        
        return question_ids
    
    def generate_and_save(self, job: Dict, candidate: Dict = None, 
                         save_to_db: bool = True) -> Dict:
        """
        Complete workflow: generate questions and optionally save
        
        Returns:
            Dictionary with questions and metadata
        """
        questions = self.generate_question_set(job, candidate)
        
        if save_to_db and 'job_id' in job:
            question_ids = self.save_questions_to_db(
                questions, 
                job['job_id'],
                candidate.get('candidate_id') if candidate else None
            )
        else:
            question_ids = []
        
        # Save to JSON for n8n
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_data = {
            'job_title': job.get('title'),
            'job_id': job.get('job_id'),
            'candidate_name': candidate.get('full_name') if candidate else None,
            'generated_at': timestamp,
            'questions': questions
        }
        save_json(output_data, f"data/questions/questions_{timestamp}.json")
        
        return {
            'questions': questions,
            'question_ids': question_ids,
            'count': len(questions)
        }


def main():
    """Demo the question generator"""
    # Sample job
    job = {
        'job_id': 1,
        'title': 'Senior Python Developer',
        'experience_level': 'senior',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
        'department': 'Engineering'
    }
    
    generator = InterviewQuestionGenerator()
    result = generator.generate_and_save(job, save_to_db=False)
    
    print("\n" + "=" * 60)
    print("GENERATED INTERVIEW QUESTIONS")
    print("=" * 60)
    
    for i, q in enumerate(result['questions'], 1):
        print(f"\n{i}. [{q['category'].upper()}] - {q['difficulty']}")
        print(f"   Q: {q['question_text'][:100]}...")
        print(f"   Expected: {q['expected_answer'][:80]}...")


if __name__ == '__main__':
    main()
