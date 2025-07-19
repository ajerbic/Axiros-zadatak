# CI/CD and Deployment Strategy for Microservices Architecture

## *Microservices Overview*

This project includes two independent microservices:

* Service1 - timestamp generator
* Service2 - timestamp formatter

## *Objective*

Your task is to evaluate, improve, and ensure the correctness and efficiency of both microservices and their associated Docker images. Specifically:

* Identify and correct any errors in the microservices or Docker configurations.
* Recommend and implement improvements related to structure, performance, maintainability, and best practices.
* Provide any additional insights or observations relevant to the services’ quality or design.

## Continuous Integration and Delivery (CI/CD)

Design and implement a CI/CD pipeline that performs the following steps:

1. *Versioning*: Automatically assign version tags to each microservice.
2. *Build*: Build Docker images for both services.
3. *Testing*: Execute test suites (unit tests, integration tests, etc.).
4. *Publishing*: Push the Docker images to a container registry (e.g., Docker Hub or a local archive).

Note: You are not required to implement actual tests, but include the necessary steps and placeholders in the pipeline.

## Continuous Deployment

Create a deployment script (using Bash or Python) that launches both microservices in Docker with the specified versions and configurable parameters.

Example usage:

```bash
> ./deploy --version_service1=v1.0 --version_service2=v1.0 --additional_param_1=5
```

This script should:

* Pull and run the specified versions of each service.
* Ensure the services are accessible locally and communicate correctly via Docker.

## (Optional) Kubernetes deployment

For local Kubernetes environments (e.g., Minikube, Docker Desktop):

1. Define Kubernetes manifests (YAML) for both microservices.
2. Deploy the services using kubectl apply.
3. Create Helm charts for each microservice to support reusable and configurable deployments.
4. Develop automation scripts that deploy the services via both raw manifests and Helm, using a CLI interface similar to the Docker deployment script above.

## Deliverables

* Optimized Docker Images:
  * Lightweight, secure, and production-ready Dockerfiles for each microservice.

* CI/CD Pipeline:
  * Robust, maintainable workflows that support automated building, testing, versioning, and publishing.

* Deployment Automation:
  * Simple and configurable Docker-based deployment of both services.

* (Optional) Kubernetes Support:
  * YAML manifests and Helm charts for deploying the services on Kubernetes.
  * Scripts for automating deployment to a local Kubernetes cluster.

## Guidance and Tools

* Docker images may be stored using Docker Hub, .tar.gz archives, or any suitable method.
* While functionality correctness is secondary, the solution will be evaluated based on:
  * Service communication and integration
  * Configurability and flexibility
  * Maintainability and ease of updates
  * Deployment speed and simplicity
  * Docker image quality and optimization
  * Pipeline reliability and clarity
* (optional) Each service should be a kubernetes deployment, and can include services/ingress/other kubernetes components

* Preferred tools and technologies include:
  * Docker
  * Kubernetes (Minikube, Docker Desktop, etc.)
  * Git
  * Python/bash
