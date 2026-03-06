#!/bin/bash
# Deploy to staging environment
set -e

IMAGE_TAG=${1:-latest}
echo "Deploying CareBuddy (tag: $IMAGE_TAG) to staging..."

# Pull latest images
docker compose -f docker-compose.yml pull

# Restart services
docker compose -f docker-compose.yml up -d --build

echo "Staging deployment complete!"
echo "Backend:  http://staging:8000/health"
echo "Frontend: http://staging:80"
