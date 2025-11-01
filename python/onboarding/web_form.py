"""
Web-based onboarding form using Flask
FREE alternative to Google Forms
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')

# Data directory for form responses
FORMS_DIR = Path(__file__).parent.parent.parent / 'data' / 'forms'
FORMS_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Landing page"""
    return render_template('form_landing.html')


@app.route('/onboarding')
def onboarding_form():
    """
    Onboarding form page
    Query params: candidate_email, job_id, job_title
    Job description is loaded from the job file, not from URL
    """
    from urllib.parse import unquote
    import json
    import os
    
    candidate_email = request.args.get('candidate_email', '')
    job_id = request.args.get('job_id', '')
    job_title = unquote(request.args.get('job_title', ''))
    
    # Load job description from job file (not from URL)
    job_description = ""
    try:
        job_file = f"data/jobs/job_{job_id}.json"
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                job_data = json.load(f)
                job_description = job_data.get('description', '')
                logger.info(f"Loaded job description from {job_file}")
        else:
            logger.warning(f"Job file not found: {job_file}")
    except Exception as e:
        logger.error(f"Error loading job file: {str(e)}")
    
    logger.info(f"Onboarding form accessed - Email: {candidate_email}, Job ID: {job_id}, Job Title: {job_title}")
    
    return render_template('onboarding_form.html', 
                         candidate_email=candidate_email,
                         job_id=job_id,
                         job_title=job_title,
                         job_description=job_description)


@app.route('/submit', methods=['POST'])
def submit_form():
    """
    Handle form submission and automatically send MCQ assessment
    """
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        logger.info(f"Form data received: {form_data}")
        
        # Add metadata
        submission = {
            'submission_time': datetime.now().isoformat(),
            'candidate_email': form_data.get('email', 'unknown'),
            'job_id': form_data.get('job_id', 'unknown'),
            'form_data': form_data
        }
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_safe = submission['candidate_email'].replace('@', '_at_').replace('.', '_')
        filename = f"response_{timestamp}_{email_safe}.json"
        
        # Save to file
        filepath = FORMS_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(submission, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Form submission saved: {filename}")
        
        # AUTOMATIC: Generate MCQ questions and send email immediately
        try:
            from python.questions.mcq_email_automation import MCQEmailSender, get_mcq_form_url
            from python.questions.mcq_generator import MCQGenerator
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            
            # Load job details to get job title and description
            job_id = form_data.get('job_id')
            job_title = form_data.get('job_title', 'Position')
            job_description = form_data.get('job_description', '')  # Get from form
            
            logger.info(f"Processing MCQ - Title: {job_title}, Description length: {len(job_description)}")
            
            # Generate MCQ questions using actual job description
            mcq_generator = MCQGenerator()
            questions = mcq_generator.generate_mcq_questions(
                job_title=job_title,
                job_description=job_description if job_description else f"Technical position for {job_title}",
                required_skills=[],
                num_questions=5
            )
            
            # Save questions
            mcq_generator.save_questions(
                questions=questions,
                job_id=job_id,
                job_title=job_title
            )
            
            logger.info(f"Generated {len(questions)} MCQ questions for {job_title}")
            
            # Send MCQ email
            email_sender = MCQEmailSender(
                api_key=os.getenv('SENDGRID_API_KEY'),
                sender_email=os.getenv('SENDER_EMAIL', 'noreply@recruitment.com')
            )
            
            mcq_url = get_mcq_form_url(
                candidate_email=submission['candidate_email'],
                job_id=job_id,
                job_title=job_title,
                job_description=job_description
            )
            
            email_sender.send_mcq_email(
                candidate_email=submission['candidate_email'],
                candidate_name=form_data.get('full_name', 'Candidate'),
                job_title=job_title,
                job_id=job_id,
                mcq_url=mcq_url
            )
            
            logger.info(f"MCQ assessment email sent automatically to: {submission['candidate_email']}")
            
        except Exception as mcq_error:
            logger.error(f"Failed to send MCQ email automatically: {mcq_error}")
            # Don't fail the form submission if email fails
        
        # Return success page
        return render_template('form_success.html', 
                             candidate_name=form_data.get('full_name', 'Candidate'))
        
    except Exception as e:
        logger.error(f"Error saving form submission: {e}")
        return render_template('form_error.html', error=str(e)), 500


@app.route('/api/responses')
def get_responses():
    """
    API endpoint to retrieve form responses
    Query params: email, job_id
    """
    try:
        email = request.args.get('email')
        job_id = request.args.get('job_id')
        
        responses = []
        for file in FORMS_DIR.glob('response_*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Filter by email or job_id if provided
                if email and data.get('candidate_email') != email:
                    continue
                if job_id and data.get('job_id') != job_id:
                    continue
                    
                responses.append(data)
        
        return jsonify({
            'success': True,
            'count': len(responses),
            'responses': responses
        })
        
    except Exception as e:
        logger.error(f"Error retrieving responses: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'onboarding-form'})


def run_server(host='127.0.0.1', port=5000, debug=False):
    """
    Run the Flask server
    
    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to bind to (default: 5000)
        debug: Enable debug mode
    """
    logger.info(f"Starting onboarding form server on http://{host}:{port}")
    logger.info(f"Form URL: http://{host}:{port}/onboarding")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)
