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

## License
This project is licensed under the MIT License.