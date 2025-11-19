import os
import sys

print("🔍 Диагностика импортов системы 5С")
print("=" * 50)

# Проверяем текущую директорию
print(f"\n📂 Текущая рабочая директория: {os.getcwd()}")

# Проверяем структуру папки app
app_path = os.path.join(os.getcwd(), 'app')
print(f"\n📁 Содержимое папки app/:")
if os.path.exists(app_path):
    files = os.listdir(app_path)
    for file in sorted(files):
        file_path = os.path.join(app_path, file)
        file_type = "📄 файл" if os.path.isfile(file_path) else "📁 папка"
        print(f"   {file_type} {file}")
else:
    print("   ❌ Папка app не существует!")

# Проверяем критически важные файлы
print(f"\n🔍 Проверка критических файлов:")
critical_files = {
    'app/__init__.py': 'Основной инициализационный файл',
    'app/models.py': 'Модели базы данных', 
    'app/auth.py': 'Аутентификация',
    'app/api.py': 'API endpoints',
    'app/main.py': 'Основные маршруты'
}

for file_path, description in critical_files.items():
    full_path = os.path.join(os.getcwd(), file_path)
    if os.path.exists(full_path):
        print(f"   ✅ {file_path} - существует ({description})")
    else:
        print(f"   ❌ {file_path} - ОТСУТСТВУЕТ ({description})")

# Проверяем __init__.py подробнее
init_path = os.path.join(app_path, '__init__.py')
print(f"\n📄 Анализ app/__init__.py:")
if os.path.exists(init_path):
    print("   ✅ Файл существует")
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем ключевые элементы
        checks = {
            'create_app': 'Функция create_app',
            'db = SQLAlchemy()': 'Инициализация базы данных',
            'login_manager = LoginManager()': 'Инициализация менеджера логина',
            'from app.main import main': 'Импорт main блюпринта',
            'from app.auth import auth': 'Импорт auth блюпринта', 
            'from app.api import api': 'Импорт api блюпринта'
        }
        
        for key, description in checks.items():
            if key in content:
                print(f"      ✅ {description} - найдено")
            else:
                print(f"      ❌ {description} - НЕ найдено")
                
    except Exception as e:
        print(f"   ❌ Ошибка чтения файла: {e}")
else:
    print("   ❌ Файл НЕ существует")

# Пробуем импортировать
print(f"\n🔄 Тестирование импортов:")
try:
    # Добавляем текущую директорию в PYTHONPATH
    sys.path.insert(0, os.getcwd())
    
    from app import create_app
    print("   ✅ from app import create_app - УСПЕХ")
    
    app = create_app()
    print("   ✅ create_app() - УСПЕХ")
    
    # Проверяем конфигурацию
    with app.app_context():
        print("   ✅ Контекст приложения - УСПЕХ")
        
except ImportError as e:
    print(f"   ❌ ImportError: {e}")
except Exception as e:
    print(f"   ❌ Другая ошибка: {e}")

print(f"\n📋 Рекомендации:")
if not os.path.exists(init_path):
    print("   1. Убедитесь что файл app/__init__.py существует")
    print("   2. Проверьте что имя файла __init__.py (с двойным подчеркиванием)")
else:
    print("   1. Проверьте содержимое app/__init__.py")
    print("   2. Убедитесь что все необходимые импорты присутствуют")

print(f"\n" + "=" * 50)