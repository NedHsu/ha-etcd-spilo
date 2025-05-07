from app import create_app, db

app = create_app()

# 創建數據庫表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 