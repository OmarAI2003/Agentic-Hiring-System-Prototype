# 🚀 Render Deployment Guide - FREE Tier

## Prerequisites
- GitHub account (you already have this ✅)
- Render account (free - NO credit card needed)
- Your Groq API key
- Your Gmail credentials (with App Password)

## Step-by-Step Deployment (100% FREE)

### 1. Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended)
4. **NO credit card required!**

### 2. Connect Your GitHub Repository
1. After signing in, Render will ask to connect to GitHub
2. Click "Connect GitHub"
3. Authorize Render to access your repositories
4. Select your repository: "OmarAI2003/Agentic-Hiring-System-Prototype"

---

## Deploy Your 3 Services

### 3. Create First Service: HR Control Panel (Main UI)
### 3. Create First Service: HR Control Panel (Main UI)

1. From your Render Dashboard, click **"New +"** in top right
2. Select **"Web Service"**
3. Click **"Connect a repository"** or select your already-connected repo
4. Choose: **"Agentic-Hiring-System-Prototype"**

5. **Configure the service:**
   - **Name**: `agentic-hiring-hr-panel` (or any name you like)
   - **Region**: Choose closest to you (e.g., Oregon USA, Frankfurt EU)
   - **Branch**: `main`
   - **Root Directory**: leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_hr_panel.py`

6. **Select FREE Plan:**
   - Scroll down to "Instance Type"
   - Select **"Free"** (NOT Starter)
   - Shows: $0/month, 750 hours/month

7. **Add Environment Variables** (click "Add Environment Variable" button):
   
   Add these 5 variables:
   
   | Key | Value |
   |-----|-------|
   | `GROQ_API_KEY` | your_actual_groq_api_key |
   | `GMAIL_EMAIL` | your_gmail@gmail.com |
   | `GMAIL_APP_PASSWORD` | your_16_character_password |
   | `ONBOARDING_FORM_URL` | https://agentic-hiring-onboarding.onrender.com/onboarding |
   | `MCQ_FORM_URL` | https://agentic-hiring-mcq.onrender.com/mcq |

   ⚠️ **Note:** The form URLs use placeholder names. We'll update them with actual URLs after deploying the other services.

8. **Click "Create Web Service"**
9. Wait 5-10 minutes while Render builds and deploys

### 4. Create Second Service: Onboarding Form Server

1. Click **"New +"** → **"Web Service"** again
2. Select same repository
3. **Configure:**
   - **Name**: `agentic-hiring-onboarding`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_form_server.py`
   - **Plan**: **Free**

4. **No environment variables needed for this service!**

5. Click **"Create Web Service"**
6. Wait for deployment (~5-10 minutes)

7. **Copy the URL!** 
   - Once live, you'll see a URL like: `https://agentic-hiring-onboarding.onrender.com`
   - Copy this URL - you'll need it next!

---

### 5. Create Third Service: MCQ Assessment Server

1. Click **"New +"** → **"Web Service"** again
2. Select same repository  
3. **Configure:**
   - **Name**: `agentic-hiring-mcq`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_mcq_server.py`
   - **Plan**: **Free**

4. **Add Environment Variables:**
   
   | Key | Value |
   |-----|-------|
   | `GROQ_API_KEY` | your_actual_groq_api_key |
   | `GMAIL_EMAIL` | your_gmail@gmail.com |
   | `GMAIL_APP_PASSWORD` | your_16_character_password |

5. Click **"Create Web Service"**
6. Wait for deployment

7. **Copy the URL!**
   - Once live: `https://agentic-hiring-mcq.onrender.com`
   - Copy this URL too!

---

### 6. Update HR Panel with Real URLs (IMPORTANT!)

Now that you have the real URLs, update the HR Panel:

1. Go back to your **agentic-hiring-hr-panel** service
2. Click **"Environment"** in the left sidebar
3. Find and UPDATE these two variables with your actual URLs:
   - `ONBOARDING_FORM_URL` = `https://your-actual-onboarding-url.onrender.com/onboarding`
   - `MCQ_FORM_URL` = `https://your-actual-mcq-url.onrender.com/mcq`
4. Click **"Save Changes"** 
5. Service will automatically redeploy (takes 2-3 minutes)

---

### 7. Get Your Final URLs

After all services show **"Live"** status (green dot), you have:

1. **HR Panel (Main App)**: 
   - `https://agentic-hiring-hr-panel-xxxx.onrender.com`
   - **This is the URL to share!**

2. **Onboarding Form**: 
   - `https://agentic-hiring-onboarding-xxxx.onrender.com`
   - (Candidates access via email link)

3. **MCQ Assessment**: 
   - `https://agentic-hiring-mcq-xxxx.onrender.com`
   - (Candidates access via email link)

---

## 🎉 Testing Your Deployment

1. **Open your HR Panel URL** in any browser
2. **Create a test job:**
   - Title: "Python Developer"
   - Click "Generate with AI" for description
   - Number of candidates: 2
   - Use your own Gmail credentials
3. **Click "Start Recruitment Workflow"**
4. **Check your email** - you should receive onboarding invitation
5. **Complete the onboarding form**
6. **Check email again** - you'll receive MCQ assessment link
7. **Complete the MCQ**
8. **Check email** - you'll receive:
   - Feedback with your score
   - Interview invitation (automatic!)

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- 750 hours/month per service (always on if using all 3)

💡 **Pro Tip:** 
Keep one service awake by pinging it periodically, or upgrade one to paid ($7/month) for always-on.

## Troubleshooting

### Service Won't Start
- Check "Logs" tab for errors
- Verify environment variables are set correctly
- Ensure PORT is set to correct value

### Emails Not Sending
- Verify GMAIL_EMAIL and GMAIL_APP_PASSWORD
- Check that Gmail App Password is exactly 16 characters
- Ensure 2FA is enabled on Gmail account

### Form URLs Not Working
- Make sure you updated the URLs in HR Panel environment after getting real URLs
- Check that all 3 services are deployed and healthy

## Success Checklist

- ✅ All 3 services show "Live" status
- ✅ HR Panel opens in browser
- ✅ Can create a job
- ✅ Receives onboarding email
- ✅ Can complete onboarding form
- ✅ Receives MCQ assessment email
- ✅ Can complete MCQ
- ✅ Receives feedback email
- ✅ Receives interview invitation email

## Sharing Your Demo

Share your HR Panel URL with anyone:
`https://agentic-hiring-hr-panel.onrender.com`

They can:
- Create jobs
- Test the full recruitment workflow
- Experience the automatic interview scheduling

---

**Deployment time: ~30 minutes**
**Cost: FREE** ✨

Need help? Check the Logs tab in Render dashboard!
