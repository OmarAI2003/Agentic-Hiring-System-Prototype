"""
Phase 2: Email Automation for Candidate Onboarding
Sends personalized emails to shortlisted candidates using SendGrid API
"""
import os
from datetime import datetime
from typing import Dict, List
from python.utils.helpers import get_logger, log_action
from python.onboarding.form_manager import GoogleFormManager
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = get_logger(__name__)


class EmailAutomation:
    """
    Handles automated email sending for candidate onboarding
    Uses SendGrid API (free, works on Render)
    """
    
    def __init__(self, test_mode: bool = True, test_email: str = "on152052@gmail.com"):
        """
        Initialize email automation
        
        Args:
            test_mode: If True, all emails go to test_email instead of real candidates
            test_email: Email address for testing (default: on152052@gmail.com)
        """
        self.test_mode = test_mode
        self.test_email = test_email
        
        # Initialize form manager
        self.form_manager = GoogleFormManager()
        
        # Get SendGrid credentials from environment
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@recruitment.com')
        
        if not self.sendgrid_api_key:
            logger.warning("SendGrid API key not found in environment. Email sending will be disabled.")
            logger.warning("Set SENDGRID_API_KEY in .env file")
            self.enabled = False
        else:
            self.enabled = True
            self.sg_client = SendGridAPIClient(self.sendgrid_api_key)
            logger.info(f"Email automation initialized (Test mode: {test_mode})")
    
    def send_onboarding_email(self, candidate: Dict, job: Dict, form_url: str = None) -> bool:
        """
        Send personalized onboarding email to candidate
        
        Args:
            candidate: Candidate information
            job: Job information  
            form_url: URL to onboarding form (auto-generated if not provided)
            
        Returns:
            True if email sent successfully
        """
        if not self.enabled:
            logger.warning("Email sending disabled (missing credentials)")
            return False
        
        # Generate form URL if not provided
        if not form_url:
            form_url = self.form_manager.get_onboarding_form_url(
                candidate_email=candidate.get('email'),
                job_id=job.get('job_id'),
                job_title=job.get('title', '')
            )
        # Determine recipient
        if self.test_mode:
            recipient_email = self.test_email
            recipient_name = f"{candidate['full_name']} (TEST)"
            logger.info(f"📧 TEST MODE: Sending to {self.test_email} instead of {candidate.get('email')}")
        else:
            recipient_email = candidate.get('email')
            recipient_name = candidate['full_name']
            
            if not recipient_email:
                logger.error(f"No email found for candidate {candidate['full_name']}")
                return False
        
        try:
            # Create email content
            subject = f"Congratulations! You've been shortlisted for {job['title']}"
            html_content = self._generate_email_html(candidate, job, form_url)
            
            # Send email using SendGrid
            logger.info(f"Sending email to {recipient_name} ({recipient_email})...")
            
            message = Mail(
                from_email=self.sender_email,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Email sent successfully to {recipient_name}")
                
                # Log action
                log_action('candidate_onboarding',
                          f"Sent onboarding email to {candidate['full_name']}",
                          {'recipient': recipient_email, 'job': job['title'], 'test_mode': self.test_mode})
                
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_name}: {str(e)}")
            return False
    
    def send_batch_emails(self, candidates: List[Dict], job: Dict, form_url: str = None) -> Dict:
        """
        Send onboarding emails to multiple candidates
        
        Args:
            candidates: List of candidate dictionaries
            job: Job information
            form_url: URL to onboarding form
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            'sent': 0,
            'failed': 0,
            'recipients': []
        }
        
        logger.info(f"📧 Sending onboarding emails to {len(candidates)} candidates...")
        
        for candidate in candidates:
            success = self.send_onboarding_email(candidate, job, form_url)
            
            if success:
                results['sent'] += 1
                results['recipients'].append(candidate['full_name'])
            else:
                results['failed'] += 1
        
        logger.info(f"✓ Batch complete: {results['sent']} sent, {results['failed']} failed")
        
        return results
    
    def _generate_email_html(self, candidate: Dict, job: Dict, form_url: str = None) -> str:
        """Generate personalized HTML email content"""
        
        # Generate form URL if not provided
        if not form_url:
            form_url = f"https://forms.google.com/candidate-onboarding?id={candidate.get('email', 'unknown')}"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
            border-radius: 0 0 5px 5px;
        }}
        .button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #777;
            font-size: 12px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Congratulations!</h1>
        </div>
        <div class="content">
            <h2>Dear {candidate['full_name']},</h2>
            
            <p>We are pleased to inform you that you have been <strong>shortlisted</strong> for the position of:</p>
            
            <div class="highlight">
                <h3>{job['title']}</h3>
                <p><strong>Location:</strong> {job.get('location', 'Remote')}</p>
                <p><strong>Employment Type:</strong> {job.get('employment_type', 'Full-time')}</p>
            </div>
            
            <p>Your profile stood out among many candidates, and we believe your skills and experience align well with our requirements.</p>
            
            <h3>Next Steps</h3>
            <p>To proceed with your application, please complete our onboarding form:</p>
            
            <center>
                <a href="{form_url}" class="button">Complete Onboarding Form</a>
            </center>
            
            <p>The form will collect:</p>
            <ul>
                <li>Personal and demographic information</li>
                <li>Availability and scheduling preferences</li>
                <li>Work authorization and visa status</li>
                <li>Additional documents (resume, certificates, etc.)</li>
            </ul>
            
            <p><strong>Please complete the form within 7 days.</strong></p>
            
            <p>If you have any questions, feel free to reply to this email.</p>
            
            <p>We look forward to learning more about you!</p>
            
            <p>Best regards,<br>
            <strong>Hiring Team</strong><br>
            Agentic HR Recruitment System</p>
        </div>
        <div class="footer">
            <p>This is an automated message from our AI-powered recruitment system.</p>
            <p>Sent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html


def test_email_automation():
    """Test email automation with sample data"""
    
    print("\n" + "="*70)
    print("EMAIL AUTOMATION TEST")
    print("="*70)
    
    # Check credentials
    if not os.getenv('GMAIL_EMAIL') or not os.getenv('GMAIL_APP_PASSWORD'):
        print("\n⚠️  Gmail credentials not configured!")
        print("\nTo enable email sending, add to .env file:")
        print("GMAIL_EMAIL=your-email@gmail.com")
        print("GMAIL_APP_PASSWORD=your-16-char-app-password")
        print("\nNote: Use Gmail App Password, not regular password")
        print("Create at: https://myaccount.google.com/apppasswords")
        return
    
    # Initialize email automation in test mode
    email_system = EmailAutomation(test_mode=True, test_email="on152052@gmail.com")
    
    if not email_system.enabled:
        print("\n❌ Email system not enabled (missing credentials)")
        return
    
    # Sample candidate
    sample_candidate = {
        'full_name': 'John Doe',
        'email': 'real.candidate@example.com',  # Won't be used in test mode
        'experience_years': 5,
        'current_position': 'Senior Python Developer',
        'match_score': 95.5
    }
    
    # Sample job
    sample_job = {
        'title': 'Lead Backend Engineer',
        'location': 'Remote (USA)',
        'employment_type': 'Full-time'
    }
    
    # Send test email
    print("\n📧 Sending test email to on152052@gmail.com...")
    print(f"   (Real candidate email {sample_candidate['email']} will be ignored in test mode)")
    
    success = email_system.send_onboarding_email(
        sample_candidate, 
        sample_job,
        form_url="https://forms.google.com/test-form"
    )
    
    if success:
        print("\n✅ TEST EMAIL SENT SUCCESSFULLY!")
        print(f"   Check inbox: on152052@gmail.com")
    else:
        print("\n❌ Failed to send test email")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    test_email_automation()
