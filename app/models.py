# app/models.py - Модели базы данных
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime
import os

# Инициализируем расширения
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db = SQLAlchemy()

# Вспомогательная таблица для многие-ко-многим (роли пользователей)
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    created_audits = db.relationship('Audit', foreign_keys='Audit.auditor_id', backref='auditor', lazy='dynamic')
    assigned_remarks = db.relationship('Remark', foreign_keys='Remark.assigned_to_id', backref='assigned_to', lazy='dynamic')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department_type = db.Column(db.String(50))  # 'office', 'production', etc.
    
    # Иерархическая структура
    parent_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    children = db.relationship('Department', backref=db.backref('parent', remote_side=[id]))
    
    # Связи
    users = db.relationship('User', backref='department', lazy='dynamic')
    audits = db.relationship('Audit', backref='department', lazy='dynamic')

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    checklist_type = db.Column(db.String(20), nullable=False)  # 'audit', 'self_check'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    criteria_groups = db.relationship('CriteriaGroup', backref='checklist', lazy='dynamic')
    department_types = db.relationship('ChecklistDepartmentType', backref='checklist', lazy='dynamic')

class CriteriaGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Связи
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    criteria = db.relationship('Criterion', backref='group', lazy='dynamic')

class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Связи
    group_id = db.Column(db.Integer, db.ForeignKey('criteria_group.id'), nullable=False)
    answers = db.relationship('CriterionAnswer', backref='criterion', lazy='dynamic')

class ChecklistDepartmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_type = db.Column(db.String(50), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    audit_type = db.Column(db.String(20), nullable=False)  # 'planned', 'unscheduled'
    status = db.Column(db.String(20), default='draft')  # 'draft', 'in_progress', 'completed'
    total_score = db.Column(db.Float)
    max_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Связи
    auditor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    answers = db.relationship('CriterionAnswer', backref='audit', lazy='dynamic')
    remarks = db.relationship('Remark', backref='audit', lazy='dynamic')

class CriterionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    
    # Связи
    audit_id = db.Column(db.Integer, db.ForeignKey('audit.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    photos = db.relationship('Photo', backref='criterion_answer', lazy='dynamic')

class Remark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='reported')  # 'reported', 'assigned', 'fixed', 'verified'
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fixed_at = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)
    
    # Связи
    audit_id = db.Column(db.Integer, db.ForeignKey('audit.id'), nullable=False)
    criterion_answer_id = db.Column(db.Integer, db.ForeignKey('criterion_answer.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photos = db.relationship('Photo', backref='remark', lazy='dynamic')

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи (фото может быть привязано либо к ответу на критерий, либо к замечанию)
    criterion_answer_id = db.Column(db.Integer, db.ForeignKey('criterion_answer.id'))
    remark_id = db.Column(db.Integer, db.ForeignKey('remark.id'))

class AuditSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False)  # 'planned', 'unscheduled'
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    auditor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)

class SelfCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'completed'
    total_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    answers = db.relationship('SelfCheckAnswer', backref='self_check', lazy='dynamic')

class SelfCheckAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    
    # Связи
    self_check_id = db.Column(db.Integer, db.ForeignKey('self_check.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)