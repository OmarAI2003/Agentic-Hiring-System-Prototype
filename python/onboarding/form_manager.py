"""
Phase 2: Google Form Manager for Candidate Onboarding
Creates and manages Google Forms for collecting candidate information
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from python.utils.helpers import get_logger, log_action

logger = get_logger(__name__)


class GoogleFormManager:
    """
    Manages Google Forms for candidate onboarding
    Stores form responses locally (no Google API needed for MVP)
    """
    
    def __init__(self, storage_path: str = "data/forms"):
        """
        Initialize form manager
        
        Args:
            storage_path: Directory to store form responses
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Use local Flask form instead of Google Forms (completely FREE)
        self.base_form_url = "http://127.0.0.1:5000/onboarding"
        
        logger.info("Google Form Manager initialized")
    
    def get_onboarding_form_url(self, candidate_email: str = None, job_id: int = None, job_title: str = None, job_description: str = None) -> str:
        """
        Get the onboarding form URL with pre-filled parameters
        
        Args:
            candidate_email: Optional candidate email for pre-filling
            job_id: Optional job ID for tracking
            job_title: Optional job title for context
            job_description: Optional job description for MCQ generation
            
        Returns:
            Form URL with query parameters
        """
        from urllib.parse import quote
        
        # Build URL with query parameters
        params = []
        if candidate_email:
            params.append(f"candidate_email={candidate_email}")
        if job_id:
            params.append(f"job_id={job_id}")
        if job_title:
            params.append(f"job_title={quote(job_title)}")
        # Note: job_description is NOT passed via URL
        # It will be loaded from the job file (data/jobs/job_{job_id}.json) when needed
        
        if params:
            form_url = f"{self.base_form_url}?{'&'.join(params)}"
        else:
            form_url = self.base_form_url
        
        return form_url
    
    def get_form_template(self) -> Dict:
        """
        Get the template structure for the onboarding form
        
        Returns:
            Dictionary with form fields and structure
        """
        return {
            "title": "Candidate Onboarding Form",
            "description": "Please complete this form to proceed with your application",
            "sections": [
                {
                    "title": "Personal Information",
                    "fields": [
                        {
                            "id": "full_name",
                            "label": "Full Name",
                            "type": "text",
                            "required": True
                        },
                        {
                            "id": "email",
                            "label": "Email Address",
                            "type": "email",
                            "required": True
                        },
                        {
                            "id": "phone",
                            "label": "Phone Number",
                            "type": "text",
                            "required": True
                        },
                        {
                            "id": "location",
                            "label": "Current Location",
                            "type": "text",
                            "required": True
                        }
                    ]
                },
                {
                    "title": "Demographic Information",
                    "fields": [
                        {
                            "id": "age",
                            "label": "Age",
                            "type": "number",
                            "required": False
                        },
                        {
                            "id": "nationality",
                            "label": "Nationality",
                            "type": "text",
                            "required": False
                        },
                        {
                            "id": "marital_status",
                            "label": "Marital Status",
                            "type": "choice",
                            "options": ["Single", "Married", "Prefer not to say"],
                            "required": False
                        }
                    ]
                },
                {
                    "title": "Work Authorization",
                    "fields": [
                        {
                            "id": "visa_status",
                            "label": "Work Authorization Status",
                            "type": "choice",
                            "options": [
                                "Citizen",
                                "Permanent Resident",
                                "Work Visa (H1B)",
                                "Student Visa (F1/OPT)",
                                "Require Sponsorship"
                            ],
                            "required": True
                        },
                        {
                            "id": "work_authorization_details",
                            "label": "Additional Details (if applicable)",
                            "type": "textarea",
                            "required": False
                        }
                    ]
                },
                {
                    "title": "Availability",
                    "fields": [
                        {
                            "id": "availability_date",
                            "label": "Earliest Start Date",
                            "type": "date",
                            "required": True
                        },
                        {
                            "id": "preferred_interview_times",
                            "label": "Preferred Interview Times (e.g., weekday mornings, afternoons)",
                            "type": "textarea",
                            "required": True
                        },
                        {
                            "id": "time_zone",
                            "label": "Time Zone",
                            "type": "text",
                            "required": True
                        }
                    ]
                },
                {
                    "title": "Documents & Additional Information",
                    "fields": [
                        {
                            "id": "resume_link",
                            "label": "Resume/CV Link (Google Drive, Dropbox, etc.)",
                            "type": "url",
                            "required": True
                        },
                        {
                            "id": "portfolio_link",
                            "label": "Portfolio/Website Link (optional)",
                            "type": "url",
                            "required": False
                        },
                        {
                            "id": "linkedin_url",
                            "label": "LinkedIn Profile URL",
                            "type": "url",
                            "required": False
                        },
                        {
                            "id": "github_url",
                            "label": "GitHub Profile URL (for technical roles)",
                            "type": "url",
                            "required": False
                        },
                        {
                            "id": "additional_info",
                            "label": "Additional Information or Questions",
                            "type": "textarea",
                            "required": False
                        }
                    ]
                }
            ]
        }
    
    def save_form_response(self, response_data: Dict) -> str:
        """
        Save form response locally
        
        Args:
            response_data: Form response data
            
        Returns:
            Response ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate_email = response_data.get('email', 'unknown').replace('@', '_at_')
        
        response_id = f"response_{timestamp}_{candidate_email}"
        filepath = os.path.join(self.storage_path, f"{response_id}.json")
        
        # Add metadata
        response_data['response_id'] = response_id
        response_data['submitted_at'] = datetime.now().isoformat()
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=2)
        
        logger.info(f"Saved form response: {response_id}")
        
        log_action('candidate_onboarding',
                  f"Received form response from {response_data.get('full_name')}",
                  {'response_id': response_id, 'email': response_data.get('email')})
        
        return response_id
    
    def get_form_responses(self, candidate_email: str = None) -> List[Dict]:
        """
        Get all form responses or filter by candidate email
        
        Args:
            candidate_email: Optional email to filter
            
        Returns:
            List of form responses
        """
        responses = []
        
        if not os.path.exists(self.storage_path):
            return responses
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                
                with open(filepath, 'r') as f:
                    response = json.load(f)
                
                # Filter by email if provided
                if candidate_email and response.get('email') != candidate_email:
                    continue
                
                responses.append(response)
        
        # Sort by submission time (newest first)
        responses.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        return responses
    
    def generate_form_html(self, form_url: str = None) -> str:
        """
        Generate an embedded HTML form (iframe) for the Google Form
        
        Args:
            form_url: Google Form URL
            
        Returns:
            HTML string with embedded form
        """
        if not form_url:
            form_url = self.base_form_url
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Candidate Onboarding Form</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 20px auto;
            padding: 0 20px;
        }}
        iframe {{
            width: 100%;
            height: 1400px;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Candidate Onboarding</h1>
        <p>Please complete the form below to proceed with your application</p>
    </div>
    <div class="container">
        <iframe src="{form_url}" frameborder="0" marginheight="0" marginwidth="0">
            Loading form...
        </iframe>
    </div>
</body>
</html>
"""
        return html
    
    def create_google_form_instructions(self) -> str:
        """
        Generate instructions for creating the Google Form manually
        
        Returns:
            Markdown instructions
        """
        template = self.get_form_template()
        
        instructions = """
# How to Create the Google Form

## Quick Setup (5 minutes)

1. **Go to Google Forms**: https://docs.google.com/forms
2. **Click "Blank" or "+" to create new form**
3. **Set Form Title**: "Candidate Onboarding Form"
4. **Add Description**: "Please complete this form to proceed with your application"

## Form Sections and Fields

"""
        
        for section in template['sections']:
            instructions += f"\n### Section: {section['title']}\n\n"
            
            for field in section['fields']:
                required = " (Required)" if field['required'] else " (Optional)"
                instructions += f"**{field['label']}{required}**\n"
                instructions += f"- Type: {field['type']}\n"
                
                if 'options' in field:
                    instructions += f"- Options: {', '.join(field['options'])}\n"
                
                instructions += "\n"
        
        instructions += """
## After Creating the Form

1. **Click "Send"** button (top right)
2. **Click the link icon** (<>)
3. **Copy the form URL** (starts with https://docs.google.com/forms/d/e/...)
4. **Update the code**:
   - Open: `python/onboarding/form_manager.py`
   - Find: `self.base_form_url = "https://docs.google.com/forms..."`
   - Replace with your form URL

## View Responses

1. In Google Forms, click "Responses" tab
2. View in spreadsheet: Click green Sheets icon
3. Download as CSV for offline processing

## Tips

- Make sure form is set to "Anyone with the link can respond"
- Don't require sign-in (Settings → Responses → uncheck "Limit to 1 response")
- Enable email collection (Settings → Responses → check "Collect email addresses")
"""
        
        return instructions


