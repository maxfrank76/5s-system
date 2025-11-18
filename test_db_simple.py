# test_db_simple.py - Простой тест БД
import os
import sys
from flask import Flask

# Добавляем текущую папку в путь
sys.path.append(os.path.dirname(__file__))

def test_database_creation():
    print("🗄️ ПРОСТОЙ ТЕСТ БАЗЫ ДАННЫХ")
    print("=" * 40)
    
    try:
        # Создаем временное приложение Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_5s.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Инициализируем базу данных
        from app.models import db
        db.init_app(app)
        
        # Создаем таблицы
        with app.app_context():
            db.create_all()
            print("✅ Таблицы созданы успешно!")
            
            # Проверяем существование таблиц
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Создано таблиц: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
                
            return True
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_database_creation():
        print("\n🎉 База данных работает!")
    else:
        print("\n❌ Есть проблемы с БД.")