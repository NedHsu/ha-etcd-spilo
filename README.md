# Spilo PostgreSQL HA Cluster with Docker Compose

This project demonstrates how to deploy a highly available PostgreSQL cluster using **Spilo**, **etcd**, and **HAProxy** with **Docker Compose**. The setup includes:
- 3 PostgreSQL nodes managed by **Spilo** (with Patroni for clustering)
- 1 **etcd** instance for distributed consensus
- 1 **HAProxy** instance for load balancing

## Features
- Automatic failover and leader election with Patroni.
- Local filesystem backups using **WAL-G**.
- Load balancing of database connections via HAProxy.
- Configurable and scalable architecture.

---

## Directory Structure
```
.
├── docker-compose.yml     # Main configuration for Docker Compose
├── haproxy/
│   └── haproxy.cfg        # Configuration for HAProxy
└── backups/               # Local backup storage (mapped to host directory)
```

---

## Prerequisites
1. Install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
2. Ensure your system has at least 4 GB of RAM and sufficient disk space.

---

## Usage

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/spilo-cluster.git
cd spilo-cluster
```

### 2. Start the Cluster
Run the following command to start all services:
```bash
docker-compose up -d
```

### 3. Check the Status
- Verify all containers are running:
  ```bash
  docker ps
  ```
- Access Patroni REST API to check each node's status:
  - Node 1: [http://localhost:8009](http://localhost:8009)
  - Node 2: [http://localhost:8010](http://localhost:8010)
  - Node 3: [http://localhost:8011](http://localhost:8011)

### 4. Connect to the Database
Use `psql` or any PostgreSQL client to connect via HAProxy:
```bash
psql -h localhost -p 5000 -U admin -W
```
- Default username: `admin`
- Default password: `password`

---

## Backups and Restores

### Backup
Backups are stored in the `./backups/` directory on the host machine. To manually trigger a backup:
1. Enter any Spilo container:
   ```bash
   docker exec -it spilo-node1 bash
   ```
2. Run the following command:
   ```bash
   wal-g backup-push /home/postgres/pgdata
   ```

### Restore
To restore from a backup:
1. Stop the cluster:
   ```bash
   docker-compose down
   ```
2. Set restore environment variables in `docker-compose.yml` (e.g., `USE_WALG_RESTORE`).
3. Restart the cluster:
   ```bash
   docker-compose up -d
   ```

---

## HAProxy Configuration
The HAProxy configuration (`haproxy/haproxy.cfg`) routes requests to the PostgreSQL leader node. You can modify it to suit your requirements.

---

## Scaling the Cluster
To add more PostgreSQL nodes:
1. Duplicate a `spilo-node` service in `docker-compose.yml` and update the `PATRONI_NAME` and ports.
2. Restart the cluster:
   ```bash
   docker-compose up -d
   ```

---

## Troubleshooting
- **Check Logs**: View logs for any container:
  ```bash
  docker logs <container_name>
  ```
- **Cluster Health**: Visit the Patroni REST API endpoints to inspect the cluster state.

---


# HA-ETCD-SPILO with Redis Cluster

## 專案概述
本專案整合了 PostgreSQL 高可用集群（使用 Spilo）和 Redis Cluster，提供完整的數據庫解決方案。

## Redis Cluster 架構

### 架構設計
- 3 個 Redis 節點組成的集群
- 每個節點既是主節點也是從節點
- 自動數據分片和故障轉移
- 使用 Docker 容器化部署

### 端口配置
- Redis 客戶端端口：6379, 6380, 6381
- 集群總線端口：16379, 16380, 16381

### 數據分片
- 使用 16384 個哈希槽
- 自動分片到 3 個節點
- 支持動態擴展

## 快速開始

### 環境要求
- Docker 和 Docker Compose
- 至少 4GB 可用內存
- 至少 10GB 可用磁盤空間

### 配置環境變量
```bash
# Redis 密碼
export REDIS_PASSWORD=your_secure_password
```

### 啟動服務
```bash
# 啟動所有服務
docker-compose up -d

# 初始化 Redis Cluster
chmod +x redis/init-cluster.sh
./redis/init-cluster.sh
```

### 驗證集群狀態
```bash
# 連接到任意節點
redis-cli -h localhost -p 6379 -a your_secure_password

# 檢查集群狀態
redis-cli -h localhost -p 6379 -a your_secure_password cluster info

# 查看節點信息
redis-cli -h localhost -p 6379 -a your_secure_password cluster nodes
```

## Redis Cluster 使用指南

### 基本操作
```bash
# 連接到集群
redis-cli -h localhost -p 6379 -a your_secure_password

# 寫入數據
set key value

# 讀取數據
get key

# 刪除數據
del key
```

### 集群管理
```bash
# 查看集群信息
cluster info

# 查看節點信息
cluster nodes

# 手動故障轉移
cluster failover
```

### 監控與維護
```bash
# 查看內存使用情況
info memory

# 查看客戶端連接
client list

# 查看慢日誌
slowlog get
```

## 注意事項

### 使用限制
1. 不支持跨槽位的事務
2. 不支持跨槽位的 Lua 腳本
3. 某些命令可能不可用

### 最佳實踐
1. 合理設計鍵名，避免跨槽位操作
2. 定期監控集群狀態
3. 設置適當的內存限制
4. 定期備份數據

### 故障處理
1. 節點故障自動轉移
2. 手動故障轉移命令
3. 集群重組操作

## 性能優化

### 配置建議
1. 適當設置內存限制
2. 配置合理的超時時間
3. 啟用持久化
4. 調整網絡參數

### 監控指標
1. 內存使用率
2. 連接數
3. 命令執行時間
4. 網絡流量

## 安全建議

### 訪問控制
1. 使用強密碼
2. 限制網絡訪問
3. 定期更換密碼

### 數據安全
1. 啟用持久化
2. 定期備份
3. 加密敏感數據

## 故障排除

### 常見問題
1. 連接失敗
   - 檢查密碼是否正確
   - 確認端口是否開放
   - 驗證網絡連接

2. 集群狀態異常
   - 檢查節點狀態
   - 驗證配置正確性
   - 查看錯誤日誌

3. 性能問題
   - 檢查內存使用
   - 分析慢日誌
   - 優化配置參數

### 日誌查看
```bash
# 查看 Redis 日誌
docker logs redis-node1
docker logs redis-node2
docker logs redis-node3
```

## 擴展與維護

### 擴展集群
1. 添加新節點
2. 重新分片
3. 平衡負載

### 版本升級
1. 備份數據
2. 更新配置
3. 重啟服務

## 參考資源
- [Redis 官方文檔](https://redis.io/documentation)
- [Redis Cluster 規範](https://redis.io/topics/cluster-spec)
- [Docker Redis 文檔](https://hub.docker.com/_/redis)


## License
This project is licensed under the MIT License.