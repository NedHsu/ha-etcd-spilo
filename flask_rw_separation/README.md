# Flask Read-Write Separation Example

這是一個使用 Flask、SQLAlchemy 和 HAProxy 實現讀寫分離的示例應用。

## 目錄結構

```
flask_rw_separation/
├── app/
│   ├── __init__.py      # 應用工廠和配置
│   ├── models.py        # 數據庫模型
│   ├── routes.py        # 路由定義
│   └── decorators.py    # 自定義裝飾器
├── run.py              # 應用入口
├── requirements.txt    # 項目依賴
└── README.md          # 項目文檔
```

## 特點

- 使用 HAProxy 實現讀寫分離
- 寫操作通過 HAProxy 轉發到主數據庫
- 讀操作通過 HAProxy 轉發到從數據庫
- 使用連接池優化數據庫連接
- 簡單的裝飾器實現讀寫分離

## HAProxy 配置

HAProxy 配置了兩個監聽端口：
- 端口 5000：轉發到主數據庫（寫入）
- 端口 5001：轉發到從數據庫（讀取）

## 安裝

1. 創建虛擬環境（可選）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

## 運行

```bash
python run.py
```

## API 端點

### 獲取所有用戶
- URL: `GET /users`
- 通過 HAProxy 使用從數據庫（讀取）

### 創建新用戶
- URL: `POST /users`
- 通過 HAProxy 使用主數據庫（寫入）
- 請求體示例：
```json
{
    "username": "test_user",
    "email": "test@example.com"
}
```

## 配置

數據庫連接配置在 `app/__init__.py` 中：

- 主數據庫（寫入）：`postgresql://postgres:postgres@haproxy:5000/postgres`
- 從數據庫（讀取）：`postgresql://postgres:postgres@haproxy:5001/postgres`

## 讀寫分離實現

1. 寫操作：
   - 所有寫操作通過 HAProxy 端口 5000 轉發到主數據庫
   - 使用 `master_session` 進行連接

2. 讀操作：
   - 所有讀操作通過 HAProxy 端口 5001 轉發到從數據庫
   - 使用 `slave_session` 進行連接

## 注意事項

1. 確保 HAProxy 已正確配置並運行
2. 確保數據庫主從複製已正確配置
3. 根據實際需求調整連接池參數
4. 在生產環境中建議添加：
   - 錯誤重試機制
   - 健康檢查
   - 監控和日誌記錄 