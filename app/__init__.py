from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему.'

def create_app():
    """Фабрика для создания приложения Flask"""
    app = Flask(__name__)
    
    # Базовая конфигурация
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///5s_system.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    # CORS временно убран
    
    # Регистрация блюпринтов
    try:
        from app.main import main as main_blueprint
        from app.auth import auth as auth_blueprint
        from app.api import api as api_blueprint
        
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(api_blueprint, url_prefix='/api')
        
        print("✅ Все блюпринты зарегистрированы")
    except ImportError as e:
        print(f"❌ Ошибка регистрации блюпринтов: {e}")
    
    return app

# Убираем циклический импорт