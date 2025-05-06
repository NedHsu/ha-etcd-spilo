#!/bin/bash

# 等待 Redis 節點就緒
echo "Waiting for Redis nodes to be ready..."
sleep 10

# 檢查 Redis 節點是否可訪問
for node in redis-node1 redis-node2 redis-node3; do
    until redis-cli -h $node -p 6379 -a "${REDIS_PASSWORD}" ping > /dev/null 2>&1; do
        echo "Waiting for Redis node $node..."
        sleep 1
    done
done

echo "All Redis nodes are ready!"

# 創建 Redis Cluster
echo "Creating Redis Cluster..."
redis-cli -a "${REDIS_PASSWORD}" --cluster create \
    redis-node1:6379 \
    redis-node2:6379 \
    redis-node3:6379 \
    --cluster-replicas 0 \
    --cluster-yes

echo "Redis Cluster initialization completed!" 