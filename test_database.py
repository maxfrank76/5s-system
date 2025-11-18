# test_database.py - Тест создания базы данных
from app import create_app, db
from app.models import User, Role, Department

def test_database():
    print("🗄️ ТЕСТ СОЗДАНИЯ БАЗЫ ДАННЫХ")
    print("=" * 40)
    
    try:
        # Создаем приложение
        app = create_app()
        
        with app.app_context():
            # Проверяем создание таблиц
            db.create_all()
            print("✅ Таблицы базы данных созданы успешно!")
            
            # Проверяем подключение
            tables = db.engine.table_names()
            print(f"✅ Создано таблиц: {len(tables)}")
            print("📊 Таблицы:", ", ".join(tables))
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🎉 База данных готова к работе!")
    else:
        print("\n❌ Есть проблемы с базой данных.")