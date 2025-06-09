#!/bin/bash

CONTAINER_NAME="fastapi_app"
IMAGE_NAME="traderiealarm_fastapi"

echo "Stopping container: $CONTAINER_NAME"
docker stop $CONTAINER_NAME

echo "Removing container: $CONTAINER_NAME"
docker rm $CONTAINER_NAME

echo "Removing image: $IMAGE_NAME"
docker rmi -f $IMAGE_NAME

echo "Rebuilding and starting container with docker-compose"
docker-compose up -d fastapi

echo "Done."
docker logs cloudflared_quick

#docker logs -f $CONTAINER_NAME