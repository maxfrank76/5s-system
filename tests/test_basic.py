# tests/test_basic.py - Базовые тесты
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db

def test_app_creation():
    """Тест создания приложения"""
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None

def test_database_connection():
    """Тест подключения к БД"""
    app = create_app()
    with app.app_context():
        # Простой запрос к БД
        result = db.session.execute('SELECT 1').scalar()
        assert result == 1

if __name__ == '__main__':
    test_app_creation()
    test_database_connection()
    print("✅ Все базовые тесты прошли!")