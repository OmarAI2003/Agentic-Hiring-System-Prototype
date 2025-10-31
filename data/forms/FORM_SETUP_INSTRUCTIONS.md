# How to Create the Google Form for Candidate Onboarding

## Quick Setup (5 minutes)

1. **Go to Google Forms**: https://docs.google.com/forms/u/0/
2. **Click "Blank" to create new form**
3. **Set Form Title**: "Candidate Onboarding Form"
4. **Add Description**: "Please complete this form to proceed with your application"

---

## Form Sections and Fields

### Section 1: Personal Information

1. **Full Name** (Required)
   - Type: Short answer

2. **Email Address** (Required)
   - Type: Short answer

3. **Phone Number** (Required)
   - Type: Short answer

4. **Current Location** (Required)
   - Type: Short answer

---

### Section 2: Demographic Information

1. **Age** (Optional)
   - Type: Short answer

2. **Nationality** (Optional)
   - Type: Short answer

3. **Marital Status** (Optional)
   - Type: Multiple choice
   - Options:
     - Single
     - Married
     - Prefer not to say

---

### Section 3: Work Authorization

1. **Work Authorization Status** (Required)
   - Type: Multiple choice
   - Options:
     - Citizen
     - Permanent Resident
     - Work Visa (H1B)
     - Student Visa (F1/OPT)
     - Require Sponsorship

2. **Additional Details** (Optional)
   - Type: Paragraph
   - Description: "If applicable, please provide additional work authorization details"

---

### Section 4: Availability

1. **Earliest Start Date** (Required)
   - Type: Date

2. **Preferred Interview Times** (Required)
   - Type: Paragraph
   - Description: "e.g., weekday mornings, afternoons"

3. **Time Zone** (Required)
   - Type: Short answer

---

### Section 5: Documents & Additional Information

1. **Resume/CV Link** (Required)
   - Type: Short answer
   - Description: "Google Drive, Dropbox, or any cloud storage link"

2. **Portfolio/Website Link** (Optional)
   - Type: Short answer

3. **LinkedIn Profile URL** (Optional)
   - Type: Short answer

4. **GitHub Profile URL** (Optional)
   - Type: Short answer
   - Description: "For technical roles"

5. **Additional Information or Questions** (Optional)
   - Type: Paragraph

---

## After Creating the Form

### Step 1: Get the Form URL

1. Click the **"Send"** button (top right)
2. Click the **link icon** (<>)
3. Click **"Shorten URL"** if desired
4. **Copy the form URL**

### Step 2: Configure Form Settings

1. Click the **Settings** icon (gear icon)
2. Under **"Responses"** tab:
   - ✅ Check "Collect email addresses"
   - ✅ Check "Allow response editing"
   - ❌ Uncheck "Limit to 1 response" (so people can resubmit)
   - ❌ Uncheck "Requires sign-in" (unless you want to restrict)
3. Click **Save**

### Step 3: Update the Code

1. Open file: `python/onboarding/form_manager.py`
2. Find line: `self.base_form_url = "https://docs.google.com/forms..."`
3. Replace with your actual form URL

Example:
```python
self.base_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSc_YOUR_FORM_ID_HERE/viewform"
```

### Step 4: Update Email Template

1. Open file: `python/onboarding/email_automation.py`
2. The form URL will be automatically used in emails

---

## Testing the Form

### Test as a Candidate

1. Open your form URL in incognito/private browser
2. Fill out the form
3. Submit

### View Responses

1. In Google Forms, click **"Responses"** tab
2. View in Google Sheets: Click the green Sheets icon
3. Or download as CSV: Click the 3 dots menu → Download responses (.csv)

---

## Integration with Email System

Once your form is ready, update the test script:

```bash
# Update form URL in form_manager.py, then test
PYTHONPATH=. python test_simple_integration.py
```

Emails will now include your actual Google Form link!

---

## Quick Form Link (For Testing)

If you don't want to create a form now, you can use this template:
https://docs.google.com/forms/d/e/1FAIpQLSdKxFxOxBxFxBxFxBxFxBxFxBxFxBxFxBxFxBx/viewform

**Note**: Replace with your actual form URL before production!

---

## Tips

- Use clear, concise labels
- Add descriptions for complex fields
- Test the form yourself before sending to candidates
- Check responses regularly in Google Forms
- Set up email notifications (Settings → Responses → "Get email notifications")

---

## Need Help?

- Google Forms Help: https://support.google.com/docs/topic/9055404
- Video Tutorial: Search "How to create Google Form" on YouTube
