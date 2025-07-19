#!/bin/bash

# Set versions (change as needed)
VERSION1="v1.0"
VERSION2="v1.0"

DOCKER_USER="ajerbic"

# Build images
echo "Building service1..."
docker build -t $DOCKER_USER/service1:$VERSION1 ./service1

echo "Building service2..."
docker build -t $DOCKER_USER/service2:$VERSION2 ./service2

# Optional: push images to Docker Hub
# echo "Pushing service1..."
# docker push $DOCKER_USER/service1:$VERSION1
# echo "Pushing service2..."
# docker push $DOCKER_USER/service2:$VERSION2

# Create network if not exists
docker network create microservices-net 2>/dev/null || true

# Stop & remove existing containers (if any)
docker stop service1 service2 2>/dev/null || true

# Run containers
echo "Starting service1..."
docker run -d --rm --name service1 --network microservices-net -p 8081:8080 $DOCKER_USER/service1:$VERSION1

echo "Starting service2..."
docker run -d --rm --name service2 --network microservices-net -p 8082:8080 $DOCKER_USER/service2:$VERSION2

echo "Services are running. Access:"
echo " - Service1: http://localhost:8081"
echo " - Service2: http://localhost:8082"
