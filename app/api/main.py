from flask import Blueprint, jsonify

api_bp = Blueprint('main', __name__)

@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'API Running'}), 200
