backend/
├── app/
│   ├── __init__.py           # 建立 Flask 應用與各擴展初始化
│   ├── config.py             # 配置檔案
│   ├── extensions.py         # 初始第三方套件 (SQLAlchemy, JWT 等)
│   ├── models.py             # 全域資料模型 (例如 User)
│   ├── api/                  # API 路由模組（Blueprints）
│   │   ├── __init__.py       # 統一註冊各 API 藍圖
│   │   ├── auth.py           # 登入、註冊等驗證 API
│   │   ├── users.py          # 用戶相關 API
│   │   └── main.py           # 其他 API 端點
│   └── errors/               # 統一處理 API 錯誤返回 JSON 格式訊息
│       ├── __init__.py       
│       └── handlers.py       
├── migrations/               # 若使用 Flask-Migrate 管理資料庫遷移
├── requirements.txt          # 專案依賴
├── run.py                    # 啟動應用的入口
└── README.md                 # 專案文件
