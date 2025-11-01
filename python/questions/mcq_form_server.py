"""
Web-based MCQ form for candidates - SIMPLIFIED
Generates 10 questions on-the-fly based on job title only
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import logging
from pathlib import Path
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')

# Data directory for answers only
ANSWERS_DIR = Path(__file__).parent.parent.parent / 'data' / 'answers'
ANSWERS_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/mcq')
def mcq_form():
    """
    MCQ form page - generates 10 questions on-the-fly based on job description
    Query params: candidate_email, job_id, job_title, job_description
    """
    from urllib.parse import unquote
    
    candidate_email = request.args.get('candidate_email', '')
    job_id = request.args.get('job_id', '')
    job_title = unquote(request.args.get('job_title', 'Software Developer'))
    job_description = unquote(request.args.get('job_description', ''))
    
    logger.info(f"MCQ accessed - Email: {candidate_email}, Job: {job_title}")
    logger.info(f"Job description length: {len(job_description)}")
    
    try:
        # Generate 10 questions using AI based on ACTUAL job description
        from python.questions.mcq_generator import MCQGenerator
        
        mcq_generator = MCQGenerator()
        questions = mcq_generator.generate_mcq_questions(
            job_title=job_title,
            job_description=job_description if job_description else f"Technical assessment for {job_title}",
            required_skills=[],
            num_questions=10
        )
        
        logger.info(f"Generated {len(questions)} questions for {job_title}")
        
        return render_template('mcq_form.html',
                             candidate_email=candidate_email,
                             job_id=job_id,
                             job_title=job_title,
                             job_description=job_description,
                             questions=questions)
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return render_template('form_error.html', error=str(e)), 500


@app.route('/submit_mcq', methods=['POST'])
def submit_mcq():
    """
    Handle MCQ submission - regenerate questions with ACTUAL job description
    """
    try:
        data = request.get_json()
        candidate_email = data.get('candidate_email')
        job_id = data.get('job_id')
        job_title = data.get('job_title', 'Software Developer')
        job_description = data.get('job_description', '')
        answers = data.get('answers', {})
        
        logger.info(f"MCQ submission from: {candidate_email}")
        logger.info(f"Using job description length: {len(job_description)}")
        
        # Regenerate questions with ACTUAL job description to check answers
        from python.questions.mcq_generator import MCQGenerator
        
        mcq_generator = MCQGenerator()
        questions = mcq_generator.generate_mcq_questions(
            job_title=job_title,
            job_description=job_description if job_description else f"Technical assessment for {job_title}",
            required_skills=[],
            num_questions=10
        )
        
        # Score answers
        total_questions = len(questions)
        correct_count = 0
        results = []
        
        for i, question in enumerate(questions, 1):
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
        job_title_clean = job_title.replace('/', '_').replace('\\', '_').replace('*', '').strip()
        job_answers_dir = ANSWERS_DIR / job_title_clean
        job_answers_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_safe = candidate_email.replace('@', '_at_').replace('.', '_')
        filename = f"answers_{timestamp}_{email_safe}.json"
        
        submission = {
            'submission_time': datetime.now().isoformat(),
            'candidate_email': candidate_email,
            'job_id': job_id,
            'job_title': job_title,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'score_percentage': score
        }
        
        with open(job_answers_dir / filename, 'w') as f:
            json.dump(submission, f, indent=2)
        
        logger.info(f"Saved submission: {filename} - Score: {score:.1f}%")
        
        # Send feedback email
        try:
            from python.questions.mcq_email_automation import MCQEmailSender, send_feedback_email
            from dotenv import load_dotenv
            
            load_dotenv()
            
            email_sender = MCQEmailSender(
                api_key=os.getenv('SENDGRID_API_KEY'),
                sender_email=os.getenv('SENDER_EMAIL', 'noreply@recruitment.com')
            )
            
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
            
            logger.info(f"Feedback email sent to {candidate_email}")
        except Exception as e:
            logger.error(f"Email error: {e}")
        
        return jsonify({
            'success': True,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
