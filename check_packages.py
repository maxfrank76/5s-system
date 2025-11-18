# check_packages.py - Проверка установленных пакетов
import sys

def check_package(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

print("📦 ПРОВЕРКА УСТАНОВЛЕННЫХ ПАКЕТОВ")
print("=" * 40)

packages = [
    "flask",
    "flask_sqlalchemy", 
    "flask_login",
    "PIL",
    "dotenv"
]

for package in packages:
    if check_package(package):
        print(f"✅ {package} - установлен")
    else:
        print(f"❌ {package} - НЕ установлен")

print(f"\n🐍 Python путь: {sys.executable}")
print(f"📁 Текущая папка: {sys.path[0]}")