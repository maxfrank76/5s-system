# test_setup.py - Проверка установки
import sys

def test_environment():
    """Проверка окружения"""
    print("🔧 ПРОВЕРКА ОКРУЖЕНИЯ ПРОЕКТА 5С")
    print("=" * 50)
    
    print(f"🐍 Python версия: {sys.version}")
    
    try:
        import flask
        print("✅ Flask установлен")
        print(f"   Версия: {flask.__version__}")
    except ImportError:
        print("❌ Flask НЕ установлен")
        return False
        
    try:
        import sqlalchemy
        print("✅ SQLAlchemy установлен")
        print(f"   Версия: {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy НЕ установлен")
        return False
        
    try:
        from PIL import Image
        print("✅ Pillow установлен")
        print(f"   Версия: {Image.__version__}")
    except ImportError:
        print("❌ Pillow НЕ установлен")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy установлен")
    except ImportError:
        print("❌ Flask-SQLAlchemy НЕ установлен")
        return False
        
    try:
        import flask_login
        print("✅ Flask-Login установлен")
    except ImportError:
        print("❌ Flask-Login НЕ установлен")
        return False
    
    print("\n🎉 Окружение настроено корректно!")
    return True

if __name__ == "__main__":
    success = test_environment()
    if not success:
        print("\n❌ Есть проблемы с установкой.")
        sys.exit(1)