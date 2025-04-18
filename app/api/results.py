# app/api/results.py

from flask import Blueprint, request, jsonify
from app.models import User

api_bp = Blueprint('results', __name__)

@api_bp.route('/results', methods=['POST'])
def create_result():
    """
    前端傳 JSON：
    {
      "uid":   "使用者的 uid",
      "mode":  "考題模式或單元名稱",
      "score": 85,
      "date":  "2025-04-18"   # ISO 字串
    }
    範例呼叫： POST /api/results
    """
    data = request.get_json(force=True)
    uid   = data.get('uid')
    mode  = data.get('mode')
    score = data.get('score')
    date  = data.get('date')

    # 驗證
    if not all([uid, mode, score is not None, date]):
        return jsonify({'message': '請提供 uid、mode、score、date'}), 400

    # 確認使用者存在
    user = User.get_by_uid(uid)
    if not user:
        return jsonify({'message': f'User {uid} not found'}), 404

    # 組裝一筆記錄
    entry = {
        'date':  date,
        'mode':  mode,
        'score': score
    }

    # 把這筆 entry append 到 user.record
    User.add_record(uid, entry)

    return jsonify({
        'message': 'Record added to user',
        'entry': entry
    }), 201
