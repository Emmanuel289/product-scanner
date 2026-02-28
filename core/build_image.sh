#! /bin/sh
LAMBDA_IMAGE_NAME=${LAMBDA_IMAGE_NAME:-"test-image"}
LAMBDA_IMAGE_TAG=${LAMBDA_IMAGE_TAG:-"latest"}

docker build \
    --tag ${LAMBDA_IMAGE_NAME}:${LAMBDA_IMAGE_TAG} \
    --platform linux/amd64 \
    --provenance false \
    --no-cache \
    -f Dockerfile .

CONTAINER_ID=$(docker run -it -d ${LAMBDA_IMAGE_NAME}:${LAMBDA_IMAGE_TAG})
docker exec -it $CONTAINER_ID sh
