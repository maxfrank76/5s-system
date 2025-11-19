from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Требуется имя пользователя и пароль'}), 400
    
    # Поиск пользователя по username или email
    user = User.query.filter(
        or_(User.username == data['username'], User.email == data['username'])
    ).first()
    
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({'message': 'Аккаунт деактивирован'}), 403
        
        login_user(user, remember=data.get('remember', False))
        user.last_login = db.func.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Вход выполнен успешно',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'role_display': user.get_role_display(),
                'department': user.department,
                'position': user.position
            }
        }), 200
    
    return jsonify({'message': 'Неверное имя пользователя или пароль'}), 401

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return jsonify({'message': 'Выход выполнен успешно'}), 200

@auth.route('/register', methods=['POST'])
@login_required
def register():
    """Регистрация нового пользователя (только для админов)"""
    if not current_user.has_role('admin'):
        return jsonify({'message': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Проверка уникальности
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Имя пользователя уже существует'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email уже существует'}), 400
    
    # Создание пользователя
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role'],
        department=data.get('department'),
        position=data.get('position'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Пользователь создан успешно',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display()
        }
    }), 201

@auth.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Получить профиль текущего пользователя"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'role_display': current_user.get_role_display(),
        'department': current_user.department,
        'position': current_user.position,
        'phone': current_user.phone,
        'created_at': current_user.created_at.isoformat(),
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    })

@auth.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Обновить профиль пользователя"""
    data = request.get_json()
    
    # Пользователь может менять только свои данные (кроме роли)
    if 'email' in data:
        # Проверка уникальности email
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'message': 'Email уже используется'}), 400
        current_user.email = data['email']
    
    if 'department' in data:
        current_user.department = data['department']
    
    if 'position' in data:
        current_user.position = data['position']
    
    if 'phone' in data:
        current_user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({'message': 'Профиль обновлен успешно'})

@auth.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Смена пароля"""
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Требуется текущий и новый пароль'}), 400
    
    if not current_user.check_password(data['current_password']):
        return jsonify({'message': 'Неверный текущий пароль'}), 400
    
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Пароль изменен успешно'})