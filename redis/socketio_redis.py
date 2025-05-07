import socketio
import eventlet
import os
from redis.cluster import RedisCluster

# 創建 SocketIO 服務器
sio = socketio.Server(
    async_mode='eventlet',
    cors_allowed_origins='*',
    message_queue=f'redis://:{os.getenv("REDIS_PASSWORD")}@localhost:6379/0'
)

# 創建 WSGI 應用
app = socketio.WSGIApp(sio)

# Redis Cluster 配置
startup_nodes = [
    {"host": "localhost", "port": 6379},
    {"host": "localhost", "port": 6380},
    {"host": "localhost", "port": 6381}
]

# 創建 Redis Cluster 客戶端
redis_client = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=True,
    password=os.getenv('REDIS_PASSWORD', 'your_secure_password')
)

# 連接事件處理
@sio.event
def connect(sid, environ):
    print(f'Client connected: {sid}')
    # 將用戶加入房間
    sio.enter_room(sid, 'general')
    # 發送歡迎消息
    sio.emit('message', {'data': f'Welcome! Your session ID is {sid}'}, room=sid)

# 斷開連接事件處理
@sio.event
def disconnect(sid):
    print(f'Client disconnected: {sid}')
    # 將用戶從房間移除
    sio.leave_room(sid, 'general')

# 消息事件處理
@sio.event
def message(sid, data):
    print(f'Message from {sid}: {data}')
    # 廣播消息到所有客戶端
    sio.emit('message', {'data': data}, room='general')
    # 將消息存儲到 Redis
    redis_client.lpush('chat_messages', str(data))
    # 保持最近 100 條消息
    redis_client.ltrim('chat_messages', 0, 99)

# 加入房間事件處理
@sio.event
def join_room(sid, data):
    room = data.get('room')
    if room:
        sio.enter_room(sid, room)
        sio.emit('message', {'data': f'Joined room: {room}'}, room=sid)

# 離開房間事件處理
@sio.event
def leave_room(sid, data):
    room = data.get('room')
    if room:
        sio.leave_room(sid, room)
        sio.emit('message', {'data': f'Left room: {room}'}, room=sid)

# 獲取歷史消息
@sio.event
def get_history(sid, data):
    count = data.get('count', 10)
    messages = redis_client.lrange('chat_messages', 0, count-1)
    sio.emit('history', {'messages': messages}, room=sid)

if __name__ == '__main__':
    # 使用 eventlet 運行服務器
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app) 