def test_form_manager():
    """Test form manager functionality"""
    
    print("\n" + "="*70)
    print("GOOGLE FORM MANAGER TEST")
    print("="*70)
    
    manager = GoogleFormManager()
    
    # Get form template
    print("\n[1] Form Template Structure:")
    print("-"*70)
    template = manager.get_form_template()
    print(f"Form Title: {template['title']}")
    print(f"Total Sections: {len(template['sections'])}\n")
    
    for i, section in enumerate(template['sections'], 1):
        print(f"{i}. {section['title']}")
        print(f"   Fields: {len(section['fields'])}")
        for field in section['fields'][:2]:  # Show first 2 fields
            req = " *" if field['required'] else ""
            print(f"   - {field['label']}{req}")
        if len(section['fields']) > 2:
            print(f"   ... and {len(section['fields']) - 2} more")
        print()
    
    # Get form URL
    print("[2] Form URL Generation:")
    print("-"*70)
    form_url = manager.get_onboarding_form_url(
        candidate_email="test@example.com",
        job_id=123
    )
    print(f"Generated URL:\n{form_url}\n")
    
    # Simulate form response
    print("[3] Simulating Form Response:")
    print("-"*70)
    sample_response = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "location": "New York, NY",
        "age": 28,
        "nationality": "American",
        "marital_status": "Single",
        "visa_status": "Citizen",
        "availability_date": "2025-11-15",
        "preferred_interview_times": "Weekday mornings (9 AM - 12 PM EST)",
        "time_zone": "EST (UTC-5)",
        "resume_link": "https://drive.google.com/file/d/abc123",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "github_url": "https://github.com/johndoe"
    }
    
    response_id = manager.save_form_response(sample_response)
    print(f"Saved response: {response_id}")
    
    # Retrieve responses
    print("\n[4] Retrieving Form Responses:")
    print("-"*70)
    responses = manager.get_form_responses()
    print(f"Total responses: {len(responses)}")
    
    if responses:
        print(f"\nLatest response:")
        print(f"  Name: {responses[0].get('full_name')}")
        print(f"  Email: {responses[0].get('email')}")
        print(f"  Submitted: {responses[0].get('submitted_at')}")
    
    # Generate instructions
    print("\n[5] Form Creation Instructions:")
    print("-"*70)
    instructions_file = "data/forms/FORM_SETUP_INSTRUCTIONS.md"
    instructions = manager.create_google_form_instructions()
    
    os.makedirs("data/forms", exist_ok=True)
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"Instructions saved to: {instructions_file}")
    print("\nTo create your Google Form:")
    print("1. Open: data/forms/FORM_SETUP_INSTRUCTIONS.md")
    print("2. Follow the step-by-step guide")
    print("3. Update form URL in form_manager.py")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == '__main__':
    test_form_manager()
