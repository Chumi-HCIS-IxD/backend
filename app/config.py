# app/config.py
import os


# 這行會讀取同層或專案根目錄下的 .env 檔案(如有)，並將其中的變數載入系統環境變數

class Config:
    # Flask 相關
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    
    # JWT 相關
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret')
    JWT_TOKEN_LOCATION = ["headers"]  # 指定從 HTTP 標頭中讀取 Token，可加上 "cookies", "json", "query_string" 等
    
    # Firebase 相關
    FIREBASE_CREDENTIAL = os.environ.get('FIREBASE_CREDENTIAL_PATH', '../backend/app/serviceAccountKey.json')

    # 如需其他設定，也可繼續補充 (e.g., DATABASE_URL, DEBUG 等等)
    # ...
