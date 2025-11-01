"""
MCQ Email Automation
Sends MCQ assessment emails to candidates who completed onboarding
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from python.utils.helpers import get_logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = get_logger(__name__)


class MCQEmailSender:
    """Send MCQ assessment emails via SendGrid"""
    
    def __init__(self, api_key: str, sender_email: str):
        """
        Initialize email sender
        
        Args:
            api_key: SendGrid API key
            sender_email: Sender email address
        """
        self.sg_client = SendGridAPIClient(api_key)
        self.sender_email = sender_email
    
    def send_mcq_email(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        job_id: int,
        mcq_url: str
    ) -> bool:
        """
        Send MCQ assessment email to candidate
        
        Args:
            candidate_email: Candidate's email
            candidate_name: Candidate's name
            job_title: Job position title
            job_id: Job ID
            mcq_url: URL to MCQ form
            
        Returns:
            True if sent successfully
        """
        try:
            # HTML email body
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .info-box {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #667eea;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        padding: 15px 40px;
                        border-radius: 8px;
                        font-weight: bold;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .footer {{
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                    }}
                    ul {{
                        padding-left: 20px;
                    }}
                    li {{
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Technical Assessment</h1>
                    <p>{job_title}</p>
                </div>
                
                <div class="content">
                    <p>Dear {candidate_name},</p>
                    
                    <p>Thank you for completing your onboarding form! We're excited to move forward with your application.</p>
                    
                    <div class="info-box">
                        <h3>Next Step: Technical Assessment</h3>
                        <p>Please complete a brief technical assessment consisting of <strong>5 multiple-choice questions</strong>.</p>
                        
                        <p><strong>Assessment Details:</strong></p>
                        <ul>
                            <li>Duration: Approximately 15-20 minutes</li>
                            <li>Questions: 5 technical MCQs</li>
                            <li>Format: Multiple choice</li>
                            <li>Instant Results: You'll see your score immediately</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="{mcq_url}" class="button">Start Assessment</a>
                    </center>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>Answer all questions to the best of your ability</li>
                        <li>You'll receive instant feedback after submission</li>
                        <li>Top performers will be invited for interviews</li>
                    </ul>
                    
                    <p>Good luck! We look forward to reviewing your assessment.</p>
                    
                    <p>Best regards,<br>
                    Recruitment Team</p>
                    
                    <div class="footer">
                        <p>This is an automated email. Please do not reply.</p>
                        <p>If you have questions, contact us at {self.sender_email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email using SendGrid
            message = Mail(
                from_email=self.sender_email,
                to_emails=candidate_email,
                subject=f"Technical Assessment - {job_title}",
                html_content=html
            )
            
            response = self.sg_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"MCQ email sent to: {candidate_email}")
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send MCQ email to {candidate_email}: {e}")
            return False
    
    def send_interview_invitation(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        score: float,
        rank: int
    ) -> bool:
        """
        Send interview invitation to top candidates
        
        Args:
            candidate_email: Candidate's email
            candidate_name: Candidate's name
            job_title: Job position title
            score: Assessment score percentage
            rank: Candidate's rank (1, 2, or 3)
            
        Returns:
            True if sent successfully
        """
        try:
            # HTML email body
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .celebration {{
                        text-align: center;
                        font-size: 48px;
                        margin: 20px 0;
                    }}
                    .score-box {{
                        background: white;
                        padding: 25px;
                        border-radius: 8px;
                        margin: 20px 0;
                        text-align: center;
                        border: 2px solid #28a745;
                    }}
                    .score {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #28a745;
                        margin: 10px 0;
                    }}
                    .rank {{
                        display: inline-block;
                        background: #ffd700;
                        color: #333;
                        padding: 10px 20px;
                        border-radius: 20px;
                        font-weight: bold;
                        margin: 10px 0;
                    }}
                    .info-box {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Congratulations!</h1>
                    <p>Interview Invitation</p>
                </div>
                
                <div class="content">
                    <div class="celebration">🎉</div>
                    
                    <p>Dear {candidate_name},</p>
                    
                    <p>Excellent work on your technical assessment! We're impressed with your performance.</p>
                    
                    <div class="score-box">
                        <p><strong>Your Assessment Score:</strong></p>
                        <div class="score">{score:.1f}%</div>
                        <div class="rank">Top #{rank} Candidate</div>
                    </div>
                    
                    <div class="info-box">
                        <h3>You've Been Selected for an Interview!</h3>
                        <p>Based on your outstanding performance, we would like to invite you for an interview for the <strong>{job_title}</strong> position.</p>
                        
                        <p><strong>Next Steps:</strong></p>
                        <ul>
                            <li>Our HR team will contact you within 1-2 business days</li>
                            <li>We'll schedule a convenient time for your interview</li>
                            <li>Please prepare to discuss your experience and technical skills</li>
                        </ul>
                    </div>
                    
                    <p>We're excited about the possibility of you joining our team!</p>
                    
                    <p>Best regards,<br>
                    Recruitment Team</p>
                    
                    <div class="footer">
                        <p>This is an automated email. Please do not reply.</p>
                        <p>If you have questions, contact us at {self.sender_email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email using SendGrid
            message = Mail(
                from_email=self.sender_email,
                to_emails=candidate_email,
                subject=f"Interview Invitation - {job_title}",
                html_content=html
            )
            
            response = self.sg_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Interview invitation sent to: {candidate_email} (Rank #{rank}, Score: {score:.1f}%)")
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send interview invitation to {candidate_email}: {e}")
            return False


def get_mcq_form_url(candidate_email: str, job_id: int, job_title: str, job_description: str = "") -> str:
    """
    Generate MCQ form URL with parameters
    
    Args:
        candidate_email: Candidate's email
        job_id: Job ID
        job_title: Job title
        job_description: Job description for MCQ generation
        
    Returns:
        MCQ form URL
    """
    import os
    from urllib.parse import quote
    
    base_url = os.getenv('MCQ_FORM_URL', 'http://localhost:5001/mcq')
    url = f"{base_url}?candidate_email={candidate_email}&job_id={job_id}&job_title={quote(job_title)}"
    
    if job_description:
        # Truncate to 200 chars for URL safety
        desc_truncated = job_description[:200] if len(job_description) > 200 else job_description
        url += f"&job_description={quote(desc_truncated)}"
    
    return url


def send_feedback_email(
    email_sender,
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    score: float,
    correct_count: int,
    total_questions: int,
    results: list
) -> bool:
    """
    Send instant feedback email with MCQ results
    
    Args:
        email_sender: MCQEmailSender instance
        candidate_email: Candidate's email
        candidate_name: Candidate's name
        job_title: Job title
        score: Score percentage
        correct_count: Number of correct answers
        total_questions: Total number of questions
        results: Detailed results list
        
    Returns:
        True if sent successfully
    """
    try:
        # Build summary only (no detailed question breakdown)
        results_html = f"""
        <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #333;">Assessment Summary</h3>
            <p style="font-size: 16px; margin: 10px 0;">
                ✓ Questions Answered: <strong>{total_questions}</strong><br>
                ✓ Correct Answers: <strong>{correct_count}</strong><br>
                ✓ Your Score: <strong>{score:.1f}%</strong>
            </p>
        </div>
        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; font-size: 15px;">
                ✅ <strong>Assessment Completed Successfully!</strong><br>
                Thank you for taking the time to complete this technical assessment.
            </p>
        </div>
        """
        
        # HTML email body
        passing_status = "Great job! You may be invited for an interview." if score >= 60 else "Thank you for your time. We will review all applications."
        status_color = "#28a745" if score >= 60 else "#dc3545"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .score-box {{
                    background: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: center;
                    border: 2px solid #667eea;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Assessment Complete!</h1>
                <p>{job_title}</p>
            </div>
            
            <div class="content">
                <p>Dear {candidate_name},</p>
                
                <p>Thank you for completing the technical assessment! Here are your results:</p>
                
                <div class="score-box">
                    <p><strong>Your Score</strong></p>
                    <div class="score">{score:.1f}%</div>
                    <p>{correct_count} out of {total_questions} correct</p>
                    <p style="color: {status_color}; font-weight: bold; margin-top: 15px;">{passing_status}</p>
                </div>
                
                <h3 style="margin: 25px 0 15px 0;">Detailed Results:</h3>
                {results_html}
                
                <p style="margin-top: 25px;">We appreciate your time and effort in completing this assessment. Our team will review all applications and get back to you soon.</p>
                
                <p>Best regards,<br>
                Recruitment Team</p>
                
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                    <p>If you have questions, contact us at {email_sender.sender_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email using SendGrid
        message = Mail(
            from_email=email_sender.sender_email,
            to_emails=candidate_email,
            subject=f"Your Assessment Results - {job_title}",
            html_content=html
        )
        
        response = email_sender.sg_client.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Feedback email sent to: {candidate_email} (Score: {score:.1f}%)")
            return True
        else:
            logger.error(f"SendGrid returned status {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to send feedback email to {candidate_email}: {e}")
        return False


if __name__ == "__main__":
    # Test email sending
    from dotenv import load_dotenv
    load_dotenv()
    
    sender = MCQEmailSender(
        api_key=os.getenv('SENDGRID_API_KEY'),
        sender_email=os.getenv('SENDER_EMAIL', 'noreply@recruitment.com')
    )
    
    # Test MCQ email
    mcq_url = get_mcq_form_url(
        candidate_email="test@example.com",
        job_id=23,
        job_title="Senior Python Developer"
    )
    
    sender.send_mcq_email(
        candidate_email="test@example.com",
        candidate_name="Test Candidate",
        job_title="Senior Python Developer",
        job_id=23,
        mcq_url=mcq_url
    )
    
    print("Test email sent!")
