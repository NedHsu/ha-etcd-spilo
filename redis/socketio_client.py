import socketio
import time

# 創建 SocketIO 客戶端
sio = socketio.Client()

# 連接事件處理
@sio.event
def connect():
    print('Connected to server')

# 斷開連接事件處理
@sio.event
def disconnect():
    print('Disconnected from server')

# 消息事件處理
@sio.on('message')
def on_message(data):
    print(f'Received message: {data}')

# 歷史消息事件處理
@sio.on('history')
def on_history(data):
    print(f'Received history: {data}')

def main():
    try:
        # 連接到服務器
        sio.connect('http://localhost:5000')
        
        # 發送消息
        sio.emit('message', 'Hello from client!')
        
        # 加入房間
        sio.emit('join_room', {'room': 'test_room'})
        
        # 獲取歷史消息
        sio.emit('get_history', {'count': 5})
        
        # 保持連接
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('Disconnecting...')
        sio.disconnect()
    except Exception as e:
        print(f'Error: {str(e)}')
        sio.disconnect()

if __name__ == '__main__':
    main() 