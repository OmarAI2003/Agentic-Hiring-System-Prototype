"""
HR Control Panel - Web Interface for Managing the Recruitment System
Allows HR to:
1. Input job description
2. Configure email settings
3. Set number of candidates
4. Choose test mode
5. Run the complete workflow
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from python.sourcing.main import CandidateSourcingEngine
from python.onboarding.email_automation import EmailAutomation
from python.utils.helpers import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

app = Flask(__name__)
app.secret_key = 'hr-system-secret-key-2025'
CORS(app)

# Get form URLs from environment (for deployment flexibility)
ONBOARDING_FORM_URL = os.getenv('ONBOARDING_FORM_URL', 'http://localhost:5000/onboarding')
MCQ_FORM_URL = os.getenv('MCQ_FORM_URL', 'http://localhost:5001/mcq')


def _extract_skills_from_description(description):
    """Extract technical skills from job description using keyword matching"""
    common_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express',
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQL', 'NoSQL',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD', 'Git',
        'REST', 'API', 'GraphQL', 'Microservices', 'Machine Learning', 'AI', 'Data Science',
        'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
        'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'SASS',
        'Linux', 'Unix', 'Bash', 'Shell', 'Agile', 'Scrum'
    ]
    
    # Find skills mentioned in description (case insensitive)
    description_lower = description.lower()
    found_skills = []
    
    for skill in common_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    # If no skills found, try to extract from job title
    if not found_skills:
        # Default based on common job titles
        if 'python' in description_lower or 'django' in description_lower or 'flask' in description_lower:
            found_skills = ['Python', 'Django', 'REST API']
        elif 'javascript' in description_lower or 'react' in description_lower or 'node' in description_lower:
            found_skills = ['JavaScript', 'React', 'Node.js']
        elif 'java' in description_lower and 'javascript' not in description_lower:
            found_skills = ['Java', 'Spring', 'SQL']
        elif 'data' in description_lower or 'machine learning' in description_lower:
            found_skills = ['Python', 'Machine Learning', 'Data Science']
        else:
            found_skills = ['Programming', 'Software Development', 'Problem Solving']
    
    # Limit to top 5 skills
    return found_skills[:5]


@app.route('/')
def index():
    """Main HR control panel page"""
    return render_template('hr_control_panel_simple.html')


@app.route('/schedule-interviews')
def schedule_interviews_page():
    """Interview scheduling page"""
    return render_template('schedule_interviews.html')


@app.route('/api/generate-job-description', methods=['POST'])
def generate_job_description():
    """Generate job description using AI from job title"""
    try:
        import os
        from groq import Groq
        
        data = request.json
        job_title = data.get('job_title', '').strip()
        
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        # Initialize Groq client
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            return jsonify({'error': 'GROQ_API_KEY not found in environment'}), 500
        
        client = Groq(api_key=api_key)
        
        # Generate job description using AI
        prompt = f"""Generate a comprehensive job description for the position: {job_title}

Include:
1. Brief company overview (generic tech company)
2. Job responsibilities (5-7 key duties)
3. Required qualifications and skills
4. Experience level required
5. What we offer

