# app/api/auth.py

from flask import Blueprint, request, jsonify
import uuid
from app.models import User  # 假設你在 models.py 中實作了 get_by_username 與 create

api_bp = Blueprint('auth', __name__)

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    record = data.get('record', [])

    # 檢查必要欄位
    if not username or not password:
        return jsonify({'message': 'username 與 password 為必填項'}), 400

    # record 必須是一個 list
    if not isinstance(record, list):
        return jsonify({'message': 'record 必須是一個 list'}), 400

    # 若 record 有內容，檢查每一筆都要有 date, mode, score
    for entry in record:
        if not isinstance(entry, dict) or not all(key in entry for key in ("date", "mode", "score")):
            return jsonify({'message': 'record 中的每筆資料必須符合 {"date": "", "mode": "", "score": ""} 格式'}), 400

    # 檢查是否已存在同名使用者
    if User.get_by_username(username):
        return jsonify({'message': 'Username 已存在'}), 400

    # 產生 uid，並組裝使用者資料
    uid = str(uuid.uuid4())
    user_data = {
        "uid": uid,
        "username": username,
        "password": password,   # 實際應加密
        "record": record
    }

    doc_id = User.create(user_data)
    return jsonify({
        "message": "使用者註冊成功",
        "uid": uid,
    }), 201


@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 檢查必要欄位
    if not username or not password:
        return jsonify({'message': 'username 與 password 為必填項'}), 400

    # 查詢使用者
    user = User.get_by_username(username)
    if not user:
        return jsonify({'message': '用戶不存在'}), 404

    # 驗證密碼（實際應使用雜湊方式）
    if user.get('password') != password:
        return jsonify({'message': '密碼錯誤'}), 401

    # 登入成功，不再發行 JWT，而是單純回傳成功訊息與使用者 uid
    return jsonify({
        "message": "登入成功",
        "uid": user["uid"]
    }), 200
