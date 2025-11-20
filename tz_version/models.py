from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # worker, auditor, manager, admin, quality_director, production_director
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    department = db.relationship('Department', backref='users')
    self_checks = db.relationship('SelfCheck', backref='user', lazy=True)
    assigned_remarks = db.relationship('Remark', foreign_keys='Remark.assigned_to_id', backref='assigned_user')
    created_remarks = db.relationship('Remark', foreign_keys='Remark.created_by_id', backref='creator')
    audits = db.relationship('Audit', backref='auditor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles or self.role == 'admin'

    def get_role_display(self):
        role_display = {
            'admin': 'Специалист по бережливому производству',
            'manager': 'Руководитель подразделения',
            'auditor': 'Аудитор',
            'worker': 'Работник',
            'quality_director': 'Директор по качеству',
            'production_director': 'Директор по производству'
        }
        return role_display.get(self.role, self.role)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    department_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Древовидная структура
    children = db.relationship('Department', backref=db.backref('parent', remote_side=[id]))

class Checklist(db.Model):
    __tablename__ = 'checklists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    checklist_type = db.Column(db.String(20), nullable=False)  # 'self_check' или 'audit'
    department_type = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    criteria_groups = db.relationship('CriteriaGroup', backref='checklist', lazy=True)

class CriteriaGroup(db.Model):
    __tablename__ = 'criteria_groups'
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    order_index = db.Column(db.Integer, default=0)

    criteria = db.relationship('Criterion', backref='group', lazy=True)

class Criterion(db.Model):
    __tablename__ = 'criteria'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('criteria_groups.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, default=0)

class SelfCheck(db.Model):
    __tablename__ = 'self_checks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id'), nullable=False)
    check_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)

    department = db.relationship('Department')
    checklist = db.relationship('Checklist')
    answers = db.relationship('SelfCheckAnswer', backref='self_check', lazy=True)

class SelfCheckAnswer(db.Model):
    __tablename__ = 'self_check_answers'
    id = db.Column(db.Integer, primary_key=True)
    self_check_id = db.Column(db.Integer, db.ForeignKey('self_checks.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    score = db.Column(db.Integer)  # 1-5
    notes = db.Column(db.Text)

    criterion = db.relationship('Criterion')

class Audit(db.Model):
    __tablename__ = 'audits'
    id = db.Column(db.Integer, primary_key=True)
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id'), nullable=False)
    audit_date = db.Column(db.DateTime, default=datetime.utcnow)
    audit_type = db.Column(db.String(20), default='planned')
    total_score = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)

    department = db.relationship('Department')
    checklist = db.relationship('Checklist')
    answers = db.relationship('CriterionAnswer', backref='audit', lazy=True)
    remarks = db.relationship('Remark', backref='audit', lazy=True)

class CriterionAnswer(db.Model):
    __tablename__ = 'criterion_answers'
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    score = db.Column(db.Integer)  # 1-5
    notes = db.Column(db.Text)

    criterion = db.relationship('Criterion')

class Remark(db.Model):
    __tablename__ = 'remarks'
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='identified')
    due_date = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    criterion = db.relationship('Criterion')

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    remark = db.relationship('Remark', backref='photos')

class AuditSchedule(db.Model):
    __tablename__ = 'audit_schedule'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    scheduled_date = db.Column(db.DateTime, nullable=False)
    audit_type = db.Column(db.String(20), default='planned')
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department')
    auditor = db.relationship('User')