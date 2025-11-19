from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import json
import os
from app import db
ffrom app.models import Area5S as Area, Check5S as Check, Audit5S as Audit, User
from functools import wraps

api = Blueprint('api', __name__)

def role_required(*roles):
    """Декоратор для проверки ролей"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(*roles):
                return jsonify({'message': 'Недостаточно прав'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ===== AREAS ENDPOINTS =====
@api.route('/areas', methods=['GET'])
@login_required
def get_areas():
    """Получить список всех участков"""
    areas = Area.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': area.id,
        'name': area.name,
        'description': area.description,
        'department': area.department,
        'location': area.location,
        'responsible_person': area.responsible_person.username if area.responsible_person else None,
        'responsible_person_id': area.responsible_person_id,
        'created_at': area.created_at.isoformat(),
        'last_check': Check.query.filter_by(area_id=area.id).order_by(desc(Check.checked_at)).first().checked_at.isoformat() if Check.query.filter_by(area_id=area.id).first() else None,
        'average_score': db.session.query(func.avg(Check.total_score)).filter(Check.area_id == area.id).scalar() or 0
    } for area in areas])

@api.route('/areas/<int:area_id>', methods=['GET'])
@login_required
def get_area(area_id):
    """Получить детали участка"""
    area = Area.query.get_or_404(area_id)
    
    return jsonify({
        'id': area.id,
        'name': area.name,
        'description': area.description,
        'department': area.department,
        'location': area.location,
        'responsible_person': area.responsible_person.username if area.responsible_person else None,
        'responsible_person_id': area.responsible_person_id,
        'created_at': area.created_at.isoformat()
    })

@api.route('/areas', methods=['POST'])
@role_required('admin', 'manager')
def create_area():
    """Создать новый участок"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Название участка обязательно'}), 400
    
    area = Area(
        name=data['name'],
        description=data.get('description'),
        department=data.get('department'),
        location=data.get('location'),
        responsible_person_id=data.get('responsible_person_id')
    )
    
    db.session.add(area)
    db.session.commit()
    
    return jsonify({
        'message': 'Участок создан успешно',
        'area': {
            'id': area.id,
            'name': area.name
        }
    }), 201

# ===== CHECKS ENDPOINTS =====
@api.route('/checks', methods=['POST'])
@login_required
def create_check():
    """Создать проверку 5С"""
    data = request.get_json()
    
    required_fields = ['area_id', 's_seiri', 's_seiton', 's_seiso', 's_seiketsu', 's_shitsuke']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    check = Check(
        area_id=data['area_id'],
        user_id=current_user.id,
        s_seiri=bool(data['s_seiri']),
        s_seiton=bool(data['s_seiton']),
        s_seiso=bool(data['s_seiso']),
        s_seiketsu=bool(data['s_seiketsu']),
        s_shitsuke=bool(data['s_shitsuke']),
        notes=data.get('notes'),
        photos=data.get('photos', [])
    )
    
    # Расчет оценки
    check.calculate_score()
    
    db.session.add(check)
    db.session.commit()
    
    return jsonify({
        'message': 'Проверка создана успешно',
        'check': {
            'id': check.id,
            'area_id': check.area_id,
            'total_score': check.total_score
        }
    }), 201

@api.route('/checks/area/<int:area_id>', methods=['GET'])
@login_required
def get_area_checks(area_id):
    """Получить проверки для участка"""
    checks = Check.query.filter_by(area_id=area_id).order_by(desc(Check.checked_at)).all()
    
    return jsonify([{
        'id': check.id,
        'area_id': check.area_id,
        'user': check.user.username,
        's_seiri': check.s_seiri,
        's_seiton': check.s_seiton,
        's_seiso': check.s_seiso,
        's_seiketsu': check.s_seiketsu,
        's_shitsuke': check.s_shitsuke,
        'total_score': check.total_score,
        'notes': check.notes,
        'checked_at': check.checked_at.isoformat()
    } for check in checks])

# ===== AUDITS ENDPOINTS =====
@api.route('/audits', methods=['POST'])
@role_required('admin', 'manager', 'auditor')
def create_audit():
    """Создать аудит"""
    data = request.get_json()
    
    required_fields = ['area_id', 'seiri_score', 'seiton_score', 'seiso_score', 'seiketsu_score', 'shitsuke_score']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    audit = Audit(
        area_id=data['area_id'],
        auditor_id=current_user.id,
        seiri_score=data['seiri_score'],
        seiton_score=data['seiton_score'],
        seiso_score=data['seiso_score'],
        seiketsu_score=data['seiketsu_score'],
        shitsuke_score=data['shitsuke_score'],
        comments=data.get('comments'),
        recommendations=data.get('recommendations'),
        photos=data.get('photos', [])
    )
    
    # Расчет общей оценки
    audit.calculate_total_score()
    
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'message': 'Аудит создан успешно',
        'audit': {
            'id': audit.id,
            'area_id': audit.area_id,
            'total_score': audit.total_score,
            'grade': audit.get_grade()
        }
    }), 201

# ===== USERS ENDPOINTS =====
@api.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Получить список пользователей (только для админов)"""
    users = User.query.all()
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'role_display': user.get_role_display(),
        'department': user.department,
        'position': user.position,
        'phone': user.phone,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users])

@api.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Получить статистику для дашборда"""
    total_areas = Area.query.filter_by(is_active=True).count()
    total_checks = Check.query.count()
    total_audits = Audit.query.count()
    
    # Последние проверки
    recent_checks = Check.query.order_by(desc(Check.checked_at)).limit(5).all()
    
    # Статистика по отделам
    department_stats = db.session.query(
        Area.department,
        func.count(Area.id),
        func.avg(Check.total_score)
    ).join(Check).group_by(Area.department).all()
    
    return jsonify({
        'total_areas': total_areas,
        'total_checks': total_checks,
        'total_audits': total_audits,
        'recent_checks': [{
            'id': check.id,
            'area_name': check.area.name,
            'user': check.user.username,
            'score': check.total_score,
            'checked_at': check.checked_at.isoformat()
        } for check in recent_checks],
        'department_stats': [{
            'department': dept,
            'area_count': count,
            'avg_score': round(avg_score or 0, 2)
        } for dept, count, avg_score in department_stats]
    })