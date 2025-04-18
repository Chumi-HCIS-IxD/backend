from flask import Blueprint
from app.api import auth, users, main, mcq,results

def register_api_blueprints(app):
    # 註冊 auth 模組，前綴 /api/auth
    app.register_blueprint(auth.api_bp, url_prefix='/api/auth')
    # 註冊 users 模組，前綴 /api/users
    app.register_blueprint(users.api_bp, url_prefix='/api/users')
    # 註冊 main 模組，前綴 /api
    app.register_blueprint(main.api_bp, url_prefix='/api')
    app.register_blueprint(mcq.api_bp, url_prefix='/api/mcq')
    app.register_blueprint(results.api_bp, url_prefix='/api')
