# run.py - Простой тест сервера
import os
import sys
from flask import Flask

# Добавляем текущую папку в путь Python
sys.path.append(os.path.dirname(__file__))

def create_simple_app():
    """Создаем простое приложение для теста"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///5s_system.db'
    
    # Инициализируем базу данных
    from app.models import db
    db.init_app(app)
    
    @app.route('/')
    def hello():
        return '''
        <h1>🚀 System 5S работает!</h1>
        <p>Flask сервер: ✅ Запущен</p>
        <p>База данных: ✅ Готова</p>
        <p><strong>Следующие шаги в новом чате:</strong></p>
        <ul>
            <li>Аутентификация (Flask-Login)</li>
            <li>API эндпоинты</li>
            <li>PWA фронтенд</li>
        </ul>
        <a href="/test">Тест БД</a>
        '''
    
    @app.route('/test')
    def test_db():
        with app.app_context():
            from app.models import User, Department
            user_count = User.query.count()
            dept_count = Department.query.count()
            return f'''
            <h2>📊 Тест базы данных</h2>
            <p>Пользователей: {user_count}</p>
            <p>Подразделений: {dept_count}</p>
            <p>✅ База данных отвечает!</p>
            <a href="/">Назад</a>
            '''
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("🌐 Запуск сервера: http://localhost:5000")
    print("📁 Репозиторий: https://github.com/maxfrank76/5s-system.git")
    app.run(debug=True, host='0.0.0.0', port=5000)