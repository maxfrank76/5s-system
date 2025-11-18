# app/__init__.py - Инициализация приложения
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Инициализация расширений происходит позже
    from app.models import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)
    
    # Создаем таблицы в базе данных
    with app.app_context():
        db.create_all()
        print("✅ База данных инициализирована!")
    
    return app