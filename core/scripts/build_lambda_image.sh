#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOCKERFILE_DIR="$SCRIPT_DIR/../"
DOCKERFILE_PATH="$DOCKERFILE_DIR/Dockerfile"

if [ -z "${REPO_URL:-}" ] || [ -z "${IMAGE_TAG:-}" ] || [ -z "${AWS_REGION:-}" ]; then
    echo "Error: Missing required env variables (REPO_URL, IMAGE_TAG, AWS_REGION)"
    exit 1
fi

AWS_REGION="${AWS_REGION}"
IMAGE_TAG="${IMAGE_TAG}"

# Login to ECR
LAMBDA_REPOSITORY_URL="${REPO_URL}"
AWS_CMD="aws"
echo "Login to AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$LAMBDA_REPOSITORY_URL"

echo "Building lambda image..."
docker build -t "$REPO_URL:$IMAGE_TAG" \
    --platform linux/amd64 \
    --provenance false \
    --no-cache \
    -f "$DOCKERFILE_PATH" "$DOCKERFILE_DIR"

echo "Pushing image to ECR repository..."
docker push "$REPO_URL:$IMAGE_TAG"

echo "Verifying image in ECR..."
REPO_NAME=$(basename "$LAMBDA_REPOSITORY_URL")
$AWS_CMD ecr describe-images \
    --repository-name "$REPO_NAME" \
    --image-ids imageTag="$IMAGE_TAG" \
    --region "$AWS_REGION" \
    || {
        echo "Image not found yet, retrying..."
        sleep 5
        $AWS_CMD ecr describe-images \
            --repository-name "$REPO_NAME" \
            --image-ids imageTag="$IMAGE_TAG" \
            --region "$AWS_REGION"
    }

echo "✅ Done! Image available at $LAMBDA_REPOSITORY_URL:$IMAGE_TAG"
