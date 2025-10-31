-- Agentic HR Recruitment System Database Schema
-- PostgreSQL Database

-- Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL,
    experience_level VARCHAR(50) NOT NULL, -- entry, mid, senior
    location VARCHAR(255),
    employment_type VARCHAR(50), -- full-time, part-time, contract
    salary_range VARCHAR(100),
    department VARCHAR(100),
    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active, closed, on-hold
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates Table
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(255),
    age INTEGER,
    nationality VARCHAR(100),
    marital_status VARCHAR(50),
    visa_status VARCHAR(100),
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    resume_url TEXT,
    skills TEXT[],
    experience_years INTEGER,
    current_position VARCHAR(255),
    education TEXT,
    availability_date DATE,
    preferred_interview_times JSONB,
    source VARCHAR(100), -- linkedin, github, referral, job_board
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Applications Table
CREATE TABLE IF NOT EXISTS job_applications (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id INTEGER REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'applied', -- applied, shortlisted, interviewing, rejected, hired
    match_score DECIMAL(5,2), -- 0-100 percentage
    match_details JSONB, -- detailed scoring breakdown
    ranking INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, candidate_id)
);

-- Interview Questions Table
CREATE TABLE IF NOT EXISTS interview_questions (
    question_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id INTEGER REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    category VARCHAR(100), -- technical, behavioral, situational, coding
    difficulty VARCHAR(50), -- easy, medium, hard
    expected_answer TEXT,
    evaluation_criteria TEXT,
    generated_by VARCHAR(50) DEFAULT 'ai', -- ai, manual
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview Schedule Table
CREATE TABLE IF NOT EXISTS interview_schedule (
    interview_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id INTEGER REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    interviewer_email VARCHAR(255) NOT NULL,
    interview_datetime TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    meeting_link TEXT,
    calendar_event_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, completed, cancelled, rescheduled
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview Feedback Table
CREATE TABLE IF NOT EXISTS interview_feedback (
    feedback_id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interview_schedule(interview_id) ON DELETE CASCADE,
    interviewer_email VARCHAR(255) NOT NULL,
    technical_skills_rating INTEGER CHECK (technical_skills_rating >= 1 AND technical_skills_rating <= 10),
    communication_skills_rating INTEGER CHECK (communication_skills_rating >= 1 AND communication_skills_rating <= 10),
    culture_fit_rating INTEGER CHECK (culture_fit_rating >= 1 AND culture_fit_rating <= 10),
    problem_solving_rating INTEGER CHECK (problem_solving_rating >= 1 AND problem_solving_rating <= 10),
    strengths TEXT,
    concerns TEXT,
    qualitative_comments TEXT,
    recommendation VARCHAR(50), -- strong_hire, hire, consider, reject
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Recommendations Table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id INTEGER REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    overall_recommendation VARCHAR(50), -- strong_hire, consider, reject
    confidence_score DECIMAL(5,2), -- 0-100
    justification TEXT,
    key_strengths TEXT[],
    key_weaknesses TEXT[],
    suggested_next_steps TEXT,
    analysis_data JSONB, -- detailed breakdown
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Logs (for tracking agentic decisions)
CREATE TABLE IF NOT EXISTS system_logs (
    log_id SERIAL PRIMARY KEY,
    log_type VARCHAR(100), -- decision, action, error, info
    module VARCHAR(100), -- sourcing, matching, scheduling, evaluation
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_applications_job_id ON job_applications(job_id);
CREATE INDEX idx_applications_candidate_id ON job_applications(candidate_id);
CREATE INDEX idx_applications_status ON job_applications(status);
CREATE INDEX idx_interview_schedule_datetime ON interview_schedule(interview_datetime);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
