from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from redis.cluster import RedisCluster

# 創建 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

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

# 創建 SocketIO 實例，配置 Redis 消息隊列
socketio = SocketIO(
    app,
    message_queue=f'redis://:{os.getenv("REDIS_PASSWORD")}@localhost:6379/0',
    cors_allowed_origins='*'
)

# 路由：首頁
@app.route('/')
def index():
    return render_template('index.html')

# 路由：聊天室
@app.route('/room/<room>')
def room(room):
    return render_template('room.html', room=room)

# SocketIO 事件處理器
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room = data.get('room', 'general')
    join_room(room)
    emit('message', {'data': f'Joined room: {room}'}, room=room)
    
    # 獲取房間歷史消息
    messages = redis_client.lrange(f'room:{room}:messages', 0, 9)
    emit('history', {'messages': messages}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data.get('room', 'general')
    leave_room(room)
    emit('message', {'data': f'Left room: {room}'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data.get('room', 'general')
    message = data.get('message', '')
    
    # 廣播消息到房間
    emit('message', {'data': message}, room=room)
    
    # 存儲消息到 Redis
    redis_client.lpush(f'room:{room}:messages', message)
    redis_client.ltrim(f'room:{room}:messages', 0, 99)  # 保持最近 100 條消息

@socketio.on('get_history')
def handle_get_history(data):
    room = data.get('room', 'general')
    count = data.get('count', 10)
    
    # 從 Redis 獲取歷史消息
    messages = redis_client.lrange(f'room:{room}:messages', 0, count-1)
    emit('history', {'messages': messages})

# 創建 HTML 模板
@app.route('/templates')
def create_templates():
    # 創建 templates 目錄
    os.makedirs('templates', exist_ok=True)
    
    # 創建 index.html
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Rooms</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io();
            
            socket.on('connect', () => {
                console.log('Connected to server');
            });
            
            socket.on('message', (data) => {
                console.log('Received message:', data);
            });
        });
    </script>
</head>
<body>
    <h1>Welcome to Chat Rooms</h1>
    <div>
        <input type="text" id="room" placeholder="Room name">
        <button onclick="joinRoom()">Join Room</button>
    </div>
    <script>
        function joinRoom() {
            const room = document.getElementById('room').value;
            if (room) {
                window.location.href = `/room/${room}`;
            }
        }
    </script>
</body>
</html>
        ''')
    
    # 創建 room.html
    with open('templates/room.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        #messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        #message { width: 80%; }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io();
            const room = '{{ room }}';
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('message');
            
            // 加入房間
            socket.emit('join', { room: room });
            
            // 接收消息
            socket.on('message', (data) => {
                const message = document.createElement('div');
                message.textContent = data.data;
                messagesDiv.appendChild(message);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
            
            // 接收歷史消息
            socket.on('history', (data) => {
                data.messages.reverse().forEach(msg => {
                    const message = document.createElement('div');
                    message.textContent = msg;
                    messagesDiv.appendChild(message);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
            
            // 發送消息
            document.getElementById('send').onclick = () => {
                const message = messageInput.value;
                if (message) {
                    socket.emit('message', { room: room, message: message });
                    messageInput.value = '';
                }
            };
            
            // 按 Enter 發送消息
            messageInput.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    document.getElementById('send').click();
                }
            };
        });
    </script>
</head>
<body>
    <h1>Chat Room: {{ room }}</h1>
    <div id="messages"></div>
    <div>
        <input type="text" id="message" placeholder="Type a message...">
        <button id="send">Send</button>
    </div>
    <div>
        <button onclick="window.location.href='/'">Back to Rooms</button>
    </div>
</body>
</html>
        ''')
    
    return 'Templates created successfully!'

if __name__ == '__main__':
    # 創建模板
    create_templates()
    # 啟動服務器
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 