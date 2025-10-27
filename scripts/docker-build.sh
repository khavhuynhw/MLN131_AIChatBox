#!/bin/bash

# HCM Chatbot - Docker Build Script
# Build all Docker images for the project

set -e

echo "🐳 Building HCM Chatbot Docker Images..."

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build Python AI Backend
print_status "Building Python AI Backend..."
if docker build -t hcm-python-ai:latest ./backend; then
    print_success "Python AI Backend built successfully"
else
    print_error "Failed to build Python AI Backend"
    exit 1
fi

# Build .NET API
print_status "Building .NET API..."
if docker build -t hcm-dotnet-api:latest ./dotnet-api/hcm-chatbot-api; then
    print_success ".NET API built successfully"
else
    print_error "Failed to build .NET API"
    exit 1
fi

# Build Node.js API
print_status "Building Node.js API..."
if docker build -t hcm-nodejs-api:latest ./nodejs-api; then
    print_success "Node.js API built successfully"
else
    print_error "Failed to build Node.js API"
    exit 1
fi

# Build Frontend
print_status "Building Frontend..."
if docker build -t hcm-frontend:latest ./frontend; then
    print_success "Frontend built successfully"
else
    print_error "Failed to build Frontend"
    exit 1
fi

print_success "All Docker images built successfully! 🎉"
echo ""
echo "Available images:"
docker images | grep hcm-

echo ""
echo "To run the application:"
echo "  docker-compose up -d"
echo ""
echo "To run in development mode:"
echo "  docker-compose -f docker-compose.dev.yml up -d"

