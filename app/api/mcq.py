# app/api/mcq.py

import os
from flask import Blueprint, jsonify, current_app, send_from_directory, url_for
from app.extensions import get_firestore_client

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
