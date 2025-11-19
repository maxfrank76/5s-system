"""
Инициализация SQLAlchemy моделей после создания db
"""
from datetime import datetime
from app import db

def init_models():
    """Инициализирует модели SQLAlchemy"""
    
    class User(db.Model):
        __tablename__ = 'users_5s'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), default='user')
        department = db.Column(db.String(100))
        position = db.Column(db.String(100))
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def set_password(self, password):
            from werkzeug.security import generate_password_hash
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            from werkzeug.security import check_password_hash
            return check_password_hash(self.password_hash, password)

        def has_role(self, role_name):
            return self.role == role_name or self.role == 'admin'

        def __repr__(self):
            return f'<User {self.username}>'

    class Area5S(db.Model):
        __tablename__ = 'areas_5s'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        department = db.Column(db.String(100))
        location = db.Column(db.String(200))
        responsible_person_id = db.Column(db.Integer, db.ForeignKey('users_5s.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)
        
        responsible_person = db.relationship('User', backref='responsible_areas')

    class Check5S(db.Model):
        __tablename__ = 'checks_5s'
        
        id = db.Column(db.Integer, primary_key=True)
        area_id = db.Column(db.Integer, db.ForeignKey('areas_5s.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('users_5s.id'), nullable=False)
        
        # 5S критерии
        s_seiri = db.Column(db.Boolean, default=False)
        s_seiton = db.Column(db.Boolean, default=False)
        s_seiso = db.Column(db.Boolean, default=False)
        s_seiketsu = db.Column(db.Boolean, default=False)
        s_shitsuke = db.Column(db.Boolean, default=False)
        
        notes = db.Column(db.Text)
        photos = db.Column(db.JSON)
        checked_at = db.Column(db.DateTime, default=datetime.utcnow)
        total_score = db.Column(db.Integer, default=0)

    class Audit5S(db.Model):
        __tablename__ = 'audits_5s'
        
        id = db.Column(db.Integer, primary_key=True)
        area_id = db.Column(db.Integer, db.ForeignKey('areas_5s.id'), nullable=False)
        auditor_id = db.Column(db.Integer, db.ForeignKey('users_5s.id'), nullable=False)
        
        seiri_score = db.Column(db.Integer, default=0)
        seiton_score = db.Column(db.Integer, default=0)
        seiso_score = db.Column(db.Integer, default=0)
        seiketsu_score = db.Column(db.Integer, default=0)
        shitsuke_score = db.Column(db.Integer, default=0)
        
        total_score = db.Column(db.Integer, default=0)
        comments = db.Column(db.Text)
        recommendations = db.Column(db.Text)
        photos = db.Column(db.JSON)
        audit_date = db.Column(db.DateTime, default=datetime.utcnow)
        next_audit_date = db.Column(db.DateTime)

    print("✅ SQLAlchemy модели инициализированы")
    
    # Возвращаем классы для использования в других модулях
    return {
        'User': User,
        'Area5S': Area5S,
        'Check5S': Check5S,
        'Audit5S': Audit5S
    }