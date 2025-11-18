# simple_test.py - Простой тест базы данных
import os
import sys

# Добавляем текущую папку в путь Python
sys.path.append(os.path.dirname(__file__))

def test_basic_import():
    print("🔧 БАЗОВЫЙ ТЕСТ ИМПОРТОВ")
    print("=" * 40)
    
    try:
        # Проверяем импорт конфигурации
        from config import Config
        print("✅ config.py импортируется")
    except ImportError as e:
        print(f"❌ Ошибка импорта config: {e}")
        return False
    
    try:
        # Проверяем импорт моделей
        from app.models import db, User
        print("✅ Модели импортируются")
    except ImportError as e:
        print(f"❌ Ошибка импорта моделей: {e}")
        return False
        
    print("🎉 Базовые импорты работают!")
    return True

if __name__ == "__main__":
    test_basic_import()