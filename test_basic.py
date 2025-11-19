import sys
import os

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Тест импортов основных модулей"""
    print("🧪 Тестирование импортов...")
    
    try:
        from app import create_app, db
        print("✅ app.create_app - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта app: {e}")
        return False
    
    try:
        from app.models import User, Area, Check, Audit
        print("✅ app.models - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта models: {e}")
        return False
    
    try:
        from app.auth import auth
        print("✅ app.auth - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта auth: {e}")
        return False
    
    try:
        from app.api import api
        print("✅ app.api - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта api: {e}")
        return False
    
    try:
        from app.main import main
        print("✅ app.main - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта main: {e}")
        return False
    
    return True

def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    try:
        from app import create_app, db
        from app.models import User
        
        app = create_app()
        with app.app_context():
            # Проверяем подключение к БД
            user_count = User.query.count()
            print(f"✅ База данных подключена")
            print(f"   Пользователей в системе: {user_count}")
            
            # Выводим список пользователей
            users = User.query.all()
            for user in users:
                print(f"   👤 {user.username} ({user.email}) - {user.role}")
                
            return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_app_creation():
    """Тест создания приложения"""
    print("\n🚀 Тестирование создания приложения...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Проверяем конфигурацию
        assert 'SECRET_KEY' in app.config
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
        
        print("✅ Приложение создано успешно")
        print(f"   SECRET_KEY: {'установлен' if app.config['SECRET_KEY'] else 'отсутствует'}")
        print(f"   DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Проверяем зарегистрированные блюпринты
        blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"   Зарегистрированные блюпринты: {blueprints}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        return False

def test_routes():
    """Тест маршрутов"""
    print("\n🌐 Тестирование маршрутов...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Тест главной страницы
            response = client.get('/')
            print(f"✅ GET / - Status: {response.status_code}")
            
            # Тест аутентификации (должен вернуть ошибку без данных)
            response = client.post('/auth/login', json={})
            print(f"✅ POST /auth/login - Status: {response.status_code}")
            
            # Тест API (должен вершить ошибку без авторизации)
            response = client.get('/api/areas')
            print(f"✅ GET /api/areas - Status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования маршрутов: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Начало тестирования бэкенда системы 5С")
    print("=" * 60)
    
    success = True
    success &= test_imports()
    success &= test_app_creation() 
    success &= test_database()
    success &= test_routes()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Все базовые тесты пройдены успешно!")
        print("\n📝 Дальнейшие действия:")
        print("   1. Установите requests: pip install requests")
        print("   2. Запустите сервер: python run.py") 
        print("   3. В отдельном терминале запустите: python test_backend.py")
    else:
        print("❌ Есть проблемы, которые нужно исправить")
        print("\n🔧 Проверьте:")
        print("   - Все ли файлы созданы в папке app/")
        print("   - Правильность импортов в __init__.py")
        print("   - Выполнен ли fix_database.py")