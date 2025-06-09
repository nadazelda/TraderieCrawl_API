#!/bin/bash
FASTAPI_CONTAINER="fastapi_app"
CLOUDFLARED_CONTAINER="cloudflared"

echo "🔁 Stopping and removing existing containers..."
docker-compose down

echo "🧹 Removing existing images..."
docker stop $FASTAPI_CONTAINER $CLOUDFLARED_CONTAINER || true
docker rm $FASTAPI_CONTAINER $CLOUDFLARED_CONTAINER || true




# 1. cloudflared 컨테이너 실행 (백그라운드)
echo "🚀 Starting containers in detached mode..."
docker-compose up -d cloudflared

# 2. cloudflared 로그에서 터널 주소 잠깐 출력
sleep 3

echo "📡 Cloudflared logs:"
docker logs $CLOUDFLARED_CONTAINER --tail 20

# 2. cloudflared 로그에서 터널 주소 잠깐 출력
sleep 3
# 3. FastAPI 빌드 및 재시작 + 로그 출력 (cleanup_fastapi.sh가 처리)
# docker-compose.yml에서 의존성을 연결돼서 자동으로 빌드됨 
./cleanup_fastapi.sh




