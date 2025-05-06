#!/bin/bash

# 檢測操作系統
if [[ "$OSTYPE" == "msys" ]]; then
    # Windows with Git Bash
    REDIS_CLI="redis-cli.exe"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    REDIS_CLI="redis-cli"
else
    # Linux
    REDIS_CLI="redis-cli"
fi

# 檢查 redis-cli 是否可用
if ! command -v $REDIS_CLI &> /dev/null; then
    echo "Error: $REDIS_CLI is not installed or not in PATH"
    echo "Please install Redis client tools first"
    exit 1
fi

# 等待 Redis 節點就緒
echo "Waiting for Redis nodes to be ready..."
sleep 10

# 檢查 Redis 節點是否可訪問
for port in 6379 6380 6381; do
    until $REDIS_CLI -h localhost -p $port -a "${REDIS_PASSWORD}" ping > /dev/null 2>&1; do
        echo "Waiting for Redis node on port $port..."
        sleep 1
    done
done

echo "All Redis nodes are ready!"

# 創建 Redis Cluster
echo "Creating Redis Cluster..."
$REDIS_CLI -a "${REDIS_PASSWORD}" --cluster create \
    localhost:6379 \
    localhost:6380 \
    localhost:6381 \
    --cluster-replicas 0 \
    --cluster-yes

echo "Redis Cluster initialization completed!" 