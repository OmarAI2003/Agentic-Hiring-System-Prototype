"""
Web-based MCQ form for candidates
Displays questions and collects answers
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')

# Data directories
QUESTIONS_DIR = Path(__file__).parent.parent.parent / 'data' / 'questions'
ANSWERS_DIR = Path(__file__).parent.parent.parent / 'data' / 'answers'
ANSWERS_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/mcq')
def mcq_form():
    """
    MCQ form page
    Query params: candidate_email, job_id, job_title
    """
    candidate_email = request.args.get('candidate_email', '')
    job_id = request.args.get('job_id', '')
    job_title = request.args.get('job_title', '')
    
    logger.info(f"MCQ form accessed for: {candidate_email}, job: {job_id}")
    
    # Load questions for this job
    try:
        job_title_clean = job_title.replace('/', '_').replace('\\', '_').replace('*', '').strip()
        questions_file = QUESTIONS_DIR / job_title_clean / f"job_{job_id}_questions.json"
        
        # If questions don't exist, generate them on-demand
        if not questions_file.exists():
            logger.warning(f"Questions file not found: {questions_file}")
            logger.info("Generating questions on-demand...")
            
            try:
                from python.questions.mcq_generator import MCQGenerator
                import os
                
                # Load job details to generate questions
                jobs_dir = Path(__file__).parent.parent.parent / 'data' / 'jobs'
                job_file = jobs_dir / f'job_{job_id}.json'
                
                if not job_file.exists():
                    # Try alternative pattern
                    job_files = list(jobs_dir.glob(f'*{job_id}*.json'))
                    if job_files:
                        job_file = job_files[0]
                    else:
                        return render_template('form_error.html', 
                                             error="Job information not found. Please contact HR."), 404
                
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                # Generate questions
                mcq_generator = MCQGenerator()
                questions = mcq_generator.generate_mcq_questions(
                    job_title=job_title,
                    job_description=job_data.get('description', ''),
                    required_skills=job_data.get('required_skills', []),
                    num_questions=5
                )
                
                # Save questions
                mcq_generator.save_questions(
                    questions=questions,
                    job_id=job_id,
                    job_title=job_title
                )
                
                logger.info(f"Generated {len(questions)} questions on-demand")
                
                # Reload the file
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
                    
            except Exception as gen_error:
                logger.error(f"Failed to generate questions on-demand: {gen_error}")
                return render_template('form_error.html', 
                                     error="Unable to load assessment questions. Please try again later."), 500
        else:
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        
        return render_template('mcq_form.html',
                             candidate_email=candidate_email,
                             job_id=job_id,
                             job_title=job_title,
                             questions=questions_data['questions'])
        
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return render_template('form_error.html', error=str(e)), 500


@app.route('/submit_mcq', methods=['POST'])
def submit_mcq():
    """
    Handle MCQ form submission and provide instant feedback
    """
    try:
        # Get form data
        data = request.get_json()
        candidate_email = data.get('candidate_email')
        job_id = data.get('job_id')
        job_title = data.get('job_title')
        answers = data.get('answers', {})
        
        logger.info(f"MCQ submission from: {candidate_email} for job: {job_id}")
        
        # Load correct answers
        job_title_clean = job_title.replace('/', '_').replace('\\', '_').replace('*', '').strip()
        questions_file = QUESTIONS_DIR / job_title_clean / f"job_{job_id}_questions.json"
        
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        # Score the answers
        total_questions = len(questions_data['questions'])
        correct_count = 0
        results = []
        
        for i, question in enumerate(questions_data['questions'], 1):
            question_id = str(i)
            user_answer = answers.get(question_id, '')
            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            results.append({
                'question_number': i,
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
        
        score = (correct_count / total_questions) * 100
        
        # Save submission
        submission = {
            'submission_time': datetime.now().isoformat(),
            'candidate_email': candidate_email,
            'job_id': job_id,
            'job_title': job_title,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'score_percentage': score,
            'answers': answers,
            'detailed_results': results
        }
        
        # Create directory structure: data/answers/{job_title}/
        job_answers_dir = ANSWERS_DIR / job_title_clean
        job_answers_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_safe = candidate_email.replace('@', '_at_').replace('.', '_')
        filename = f"answers_{timestamp}_{email_safe}.json"
        filepath = job_answers_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(submission, f, indent=2, ensure_ascii=False)
        
        logger.info(f"MCQ submission saved: {filename} - Score: {score:.1f}%")
        
        # AUTOMATIC: Send feedback email immediately
        try:
            from python.questions.mcq_email_automation import MCQEmailSender, send_feedback_email
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            
            email_sender = MCQEmailSender(
                api_key=os.getenv('SENDGRID_API_KEY'),
                sender_email=os.getenv('SENDER_EMAIL', 'noreply@recruitment.com')
            )
            
            # Send feedback email with results
            send_feedback_email(
                email_sender=email_sender,
                candidate_email=candidate_email,
                candidate_name=candidate_email.split('@')[0].title(),
                job_title=job_title,
                score=score,
                correct_count=correct_count,
                total_questions=total_questions,
                results=results
            )
            
            logger.info(f"Feedback email sent to: {candidate_email}")
            
        except Exception as email_error:
            logger.error(f"Failed to send feedback email: {email_error}")
            # Don't fail the submission if email fails
        
        # ========================================
        # AUTOMATIC INTERVIEW SCHEDULING
        # ========================================
        try:
            from python.interview.interview_scheduler import InterviewScheduler
            
            logger.info("Checking if interview scheduling should be triggered...")
            
            # Get total number of candidates for this job
            jobs_dir = Path(__file__).parent.parent.parent / 'data' / 'jobs'
            
            # Try to find job file by job_id
            job_file = jobs_dir / f'job_{job_id}.json'
            
            if not job_file.exists():
                # Try alternative pattern
                job_files = list(jobs_dir.glob(f'*{job_id}*.json'))
                if job_files:
                    job_file = job_files[0]
                else:
                    logger.warning(f"Job file not found for job_id: {job_id}")
                    job_file = None
            
            if job_file and job_file.exists():
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                    total_candidates = job_data.get('num_candidates', 0)
                    
                    logger.info(f"Total candidates for job: {total_candidates}")
                    
                    # Count how many candidates have completed MCQ
                    answers_dir = Path(__file__).parent.parent.parent / 'data' / 'answers' / job_title
                    if answers_dir.exists():
                        completed_count = len(list(answers_dir.glob('answers_*.json')))
                        logger.info(f"Candidates completed MCQ: {completed_count}/{total_candidates}")
                        
                        # Trigger interview scheduling if:
                        # 1. All candidates completed (for >3 candidates)
                        # 2. Immediately if candidates <= 3
                        should_schedule = False
                        top_n = 3  # Default: top 3 candidates
                        
                        if total_candidates <= 3:
                            # Send to all candidates immediately
                            should_schedule = True
                            top_n = total_candidates
                            logger.info(f"Total candidates ({total_candidates}) <= 3, scheduling interviews for all")
                        elif completed_count >= total_candidates:
                            # All candidates completed, select top 3
                            should_schedule = True
                            top_n = 3
                            logger.info(f"All {total_candidates} candidates completed, selecting top 3")
                        
                        if should_schedule:
                            logger.info("=" * 80)
                            logger.info("TRIGGERING AUTOMATIC INTERVIEW SCHEDULING")
                            logger.info("=" * 80)
                            
                            scheduler = InterviewScheduler()
                            result = scheduler.schedule_interviews_for_job(job_id, job_title, top_n)
                            
                            if result['success']:
                                logger.info(f"✓ Interview invitations sent to {result['invitations_sent']} candidates")
                            else:
                                logger.warning(f"Interview scheduling failed: {result.get('message')}")
                        else:
                            logger.info(f"Waiting for more candidates to complete ({completed_count}/{total_candidates})")
                    else:
                        logger.warning(f"Answers directory not found: {answers_dir}")
            else:
                logger.warning(f"Could not find job file for job_id: {job_id}")
                
        except Exception as scheduling_error:
            logger.error(f"Error in automatic interview scheduling: {scheduling_error}")
            import traceback
            traceback.print_exc()
            # Don't fail the submission if scheduling fails
        
        # Return results
        return jsonify({
            'success': True,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing MCQ submission: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/answers/<job_title>')
def get_answers(job_title):
    """
    API endpoint to retrieve all answers for a job position
    """
    try:
        job_title_clean = job_title.replace('/', '_').replace('\\', '_').replace('*', '').strip()
        job_answers_dir = ANSWERS_DIR / job_title_clean
        
        if not job_answers_dir.exists():
            return jsonify({'answers': []})
        
        answers = []
        for file in job_answers_dir.glob('answers_*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                answers.append(data)
        
        # Sort by score (highest first)
        answers.sort(key=lambda x: x.get('score_percentage', 0), reverse=True)
        
        return jsonify({'answers': answers})
        
    except Exception as e:
        logger.error(f"Error retrieving answers: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'mcq-form'})


if __name__ == '__main__':
    print("=" * 60)
    print("MCQ FORM SERVER")
    print("=" * 60)
    print("Server starting on: http://127.0.0.1:5001")
    print("MCQ Form URL: http://127.0.0.1:5001/mcq")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
