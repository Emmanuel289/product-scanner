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

# LocalStack vs real AWS mode
if [ "${AWS_MODE:-}" = "local" ]; then
    echo "Running in LocalStack mode..."
    LOCALSTACK_ENDPOINT="http://localhost:4566"
    LAMBDA_REPOSITORY_URL="localhost:4566/$(basename "$REPO_URL")"
    ECR_REGISTRY=$(echo "$REPO_URL" | cut -d'/' -f1)

    # Use awslocal if available, otherwise fall back to aws --endpoint-url
    if command -v awslocal &> /dev/null; then
        AWS_CMD="awslocal"
    else
        AWS_CMD="aws --endpoint-url=$LOCALSTACK_ENDPOINT"
    fi

    echo "Login to LocalStack ECR..."
    $AWS_CMD ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_REGISTRY"
else
    echo "Running in AWS mode..."
    LAMBDA_REPOSITORY_URL="${REPO_URL}"
    AWS_CMD="aws"

    echo "Login to AWS ECR..."
    $AWS_CMD ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$LAMBDA_REPOSITORY_URL"
fi

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
