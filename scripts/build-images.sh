#!/bin/bash

# Build and tag Docker images for MLN131 Chatbot services
# Usage: ./scripts/build-images.sh [push]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Registry configuration
REGISTRY="mln131"
VERSION="latest"

# Services to build
SERVICES=("postgres" "python-ai" "dotnet-api" "nodejs-api" "frontend")

echo -e "${GREEN}Building Docker images for MLN131 Chatbot services...${NC}"

# Function to build image
build_image() {
    local service=$1
    local context=""
    local dockerfile=""
    
    case $service in
        "postgres")
            context="./database"
            dockerfile="Dockerfile"
            ;;
        "python-ai")
            context="./backend"
            dockerfile="Dockerfile"
            ;;
        "dotnet-api")
            context="./dotnet-api"
            dockerfile="Dockerfile"
            ;;
        "nodejs-api")
            context="./nodejs-api"
            dockerfile="Dockerfile"
            ;;
        "frontend")
            context="./frontend"
            dockerfile="Dockerfile"
            ;;
    esac
    
    echo -e "${YELLOW}Building $service image...${NC}"
    docker build -t "$REGISTRY/$service:$VERSION" -f "$context/$dockerfile" "$context"
    echo -e "${GREEN}✓ $service image built successfully${NC}"
}

# Function to push image
push_image() {
    local service=$1
    echo -e "${YELLOW}Pushing $service image...${NC}"
    docker push "$REGISTRY/$service:$VERSION"
    echo -e "${GREEN}✓ $service image pushed successfully${NC}"
}

# Build all images
for service in "${SERVICES[@]}"; do
    build_image "$service"
done

echo -e "${GREEN}All images built successfully!${NC}"

# Push images if argument is provided
if [ "$1" = "push" ]; then
    echo -e "${YELLOW}Pushing images to registry...${NC}"
    for service in "${SERVICES[@]}"; do
        push_image "$service"
    done
    echo -e "${GREEN}All images pushed successfully!${NC}"
fi

echo -e "${GREEN}Done!${NC}"

