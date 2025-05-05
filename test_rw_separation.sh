#!/bin/bash

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== 開始測試讀寫分離 ==="

# 1. 測試寫入連接（主節點）
echo -e "\n${GREEN}1. 測試寫入連接 (端口 5000)${NC}"
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5000 -U postgres << EOF
CREATE DATABASE test_rw;
\c test_rw
CREATE TABLE test_table (id serial PRIMARY KEY, data text);
INSERT INTO test_table (data) VALUES ('test data');
SELECT * FROM test_table;
EOF

# 2. 測試讀取連接（備節點）
echo -e "\n${GREEN}2. 測試讀取連接 (端口 5001)${NC}"
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5001 -U postgres << EOF
\c test_rw
SELECT * FROM test_table;
EOF

# 3. 測試備節點寫入（應該失敗）
echo -e "\n${GREEN}3. 測試備節點寫入 (應該失敗)${NC}"
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5001 -U postgres << EOF
\c test_rw
INSERT INTO test_table (data) VALUES ('should fail');
EOF

# 4. 檢查節點狀態
echo -e "\n${GREEN}4. 檢查節點狀態${NC}"
echo "主節點狀態："
curl -s http://localhost:8009/master | jq .
echo "備節點狀態："
curl -s http://localhost:8009/replica | jq .

# 5. 清理測試數據
echo -e "\n${GREEN}5. 清理測試數據${NC}"
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -p 5000 -U postgres << EOF
DROP DATABASE test_rw;
EOF

echo -e "\n=== 測試完成 ===" 