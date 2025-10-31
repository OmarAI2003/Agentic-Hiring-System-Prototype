#!/bin/bash
# Database Setup Script - Initializes schema and tables

echo "=========================================="
echo "Database Schema Setup"
echo "=========================================="
echo ""

PROJECT_DIR="/c/Users/A/Agentic-Hiring-System-Prototype"
SCHEMA_FILE="$PROJECT_DIR/database/schema.sql"
DB_NAME="hr_recruitment"

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Error: schema.sql not found at $SCHEMA_FILE"
    exit 1
fi

echo "Database: $DB_NAME"
echo "Schema file: $SCHEMA_FILE"
echo ""

# Function to setup database based on environment
setup_database() {
    local method=$1
    
    case $method in
        docker)
            echo "🐳 Setting up database via Docker..."
            docker exec -i postgres-hr psql -U postgres -d $DB_NAME < "$SCHEMA_FILE"
            ;;
        local)
            echo "💻 Setting up database locally..."
            
            # Try different connection methods
            if command -v psql &> /dev/null; then
                # Standard PostgreSQL
                psql -U postgres -d $DB_NAME < "$SCHEMA_FILE"
            elif [ -f "/Program Files/PostgreSQL/15/bin/psql.exe" ]; then
                # Windows PostgreSQL
                "/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -d $DB_NAME < "$SCHEMA_FILE"
            else
                echo "❌ Cannot find psql. Please run manually:"
                echo "   psql -U postgres -d $DB_NAME < $SCHEMA_FILE"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unknown method: $method"
            exit 1
            ;;
    esac
}

# Detect setup method
echo "Detecting PostgreSQL setup..."
if docker ps | grep -q postgres-hr; then
    echo "✓ Found Docker container 'postgres-hr'"
    setup_database docker
elif command -v psql &> /dev/null || [ -f "/Program Files/PostgreSQL/15/bin/psql.exe" ]; then
    echo "✓ Found local PostgreSQL installation"
    setup_database local
else
    echo ""
    echo "⚠️  Cannot detect PostgreSQL. Please choose:"
    echo ""
    echo "1. Using Docker? Run:"
    echo "   docker exec -i postgres-hr psql -U postgres -d $DB_NAME < $SCHEMA_FILE"
    echo ""
    echo "2. Using local PostgreSQL? Run:"
    echo "   psql -U postgres -d $DB_NAME < $SCHEMA_FILE"
    echo ""
    exit 1
fi

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database schema initialized successfully!"
    echo ""
    echo "Tables created:"
    echo "  - jobs"
    echo "  - candidates"
    echo "  - job_applications"
    echo "  - interview_questions"
    echo "  - interview_schedule"
    echo "  - interview_feedback"
    echo "  - ai_recommendations"
    echo "  - system_logs"
    echo ""
    
    # Test connection from Python
    echo "Testing database connection from Python..."
    cd "$PROJECT_DIR"
    python << 'EOF'
import os
os.environ['SKIP_DB_LOGGING'] = '0'  # Enable DB logging

try:
    from database.models import get_session, Job
    
    session = get_session()
    
    # Test query
    count = session.query(Job).count()
    print(f"✅ Database connection successful!")
    print(f"   Jobs table accessible (current count: {count})")
    
    session.close()
except Exception as e:
    print(f"⚠️  Database connection issue: {str(e)}")
    print(f"   Check your .env settings:")
    print(f"   - DB_NAME={os.getenv('DB_NAME', 'hr_recruitment')}")
    print(f"   - DB_USER={os.getenv('DB_USER', 'postgres')}")
    print(f"   - DB_HOST={os.getenv('DB_HOST', 'localhost')}")
    print(f"   - DB_PORT={os.getenv('DB_PORT', '5432')}")
EOF
    
else
    echo ""
    echo "❌ Database setup failed!"
    echo ""
    echo "Common issues:"
    echo "  - Wrong password in .env file"
    echo "  - PostgreSQL not running"
    echo "  - Database '$DB_NAME' doesn't exist"
    echo ""
    echo "To create database manually:"
    echo "  createdb $DB_NAME"
    echo "  # OR via Docker:"
    echo "  docker exec postgres-hr createdb -U postgres $DB_NAME"
    exit 1
fi

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Update .env with correct credentials"
echo "2. Remove SKIP_DB_LOGGING from test scripts"
echo "3. Run tests with database enabled"
echo ""
