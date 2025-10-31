# Setup Script for Agentic HR Recruitment System

echo "=========================================="
echo "Agentic HR Recruitment System - Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python --version

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if Ollama is installed
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null
then
    echo "✓ Ollama is installed"
    echo "Pulling Llama 3 model..."
    ollama pull llama3
else
    echo "✗ Ollama not found"
    echo "Please install Ollama from: https://ollama.ai"
    echo "Then run: ollama pull llama3"
fi

# Check PostgreSQL
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null
then
    echo "✓ PostgreSQL is installed"
else
    echo "✗ PostgreSQL not found"
    echo "Please install PostgreSQL"
fi

# Create directories
echo "Creating required directories..."
python -c "from python.utils.helpers import ensure_directories; ensure_directories()"

# Initialize database
echo "Would you like to initialize the database? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "Initializing database..."
    python -c "from database.models import init_database; init_database()"
    echo "✓ Database initialized"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure"
echo "2. Ensure Ollama is running: ollama serve"
echo "3. Start PostgreSQL database"
echo "4. Run Phase 1: python -m python.sourcing.main"
echo ""
echo "For n8n workflows:"
echo "1. Install n8n: npm install -g n8n"
echo "2. Start n8n: n8n"
echo "3. Import workflows from n8n_workflows/"
echo ""
