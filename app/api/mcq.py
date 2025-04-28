# app/api/mcq.py

import os
from flask import Blueprint, jsonify, current_app, send_from_directory, url_for, request
from app.extensions import get_firestore_client
from firebase_admin import firestore

api_bp = Blueprint('mcq', __name__)

@api_bp.route('/questionSets/<unit_id>/questions', methods=['GET'])
def get_unit_questions(unit_id):
    """
    回傳題目清單，每題多出 audioUrl 欄位，
    可直接拿去 <audio src="…"> 播放。
    """
    db = get_firestore_client()
    unit_ref = db.collection('questionSets').document(unit_id)
    unit_snap = unit_ref.get()
    if not unit_snap.exists:
        return jsonify({'message': f'Unit "{unit_id}" not found'}), 404

    questions = []
    for doc in unit_ref.collection('questions').stream():
        data = doc.to_dict()
        qid = doc.id
        data['id'] = qid
        # 動態產生指向同一 Blueprint 的檔案路由
        data['audioUrl'] = url_for(
            'mcq.serve_mcq_file',
            unit_id=unit_id,
            filename=f'{qid}.wav',
            _external=True
        )
        questions.append(data)

    return jsonify({
        'unitId': unit_id,
        'questions': questions
    }), 200

@api_bp.route('/questionSets/<unit_id>/audio/<filename>', methods=['GET'])
def serve_mcq_file(unit_id, filename):
    """
    真正把存放在 app/resource/MCQ/<unit_id>/<filename> 的 wav
    透過這支路由送出去。
    """
    # current_app.root_path → chumi/app
    directory = os.path.join(current_app.root_path, 'resource', 'MCQ', unit_id)
    return send_from_directory(directory, filename)

def _room_doc(room_id):
    db = get_firestore_client()
    return db.collection('rooms').document(room_id)

