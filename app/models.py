from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# НЕ импортируем db здесь - это вызовет циклический импорт
# from app import db  # ❌ ЭТО НЕПРАВИЛЬНО

print("✅ models.py загружен")

# Создаем базовый класс, который будет заполнен позже
class BaseModel:
    """Базовый класс для моделей"""
    pass

# Определяем модели без наследования от db.Model пока
class User(BaseModel, UserMixin):
    """Модель пользователя"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password_hash = kwargs.get('password_hash')
        self.role = kwargs.get('role', 'user')
        self.department = kwargs.get('department')
        self.position = kwargs.get('position')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at', datetime.utcnow())

    def set_password(self, password):
        from app import db
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return self.role == role_name or self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

# Временно пустые классы для остальных моделей
class Area5S(BaseModel):
    pass

class Check5S(BaseModel):
    pass

class Audit5S(BaseModel):
    pass

class Notification5S(BaseModel):
    pass

class Report5S(BaseModel):
    pass