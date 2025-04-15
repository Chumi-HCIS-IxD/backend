# app/api/users.py
from flask import Blueprint, request, jsonify
from app.models import User

api_bp = Blueprint('users', __name__)

@api_bp.route('/profile', methods=['GET'])
def profile():
    # 從 Query String 取得 uid，例如 /api/users/profile?uid=<some_uid>
    uid = request.args.get('uid')
    if not uid:
        return jsonify({'message': 'No uid provided'}), 400

    user = User.get_by_uid(uid)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'uid': user.get("uid"),
        'username': user.get("username"),
        'record': user.get("record", [])
    }), 200
