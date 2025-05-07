from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# 初始化 SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 通過 HAProxy 連接數據庫
    # HAProxy 配置：
    # - 寫入端口 5000 轉發到主數據庫
    # - 讀取端口 5001 轉發到從數據庫
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@haproxy:5000/postgres'  # 主數據庫（寫入）
    app.config['SQLALCHEMY_BINDS'] = {
        'slave': 'postgresql://postgres:postgres@haproxy:5001/postgres'  # 從數據庫（讀取）
    }

    # 初始化擴展
    db.init_app(app)

    # 創建主數據庫引擎
    master_engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10
    )

    # 創建從數據庫引擎
    slave_engine = create_engine(
        app.config['SQLALCHEMY_BINDS']['slave'],
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10
    )

    # 創建會話工廠
    app.master_session = sessionmaker(bind=master_engine)
    app.slave_session = sessionmaker(bind=slave_engine)

    # 註冊藍圖
    from .routes import main
    app.register_blueprint(main)

    return app 