"""
Interview Scheduler - Selects top candidates and sends interview invitations
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InterviewScheduler:
    """Handles interview scheduling for top candidates"""
    
    def __init__(self):
        self.sender_email = os.environ.get('GMAIL_EMAIL', 'omaragiez3@gmail.com')
        self.sender_password = os.environ.get('GMAIL_APP_PASSWORD', 'rbwjtjjgjoqzgtkc')
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
    
    def get_candidates_by_job(self, job_id: str, job_title: str):
        """
        Get all candidates who completed MCQ for a specific job
        Returns list of candidates with their scores
        """
        answers_dir = self.data_dir / 'answers' / job_title
        
        if not answers_dir.exists():
            logger.warning(f"No answers found for job: {job_title}")
            return []
        
        candidates = []
        
        # Read all answer files
        for answer_file in answers_dir.glob('answers_*.json'):
            try:
                with open(answer_file, 'r', encoding='utf-8') as f:
                    answer_data = json.load(f)
                
                # Check if this answer is for the correct job
                if answer_data.get('job_id') == job_id:
                    candidates.append({
                        'email': answer_data.get('candidate_email'),
                        'name': answer_data.get('candidate_name', 'Candidate'),
                        'score': answer_data.get('score', 0),
                        'correct_answers': answer_data.get('correct_count', 0),
                        'total_questions': answer_data.get('total_questions', 0),
                        'submitted_at': answer_data.get('submitted_at'),
                        'file_path': str(answer_file)
                    })
            except Exception as e:
                logger.error(f"Error reading answer file {answer_file}: {e}")
                continue
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Found {len(candidates)} candidates for job {job_id}")
        return candidates
    
    def select_top_candidates(self, candidates: list, top_n: int = 2):
        """
        Select top N candidates based on score
        If total candidates <= top_n, return all
        """
        if len(candidates) <= top_n:
            logger.info(f"Total candidates ({len(candidates)}) <= {top_n}, selecting all")
            return candidates
        
        top_candidates = candidates[:top_n]
        logger.info(f"Selected top {top_n} candidates from {len(candidates)} total")
        return top_candidates
    
    def send_interview_invitation(self, candidate: dict, job_title: str, job_id: str):
        """Send interview invitation email to a candidate"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Interview Invitation - {job_title}"
            msg['From'] = self.sender_email
            msg['To'] = candidate['email']
            
            # Generate interview time slots (next 3 business days)
            time_slots = self._generate_time_slots()
            
            # Create HTML email
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .score-box {{ background: #e7f3ff; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }}
                    .time-slots {{ background: white; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                    .time-slot {{ padding: 10px; margin: 5px 0; background: #f0f0f0; border-radius: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .btn {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Congratulations!</h1>
                        <p>You've been selected for an interview</p>
                    </div>
                    <div class="content">
                        <p>Dear {candidate['name']},</p>
                        
                        <p>We are pleased to inform you that you have successfully passed the initial assessment for the <strong>{job_title}</strong> position.</p>
                        
                        <div class="score-box">
                            <h3>Your Assessment Results:</h3>
                            <p>✓ Score: <strong>{candidate['score']}%</strong></p>
                            <p>✓ Correct Answers: <strong>{candidate['correct_answers']}/{candidate['total_questions']}</strong></p>
                            <p>✓ Status: <strong>Selected for Interview</strong></p>
                        </div>
                        
                        <h3>Next Steps - Interview Scheduling:</h3>
                        <p>We would like to invite you for an interview to discuss your qualifications further and learn more about your experience.</p>
                        
                        <div class="time-slots">
                            <h4>Available Time Slots:</h4>
                            {''.join([f'<div class="time-slot">📅 {slot}</div>' for slot in time_slots])}
                        </div>
                        
                        <p>Please reply to this email with your preferred time slot(s). We will confirm the final interview time and send you the meeting details (video call link or office location).</p>
                        
                        <p><strong>Interview Format:</strong></p>
                        <ul>
                            <li>Duration: 45-60 minutes</li>
                            <li>Technical discussion about your experience</li>
                            <li>Questions about the role and company</li>
                            <li>Q&A session</li>
                        </ul>
                        
                        <p>If none of these time slots work for you, please let us know your availability and we'll do our best to accommodate.</p>
                        
                        <p>We look forward to speaking with you!</p>
                        
                        <p>Best regards,<br>
                        <strong>Recruitment Team</strong></p>
                        
                        <div class="footer">
                            <p>This is an automated message from the Agentic Hiring System</p>
                            <p>Job ID: {job_id}</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"✓ Interview invitation sent to {candidate['email']} (Score: {candidate['score']}%)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send interview invitation to {candidate['email']}: {e}")
            return False
    
    def _generate_time_slots(self):
        """Generate available interview time slots for next 3 business days"""
        time_slots = []
        current_date = datetime.now()
        days_added = 0
        
        while days_added < 3:
            current_date += timedelta(days=1)
            
            # Skip weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
            
            # Add morning and afternoon slots
            date_str = current_date.strftime('%A, %B %d, %Y')
            time_slots.append(f"{date_str} - 10:00 AM")
            time_slots.append(f"{date_str} - 2:00 PM")
            
            days_added += 1
        
        return time_slots
    
    def schedule_interviews_for_job(self, job_id: str, job_title: str, top_n: int = 2):
        """
        Main function: Get candidates, select top N, send interview invitations
        
        Args:
            job_id: Unique job identifier
            job_title: Job title (used for finding answer files)
            top_n: Number of top candidates to select (default: 2)
        
        Returns:
            dict with results
        """
        logger.info("=" * 80)
        logger.info("STARTING INTERVIEW SCHEDULING")
        logger.info(f"Job: {job_title} (ID: {job_id})")
        logger.info(f"Selecting top {top_n} candidates")
        logger.info("=" * 80)
        
        # Get all candidates who completed MCQ
        all_candidates = self.get_candidates_by_job(job_id, job_title)
        
        if not all_candidates:
            logger.warning("No candidates found who completed MCQ assessment")
            return {
                'success': False,
                'message': 'No candidates found who completed MCQ assessment',
                'total_candidates': 0,
                'selected_candidates': 0,
                'invitations_sent': 0
            }
        
        # Select top candidates
        top_candidates = self.select_top_candidates(all_candidates, top_n)
        
        # Send interview invitations
        invitations_sent = 0
        failed = []
        
        for candidate in top_candidates:
            success = self.send_interview_invitation(candidate, job_title, job_id)
            if success:
                invitations_sent += 1
            else:
                failed.append(candidate['email'])
        
        logger.info("=" * 80)
        logger.info("INTERVIEW SCHEDULING COMPLETED")
        logger.info(f"Total candidates: {len(all_candidates)}")
        logger.info(f"Selected: {len(top_candidates)}")
        logger.info(f"Invitations sent: {invitations_sent}")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'message': f'Interview invitations sent to top {len(top_candidates)} candidates',
            'total_candidates': len(all_candidates),
            'selected_candidates': len(top_candidates),
            'invitations_sent': invitations_sent,
            'failed': failed,
            'top_candidates': [
                {
                    'email': c['email'],
                    'name': c['name'],
                    'score': c['score'],
                    'rank': idx + 1
                }
                for idx, c in enumerate(top_candidates)
            ]
        }


def main():
    """Test the interview scheduler"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python interview_scheduler.py <job_id> <job_title> [top_n]")
        print("Example: python interview_scheduler.py 20251031_221530 'Senior Python Developer' 2")
        sys.exit(1)
    
    job_id = sys.argv[1]
    job_title = sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    scheduler = InterviewScheduler()
    result = scheduler.schedule_interviews_for_job(job_id, job_title, top_n)
    
    print("\n" + "=" * 80)
    print("RESULTS:")
    print(json.dumps(result, indent=2))
    print("=" * 80)


if __name__ == '__main__':
    main()
