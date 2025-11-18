# fix_database.py - Принудительное создание таблиц БД
import os
import sys
from flask import Flask

sys.path.append(os.path.dirname(__file__))

def create_tables():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///5s_system.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'fix-db-key'
    
    from app.models import db
    
    # Инициализируем БД с приложением
    db.init_app(app)
    
    with app.app_context():
        # УДАЛЯЕМ все таблицы и создаем заново
        db.drop_all()
        db.create_all()
        
        # Проверяем создание
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("🗄️ Таблицы созданы заново:")
        for table in tables:
            print(f"   ✅ {table}")
        
        print(f"📊 Всего таблиц: {len(tables)}")
        
        return True

if __name__ == '__main__':
    print("🔧 Исправляем базу данных...")
    if create_tables():
        print("🎉 База данных исправлена!")
    else:
        print("❌ Ошибка при создании БД")