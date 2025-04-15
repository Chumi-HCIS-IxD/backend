# app/extensions.py
import firebase_admin
from firebase_admin import credentials, firestore

# 如果你的其他第三方套件初始化也放在這裡，請繼續原有的內容
# 例如：from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

def init_firebase_app(app):
    """
    使用 Flask 應用設定來初始化 Firebase Admin SDK。
    若設定中有 FIREBASE_CREDENTIAL，則使用該服務帳戶金鑰初始化，
    否則就嘗試使用預設認證。
    """
    cred_path = app.config.get('FIREBASE_CREDENTIAL')
    if cred_path:
        cred = credentials.Certificate(cred_path)
        # 若已經初始化過會拋出錯誤，可以進行例外處理
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
    else:
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()

def get_firestore_client():
    """
    回傳 Firestore 客戶端，此函式可以被 models 或其他地方調用。
    """
    return firestore.client()
