# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import init_firebase_app
from flask_jwt_extended import JWTManager
# 如果有其他擴展也請一併引入，如 SQLAlchemy, JWT 等

def create_app():
    app = Flask(__name__)
    
    # 載入設定
    app.config.from_object(Config)
    
    # 初始化 Firebase Admin SDK
    init_firebase_app(app)
    
    # 初始化其他第三方套件
    # 例如：db.init_app(app)
    
    # 註冊 API 藍圖
    from app.api import register_api_blueprints
    register_api_blueprints(app)
    jwt = JWTManager(app)
    # 初始化錯誤處理（若有相關設定）
    # from app.errors import register_error_handlers
    # register_error_handlers(app)
    
    return app