@api_bp.route('/rooms', methods=['POST', 'GET'])
def rooms():
    """
    POST: 建立新遊戲房間，JSON Body:
    {
      "host": "用戶 uid",
      "unitId": "題組 ID",
      "roomId": "自訂房間 ID (optional)"
    }
    回傳 roomId。

    GET: 取得所有 waiting 狀態的房間清單
    回傳格式：[{"roomId": "...", "host": "...", "players": [...]}, ...]
    """
    db = get_firestore_client()
    if request.method == 'POST':
        data = request.get_json(force=True)
        host = data.get('host')
        unit_id = data.get('unitId')
        custom_id = data.get('roomId')
        if not host or not unit_id:
            return jsonify({'message': '請提供 host 與 unitId'}), 400
        # 檢查 custom_id
        if custom_id:
            room_ref = db.collection('rooms').document(custom_id)
            if room_ref.get().exists:
                return jsonify({'message': f'Room {custom_id} already exists'}), 400
            room_id = custom_id
        else:
            room_ref = db.collection('rooms').document()
            room_id = room_ref.id
        room_ref.set({
            'host': host,
            'unitId': unit_id,
            'players': [],
            'status': 'waiting',
            'currentQuestionIndex': 0,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        return jsonify({'roomId': room_id}), 201
    else:
        # GET: list waiting rooms
        rooms = []
        docs = db.collection('rooms').where('status', '==', 'waiting').stream()
        for doc in docs:
            data = doc.to_dict()
            rooms.append({
                'roomId': doc.id,
                'host': data.get('host'),
                'players': data.get('players', [])
            })
        return jsonify({'rooms': rooms}), 200


@api_bp.route('/rooms/<room_id>/join', methods=['POST'])
def join_room(room_id):
    """
    加入房間，JSON Body:
    { "user": "用戶 uid" }
    """
    data = request.get_json(force=True)
    user = data.get('user')
    if not user:
        return jsonify({'message': '請提供 user'}), 400

    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': f'Room {room_id} not found'}), 404
    # 不重複加入
    room_ref.update({
        'players': firestore.ArrayUnion([user])
    })
    return jsonify({'message': f'User {user} joined room {room_id}'}), 200

@api_bp.route('/rooms/<room_id>/start', methods=['POST'])
def start_game(room_id):
    """
    房主啟動遊戲
    """
    data = request.get_json(force=True)
    host = data.get('host')
    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': 'Room not found'}), 404
    room = snap.to_dict()
    if room.get('host') != host:
        return jsonify({'message': 'Only host can start the game'}), 403

    room_ref.update({
        'status': 'started',
        'startAt': firestore.SERVER_TIMESTAMP
    })
    return jsonify({'message': 'Game started'}), 200

@api_bp.route('/rooms/<room_id>/submit', methods=['POST'])
def submit_all_answers(room_id):
    """
    批量提交所有題目答案，JSON Body:
    {
      "user": "用戶 uid",
      "answers": [
         {"questionId": "q01", "selected": 2},
         ...
      ]
    }
    房間所有玩家提交完後自動標記狀態為 finished，並將本次提交結果存入使用者 record。
    """
    data = request.get_json(force=True)
    user = data.get('user')
    answers = data.get('answers')
    if not user or not isinstance(answers, list):
        return jsonify({'message': '請提供 user 與 answers 列表'}), 400
    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': 'Room not found'}), 404
    room = snap.to_dict()
    players = room.get('players', [])
    db = get_firestore_client()

    # 批次寫入答案
    batch = db.batch()
    for ans in answers:
        qid = ans.get('questionId')
        sel = ans.get('selected')
        if not qid or sel is None:
            continue
        doc_ref = room_ref.collection('answers').document(f"{user}_{qid}")
        batch.set(doc_ref, {
            'user': user,
            'questionId': qid,
            'selected': sel,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
    batch.commit()

    # 檢查是否所有玩家都完成
    unit_id = room.get('unitId')
    total_qs = len(list(db.collection('questionSets')
                        .document(unit_id)
                        .collection('questions')
                        .stream()))
    ans_docs = list(room_ref.collection('answers').stream())
    if len(ans_docs) >= len(players) * total_qs:
        room_ref.update({'status': 'finished', 'finishedAt': firestore.SERVER_TIMESTAMP})

    # 將本次提交存入使用者 record
    from app.models import User
        # 將本次提交存入使用者 record，使用後端時間戳
    from app.models import User
    from datetime import datetime
    entry = {
        'date': datetime.utcnow().isoformat() + 'Z',  # ISO 格式 UTC 時間
        'mode': room.get('unitId'),
        'answers': answers
    }
    User.add_record(user, entry)
    User.add_record(user, entry)

    return jsonify({'message': 'Answers submitted'}), 200

@api_bp.route('/rooms/<room_id>/players', methods=['GET'])
def get_room_players(room_id):
    """
    取得房間玩家清單，不包含房主。
    回傳格式：{ 'host': ..., 'players': [...] }
    """
    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': 'Room not found'}), 404
    room = snap.to_dict()
    host = room.get('host')
    players = room.get('players', [])
    return jsonify({
        'host': host,
        'players': players
    }), 200
    
@api_bp.route('/rooms/<room_id>/status', methods=['GET'])
def get_room_status(room_id):
    """
    確認房間狀態，回傳 host、players、status、currentQuestionIndex 和 unitId。
    """
    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': 'Room not found'}), 404
    room = snap.to_dict()
    return jsonify({
        'host': room.get('host'),
        'players': room.get('players', []),
        'status': room.get('status'),
        'currentQuestionIndex': room.get('currentQuestionIndex'),
        'unitId': room.get('unitId')
    }), 200

@api_bp.route('/rooms/<room_id>/results', methods=['GET'])
def get_results(room_id):
    """
    取得最終排名
    """
    db = get_firestore_client()
    room_ref = _room_doc(room_id)
    snap = room_ref.get()
    if not snap.exists:
        return jsonify({'message': 'Room not found'}), 404
    room = snap.to_dict()
    unit_id = room.get('unitId')

    # 讀取題組答案
    qs = db.collection('questionSets').document(unit_id).collection('questions').stream()
    answers_map = {d.id: d.to_dict().get('ans') for d in qs}

    # 彙整玩家答案並計算分數
    users = room.get('players', [])
    scores = {u: 0 for u in users}
    ans_docs = room_ref.collection('answers').stream()
    for ans in ans_docs:
        a = ans.to_dict()
        user = a['user']
        qid = a['questionId']
        if answers_map.get(qid) == a.get('selected'):
            scores[user] = scores.get(user, 0) + 1

    # 排序
    ranking = sorted(
        [{'user': u, 'score': scores[u]} for u in scores],
        key=lambda x: x['score'],
        reverse=True
    )
    return jsonify({'results': ranking}), 200
