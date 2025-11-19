from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'message': 'Система 5С API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/auth/*',
            'api': '/api/*'
        }
    })

@main.route('/dashboard')
@login_required
def dashboard():
    """Дашборд системы"""
    return jsonify({
        'message': 'Дашборд системы 5С',
        'user': current_user.username
    })