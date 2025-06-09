#!/bin/bash

CONTAINER_NAME="ngrok"
IMAGE_NAME="ngrok/ngrok:latest"

echo "Stopping container: $CONTAINER_NAME"
docker stop $CONTAINER_NAME

echo "Removing container: $CONTAINER_NAME"
docker rm $CONTAINER_NAME

# ngrok 이미지는 자주 업데이트 안 하니까 rmi는 선택사항
# echo "Removing image: $IMAGE_NAME"
# docker rmi -f $IMAGE_NAME

echo "Starting ngrok container with docker-compose"
docker-compose up -d ngrok

echo "Done."

docker logs -f $CONTAINER_NAME
