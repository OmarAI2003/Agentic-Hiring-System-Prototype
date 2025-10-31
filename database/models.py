"""
SQLAlchemy ORM Models for HR Recruitment System
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, TIMESTAMP, 
    DECIMAL, ARRAY, JSON, ForeignKey, CheckConstraint, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Job(Base):
    __tablename__ = 'jobs'
    
    job_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(ARRAY(Text), nullable=False)
    experience_level = Column(String(50), nullable=False)
    location = Column(String(255))
    employment_type = Column(String(50))
    salary_range = Column(String(100))
    department = Column(String(100))
    posted_date = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(50), default='active')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship('JobApplication', back_populates='job', cascade='all, delete-orphan')
    interview_questions = relationship('InterviewQuestion', back_populates='job', cascade='all, delete-orphan')
    interview_schedules = relationship('InterviewSchedule', back_populates='job', cascade='all, delete-orphan')
    ai_recommendations = relationship('AIRecommendation', back_populates='job', cascade='all, delete-orphan')


class Candidate(Base):
    __tablename__ = 'candidates'
    
    candidate_id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    location = Column(String(255))
    age = Column(Integer)
    nationality = Column(String(100))
    marital_status = Column(String(50))
    visa_status = Column(String(100))
    linkedin_url = Column(Text)
    github_url = Column(Text)
    portfolio_url = Column(Text)
    resume_url = Column(Text)
    skills = Column(ARRAY(Text))
    experience_years = Column(Integer)
    current_position = Column(String(255))
    education = Column(Text)
    availability_date = Column(Date)
    preferred_interview_times = Column(JSON)
    source = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship('JobApplication', back_populates='candidate', cascade='all, delete-orphan')
    interview_schedules = relationship('InterviewSchedule', back_populates='candidate', cascade='all, delete-orphan')
    ai_recommendations = relationship('AIRecommendation', back_populates='candidate', cascade='all, delete-orphan')


class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    application_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete='CASCADE'))
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id', ondelete='CASCADE'))
    application_date = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(50), default='applied')
    match_score = Column(DECIMAL(5, 2))
    match_details = Column(JSON)
    ranking = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship('Job', back_populates='applications')
    candidate = relationship('Candidate', back_populates='applications')


class InterviewQuestion(Base):
    __tablename__ = 'interview_questions'
    
    question_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete='CASCADE'))
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id', ondelete='CASCADE'))
    question_text = Column(Text, nullable=False)
    category = Column(String(100))
    difficulty = Column(String(50))
    expected_answer = Column(Text)
    evaluation_criteria = Column(Text)
    generated_by = Column(String(50), default='ai')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    job = relationship('Job', back_populates='interview_questions')


class InterviewSchedule(Base):
    __tablename__ = 'interview_schedule'
    
    interview_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete='CASCADE'))
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id', ondelete='CASCADE'))
    interviewer_email = Column(String(255), nullable=False)
    interview_datetime = Column(TIMESTAMP, nullable=False)
    duration_minutes = Column(Integer, default=60)
    meeting_link = Column(Text)
    calendar_event_id = Column(String(255))
    status = Column(String(50), default='scheduled')
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship('Job', back_populates='interview_schedules')
    candidate = relationship('Candidate', back_populates='interview_schedules')
    feedback = relationship('InterviewFeedback', back_populates='interview', cascade='all, delete-orphan')


class InterviewFeedback(Base):
    __tablename__ = 'interview_feedback'
    
    feedback_id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey('interview_schedule.interview_id', ondelete='CASCADE'))
    interviewer_email = Column(String(255), nullable=False)
    technical_skills_rating = Column(Integer, CheckConstraint('technical_skills_rating >= 1 AND technical_skills_rating <= 10'))
    communication_skills_rating = Column(Integer, CheckConstraint('communication_skills_rating >= 1 AND communication_skills_rating <= 10'))
    culture_fit_rating = Column(Integer, CheckConstraint('culture_fit_rating >= 1 AND culture_fit_rating <= 10'))
    problem_solving_rating = Column(Integer, CheckConstraint('problem_solving_rating >= 1 AND problem_solving_rating <= 10'))
    strengths = Column(Text)
    concerns = Column(Text)
    qualitative_comments = Column(Text)
    recommendation = Column(String(50))
    submitted_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    interview = relationship('InterviewSchedule', back_populates='feedback')


class AIRecommendation(Base):
    __tablename__ = 'ai_recommendations'
    
    recommendation_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete='CASCADE'))
    candidate_id = Column(Integer, ForeignKey('candidates.candidate_id', ondelete='CASCADE'))
    overall_recommendation = Column(String(50))
    confidence_score = Column(DECIMAL(5, 2))
    justification = Column(Text)
    key_strengths = Column(ARRAY(Text))
    key_weaknesses = Column(ARRAY(Text))
    suggested_next_steps = Column(Text)
    analysis_data = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    job = relationship('Job', back_populates='ai_recommendations')
    candidate = relationship('Candidate', back_populates='ai_recommendations')


class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    log_id = Column(Integer, primary_key=True)
    log_type = Column(String(100))
    module = Column(String(100))
    description = Column(Text)
    log_metadata = Column('metadata', JSON)  # Renamed to avoid SQLAlchemy conflict
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# Database connection and session management
def get_database_url():
    """Construct database URL from environment variables"""
    return f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


def create_db_engine():
    """Create SQLAlchemy engine"""
    return create_engine(get_database_url(), echo=False)


def get_session():
    """Get database session"""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize database tables"""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")


if __name__ == '__main__':
    init_database()
