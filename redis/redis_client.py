from redis.cluster import RedisCluster
import os

def create_redis_cluster_client():
    """
    創建 Redis Cluster 客戶端
    """
    # Redis 節點配置
    startup_nodes = [
        {"host": "localhost", "port": 6379},
        {"host": "localhost", "port": 6380},
        {"host": "localhost", "port": 6381}
    ]

    # 創建 Redis Cluster 客戶端
    redis_client = RedisCluster(
        startup_nodes=startup_nodes,
        decode_responses=True,  # 自動將響應解碼為字符串
        password=os.getenv('REDIS_PASSWORD', 'your_secure_password')  # 使用環境變量中的密碼
    )
    
    return redis_client

def test_redis_connection():
    """
    測試 Redis 連接和基本操作
    """
    try:
        # 創建客戶端
        redis_client = create_redis_cluster_client()
        
        # 測試連接
        print("Testing Redis connection...")
        redis_client.ping()
        print("Connection successful!")
        
        # 基本操作示例
        print("\nTesting basic operations:")
        
        # 設置值
        redis_client.set("test_key", "Hello Redis Cluster!")
        print("Set value: test_key -> Hello Redis Cluster!")
        
        # 獲取值
        value = redis_client.get("test_key")
        print(f"Get value: test_key -> {value}")
        
        # 刪除值
        redis_client.delete("test_key")
        print("Deleted test_key")
        
        # 檢查是否刪除成功
        value = redis_client.get("test_key")
        print(f"After deletion: test_key -> {value}")
        
        # 使用哈希表
        print("\nTesting hash operations:")
        redis_client.hset("user:1", mapping={
            "name": "John",
            "email": "john@example.com",
            "age": "30"
        })
        print("Created hash: user:1")
        
        # 獲取哈希表所有字段
        user_data = redis_client.hgetall("user:1")
        print(f"User data: {user_data}")
        
        # 使用列表
        print("\nTesting list operations:")
        redis_client.lpush("my_list", "item1", "item2", "item3")
        print("Created list: my_list")
        
        # 獲取列表範圍
        list_items = redis_client.lrange("my_list", 0, -1)
        print(f"List items: {list_items}")
        
        # 清理測試數據
        redis_client.delete("user:1", "my_list")
        print("\nCleaned up test data")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_redis_connection() 