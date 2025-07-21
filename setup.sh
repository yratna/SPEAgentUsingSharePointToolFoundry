#!/bin/bash

# SharePoint Tool Foundry - Setup Script
# This script helps set up the development environment and verify configuration

set -e  # Exit on any error

echo "🚀 SharePoint Tool Foundry - Setup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION found (minimum 3.8 required)"
    else
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded"

# Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        print_status "Copying .env.example to .env..."
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your actual Azure credentials"
        echo ""
        echo "Required environment variables:"
        echo "  - PROJECT_ENDPOINT: Your Azure AI Foundry project endpoint"
        echo "  - SHAREPOINT_RESOURCE_NAME: Your SharePoint connection name"
        echo "  - MODEL_DEPLOYMENT_NAME: Your model deployment name"
        echo ""
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
else
    print_success ".env file found"
fi

# Verify environment variables
print_status "Checking environment variables..."
source .env 2>/dev/null || true

MISSING_VARS=()
if [ -z "$PROJECT_ENDPOINT" ]; then
    MISSING_VARS+=("PROJECT_ENDPOINT")
fi
if [ -z "$SHAREPOINT_RESOURCE_NAME" ]; then
    MISSING_VARS+=("SHAREPOINT_RESOURCE_NAME")
fi
if [ -z "$MODEL_DEPLOYMENT_NAME" ]; then
    MISSING_VARS+=("MODEL_DEPLOYMENT_NAME")
fi

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    print_success "All required environment variables are set"
else
    print_warning "Missing environment variables: ${MISSING_VARS[*]}"
    print_warning "Please update your .env file with the correct values"
fi

# Run tests
print_status "Running tests..."
if command -v pytest &> /dev/null; then
    if python -m pytest test_sharepoint_agent.py -v; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Check the output above."
    fi
else
    print_warning "pytest not found. Installing pytest..."
    pip install pytest pytest-mock
    if python -m pytest test_sharepoint_agent.py -v; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Check the output above."
    fi
fi

# Check Azure CLI (optional)
if command -v az &> /dev/null; then
    print_success "Azure CLI found"
    if az account show &> /dev/null; then
        ACCOUNT=$(az account show --query "name" -o tsv)
        print_success "Logged into Azure account: $ACCOUNT"
    else
        print_warning "Not logged into Azure CLI. Run 'az login' if needed."
    fi
else
    print_warning "Azure CLI not found. This is optional but recommended."
fi

echo ""
print_success "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Update .env file with your Azure credentials (if not done already)"
echo "2. Run the agent: python sharepoint_agent.py"
echo "3. Or use interactive mode: python interactive_cli.py"
echo "4. Or see examples: python examples.py"
echo ""
echo "For help, check the README.md file."
