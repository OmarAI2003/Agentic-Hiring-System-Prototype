"""
Utility functions for the HR Recruitment System
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# Ensure logs directory exists before configuring logging
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_decision(module: str, description: str, metadata: Dict = None):
    """Log an agentic AI decision"""
    from database.models import SystemLog, get_session
    
    logger = get_logger(module)
    logger.info(f"DECISION: {description}")
    
    try:
        session = get_session()
        log_entry = SystemLog(
            log_type='decision',
            module=module,
            description=description,
            log_metadata=metadata or {}  # Updated field name
        )
        session.add(log_entry)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Failed to log decision: {str(e)}")


def log_action(module: str, description: str, metadata: Dict = None):
    """Log a system action"""
    from database.models import SystemLog, get_session
    
    logger = get_logger(module)
    logger.info(f"ACTION: {description}")
    
    try:
        session = get_session()
        log_entry = SystemLog(
            log_type='action',
            module=module,
            description=description,
            log_metadata=metadata or {}  # Updated field name
        )
        session.add(log_entry)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Failed to log action: {str(e)}")


def save_json(data: Any, filepath: str):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: str) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'logs',
        'data/candidates',
        'data/jobs',
        'reports',
        'config'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def calculate_percentage_match(required: List[str], candidate: List[str]) -> float:
    """
    Calculate percentage match between required and candidate skills/attributes
    Returns value between 0 and 100
    """
    if not required:
        return 100.0
    
    required_set = set([item.lower().strip() for item in required])
    candidate_set = set([item.lower().strip() for item in candidate])
    
    matches = required_set.intersection(candidate_set)
    return (len(matches) / len(required_set)) * 100


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    return text.lower().strip()


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value from environment"""
    return os.getenv(key, default)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_skills_list(skills_str: str) -> List[str]:
    """Parse comma-separated skills string into list"""
    if not skills_str:
        return []
    return [skill.strip() for skill in skills_str.split(',') if skill.strip()]


class ConfigManager:
    """Configuration manager for the application"""
    
    @staticmethod
    def get_ollama_config() -> Dict[str, str]:
        """Get Ollama configuration"""
        return {
            'host': get_config('OLLAMA_HOST', 'http://localhost:11434'),
            'model': get_config('OLLAMA_MODEL', 'llama3')
        }
    
    @staticmethod
    def get_db_config() -> Dict[str, str]:
        """Get database configuration"""
        return {
            'host': get_config('DB_HOST', 'localhost'),
            'port': get_config('DB_PORT', '5432'),
            'name': get_config('DB_NAME', 'hr_recruitment'),
            'user': get_config('DB_USER', 'postgres'),
            'password': get_config('DB_PASSWORD', '')
        }
    
    @staticmethod
    def is_mock_data_enabled() -> bool:
        """Check if mock data generation is enabled"""
        return get_config('MOCK_DATA_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def get_candidate_pool_size() -> int:
        """Get candidate pool size for mock data"""
        return int(get_config('CANDIDATE_POOL_SIZE', '100'))
    
    @staticmethod
    def get_top_candidates_count() -> int:
        """Get number of top candidates to shortlist"""
        return int(get_config('TOP_CANDIDATES_COUNT', '10'))


if __name__ == '__main__':
    # Test utilities
    ensure_directories()
    print("Utilities module initialized successfully!")