Make it professional and detailed. Format it as a clear, structured job posting."""

        logger.info(f"Generating job description for: {job_title}")
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Faster, uses fewer tokens
            messages=[
                {"role": "system", "content": "You are an expert HR professional and technical recruiter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        job_description = response.choices[0].message.content.strip()
        
        logger.info("✓ Job description generated successfully")
        
        return jsonify({
            'success': True,
            'job_description': job_description
        })
        
    except Exception as e:
        logger.error(f"Error generating job description: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/start-workflow', methods=['POST'])
def start_workflow():
    """
    Start the complete recruitment workflow
    
    Expected JSON:
    {
        "job_title": "Senior Python Developer",
        "job_description": "Build scalable web apps...",
        "sender_email": "omaragiez3@gmail.com",
        "sender_password": "rbwjtjjgjoqzgtkc",
        "num_candidates": 3,
        "test_email": "on152052@gmail.com"
    }
    """
    try:
        import json
        import os
        from datetime import datetime
        from python.questions.mcq_generator import MCQGenerator
        
        data = request.json
        
        # Extract parameters
        job_title = data.get('job_title', '').strip()
        job_description = data.get('job_description', '').strip()
        sender_email = data.get('sender_email', '').strip()
        sender_password = data.get('sender_password', '').strip()
        num_candidates = int(data.get('num_candidates', 3))
        test_email = data.get('test_email', 'on152052@gmail.com').strip()
        
        # Validate inputs
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        if not sender_email:
            return jsonify({'error': 'Sender email is required'}), 400
        
        if not sender_password:
            return jsonify({'error': 'Sender password is required'}), 400
        
        if len(sender_password) != 16:
            return jsonify({'error': 'Gmail App Password must be exactly 16 characters'}), 400
        
        # Update environment variables for email sending
        os.environ['GMAIL_EMAIL'] = sender_email
        os.environ['GMAIL_APP_PASSWORD'] = sender_password
        
        # Extract skills from job description using simple keyword extraction
        required_skills = _extract_skills_from_description(job_description)
        
        logger.info("=" * 80)
        logger.info("STARTING COMPLETE RECRUITMENT WORKFLOW")
        logger.info(f"Job: {job_title}")
        logger.info(f"Candidates: {num_candidates}")
        logger.info(f"Skills extracted: {required_skills}")
        logger.info("=" * 80)
        
        # Generate unique job ID
        job_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save job to file
        job_data = {
            'job_id': job_id,
            'title': job_title,
            'description': job_description,
            'required_skills': required_skills,
            'num_candidates': num_candidates,
            'created_at': datetime.now().isoformat()
        }
        
        jobs_dir = Path(__file__).parent / 'data' / 'jobs'
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_file = jobs_dir / f'job_{job_id}.json'
        
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        
        logger.info(f"✓ Job saved: {job_file}")
        
        # ========================================
        # PHASE 1: Source Candidates
        # ========================================
        logger.info("\n📋 PHASE 1: SOURCING CANDIDATES...")
        
        sourcing_engine = CandidateSourcingEngine(use_mock_data=True)
        
        candidates = sourcing_engine.source_candidates(
            job={'title': job_title, 'description': job_description, 'required_skills': required_skills},
            candidate_count=num_candidates,
            use_github=False
        )
        
        logger.info(f"✓ Sourced {len(candidates)} candidates")
        
        # ========================================
        # PHASE 2: Generate MCQ Questions
        # ========================================
        logger.info("\n❓ PHASE 2: GENERATING MCQ QUESTIONS...")
        
        mcq_generator = MCQGenerator()
        questions = mcq_generator.generate_mcq_questions(
            job_title=job_title,
            job_description=job_description,
            required_skills=required_skills,
            num_questions=5
        )
        
        # Save questions
        mcq_generator.save_questions(
            questions=questions,
            job_id=job_id,
            job_title=job_title
        )
        
        logger.info(f"✓ Generated {len(questions)} MCQ questions")
        
        # ========================================
        # PHASE 3: Send Onboarding Emails
        # ========================================
        logger.info("\n📧 PHASE 3: SENDING ONBOARDING EMAILS...")
        
        email_automation = EmailAutomation(test_mode=False)
        
        emails_sent = 0
        failed_emails = []
        
        for candidate in candidates:
            try:
                # Override email with test email for testing
                candidate_copy = candidate.copy()
                if test_email:
                    candidate_copy['email'] = test_email
                    logger.info(f"Using test email: {test_email}")
                
                job_dict = {
                    'job_id': job_id,
                    'title': job_title,
                    'description': job_description
                }
                
                # Let email_automation generate the form URL with all parameters
                success = email_automation.send_onboarding_email(
                    candidate=candidate_copy,
                    job=job_dict,
                    form_url=None  # Let it auto-generate with job_title and job_description
                )
                
                if success:
                    emails_sent += 1
                    logger.info(f"✓ Email sent to {candidate_copy.get('full_name', 'Unknown')}")
                else:
                    failed_emails.append(candidate_copy.get('email'))
                
            except Exception as email_error:
                logger.error(f"Failed to send email: {email_error}")
                failed_emails.append(candidate.get('email'))
        
        logger.info(f"✓ Sent {emails_sent}/{len(candidates)} onboarding emails")
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Workflow completed successfully!',
            'results': {
                'job_id': job_id,
                'job_title': job_title,
                'candidates_sourced': len(candidates),
                'mcq_questions_generated': len(questions),
                'emails_sent': emails_sent,
                'emails_failed': len(failed_emails),
                'test_email_used': test_email if test_email else None,
                'next_steps': [
                    f"Check {test_email if test_email else 'candidate emails'} for onboarding links",
                    "Candidates fill onboarding form → Auto-receives MCQ email",
                    "Candidates complete MCQ → Auto-receives feedback email"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule-interviews', methods=['POST'])
def schedule_interviews():
    """
    Schedule interviews for top candidates based on MCQ scores
    
    Expected JSON:
    {
        "job_id": "20251031_221530",
        "job_title": "Senior Python Developer",
        "top_n": 2
    }
    """
    try:
        from python.interview.interview_scheduler import InterviewScheduler
        
        data = request.json
        
        job_id = data.get('job_id', '').strip()
        job_title = data.get('job_title', '').strip()
        top_n = int(data.get('top_n', 2))
        
        # Validate inputs
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        logger.info(f"Scheduling interviews for job: {job_title} (ID: {job_id})")
        
        # Schedule interviews
        scheduler = InterviewScheduler()
        result = scheduler.schedule_interviews_for_job(job_id, job_title, top_n)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'results': {
                    'total_candidates': result['total_candidates'],
                    'selected_candidates': result['selected_candidates'],
                    'invitations_sent': result['invitations_sent'],
                    'top_candidates': result['top_candidates']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 400
        
    except Exception as e:
        logger.error(f"Error scheduling interviews: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _extract_job_title(description: str) -> str:
    """Extract job title from description using simple heuristics"""
    # Look for common patterns
    lines = description.strip().split('\n')
    first_line = lines[0].strip()
    
    # If first line is short and looks like a title
    if len(first_line) < 100 and any(word in first_line.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'designer']):
        return first_line
    
    # Default fallback
    return "Software Engineer"


def _extract_skills(description: str) -> list:
    """Extract required skills from job description"""
    # Common tech skills to look for
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'node', 'django', 'flask',
        'aws', 'docker', 'kubernetes', 'postgresql', 'mongodb', 'redis',
        'git', 'ci/cd', 'agile', 'scrum', 'sql', 'nosql', 'rest', 'api',
        'microservices', 'cloud', 'linux', 'typescript', 'vue', 'angular'
    ]
    
    description_lower = description.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in description_lower:
            found_skills.append(skill)
    
    return found_skills[:10]  # Return top 10


def _extract_experience_level(description: str) -> str:
    """Determine experience level from description"""
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['senior', 'lead', 'principal', 'staff']):
        return 'senior'
    elif any(word in description_lower for word in ['junior', 'entry', 'graduate', 'intern']):
        return 'entry'
    else:
        return 'mid'


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 3000))
    
    print("\n" + "=" * 80)
    print("HR CONTROL PANEL STARTING")
    print("=" * 80)
    print(f"\nAccess the control panel at: http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80 + "\n")
    
    # Use debug mode only in local development, not in production
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
