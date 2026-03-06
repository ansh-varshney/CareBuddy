#!/bin/bash
# Deploy to production environment
set -e

IMAGE_TAG=${1:-latest}
echo "Deploying CareBuddy (tag: $IMAGE_TAG) to PRODUCTION..."

# Pull latest images
docker compose -f docker-compose.yml pull

# Rolling restart
docker compose -f docker-compose.yml up -d --build --remove-orphans

echo "Production deployment complete!"
