"""
MCQ Question Generator using Groq AI
Generates technical multiple-choice questions based on job description
"""
import os
import json
from typing import List, Dict
from groq import Groq
from python.utils.helpers import get_logger

logger = get_logger(__name__)


class MCQGenerator:
    """Generate MCQ questions using Groq AI"""
    
    def __init__(self):
        """Initialize MCQ generator with Groq API"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_mcq_questions(
        self, 
        job_title: str, 
        job_description: str, 
        required_skills: List[str],
        num_questions: int = 5
    ) -> List[Dict]:
        """
        Generate MCQ questions for a job position
        
        Args:
            job_title: Job title
            job_description: Full job description
            required_skills: List of required skills
            num_questions: Number of questions to generate (default: 5)
            
        Returns:
            List of MCQ questions with answers
        """
        logger.info(f"Generating {num_questions} MCQ questions for: {job_title}")
        
        prompt = f"""You are an expert technical recruiter. Generate EXACTLY {num_questions} multiple-choice questions to assess candidates for this position:

Job Title: {job_title}
Required Skills: {', '.join(required_skills)}

Job Description:
{job_description}

Generate {num_questions} technical MCQ questions that test:
1. Technical knowledge of required skills
2. Problem-solving abilities
3. Best practices understanding
4. Real-world application scenarios

For EACH question, provide:
- A clear, specific question
- 4 answer options (A, B, C, D)
- The correct answer (A, B, C, or D)
- A brief explanation of why that answer is correct

Format your response as valid JSON with this EXACT structure:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}

IMPORTANT: Return ONLY valid JSON, no other text. Generate exactly {num_questions} questions."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer. Generate high-quality MCQ questions in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract and parse response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            questions_data = json.loads(content)
            questions = questions_data.get('questions', [])
            
            if len(questions) != num_questions:
                logger.warning(f"Expected {num_questions} questions, got {len(questions)}")
            
            logger.info(f"Successfully generated {len(questions)} MCQ questions")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content: {content}")
            raise
        except Exception as e:
            logger.error(f"Error generating MCQ questions: {e}")
            raise
    
    def save_questions(
        self, 
        questions: List[Dict], 
        job_id: int,
        job_title: str,
        output_dir: str = "data/questions"
    ) -> str:
        """
        Save generated questions to file
        
        Args:
            questions: List of MCQ questions
            job_id: Job ID
            job_title: Job title for folder organization
            output_dir: Directory to save questions
            
        Returns:
            Path to saved file
        """
        # Create directory structure: data/questions/{job_title}/{job_id}_questions.json
        job_title_clean = job_title.replace('/', '_').replace('\\', '_').replace('*', '').strip()
        job_dir = os.path.join(output_dir, job_title_clean)
        os.makedirs(job_dir, exist_ok=True)
        
        filename = f"job_{job_id}_questions.json"
        filepath = os.path.join(job_dir, filename)
        
        data = {
            "job_id": job_id,
            "job_title": job_title,
            "num_questions": len(questions),
            "questions": questions
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(questions)} questions to: {filepath}")
        return filepath


if __name__ == "__main__":
    # Test the generator
    from dotenv import load_dotenv
    load_dotenv()
    
    generator = MCQGenerator()
    
    test_job = {
        "title": "Senior Python Developer",
        "description": "Build scalable web applications using Python, Django, and AWS",
        "skills": ["Python", "Django", "AWS", "Docker", "PostgreSQL"]
    }
    
    questions = generator.generate_mcq_questions(
        job_title=test_job["title"],
        job_description=test_job["description"],
        required_skills=test_job["skills"],
        num_questions=5
    )
    
    filepath = generator.save_questions(
        questions=questions,
        job_id=999,
        job_title=test_job["title"]
    )
    
    print(f"\n✅ Generated {len(questions)} questions")
    print(f"📁 Saved to: {filepath}")
