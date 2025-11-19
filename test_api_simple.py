import requests
import time

BASE_URL = "http://localhost:5000"

def wait_for_server():
    """Ждем пока сервер запустится"""
    print("⏳ Ожидание запуска сервера...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Сервер запущен!")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ Сервер не запустился")
    return False

def test_system():
    print("🧪 Тестирование системы 5С")
    print("=" * 40)
    
    if not wait_for_server():
        return False
    
    session = requests.Session()
    
    try:
        # 1. Вход пользователя
        print("\n1. Вход в систему...")
        response = session.post(f"{BASE_URL}/auth/login", 
                              json={"username": "user1", "password": "user1123"})
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Вход успешен: {user_data['user']['username']}")
        else:
            print(f"   ❌ Ошибка входа: {response.status_code}")
            return False
        
        # 2. Проверка профиля
        print("\n2. Проверка профиля...")
        response = session.get(f"{BASE_URL}/auth/profile")
        if response.status_code == 200:
            print(f"   ✅ Профиль работает")
        
        # 3. Получение участков
        print("\n3. Получение участков...")
        response = session.get(f"{BASE_URL}/api/areas")
        if response.status_code == 200:
            areas = response.json()['areas']
            print(f"   ✅ Участки: {len(areas)} шт.")
        
        # 4. Статистика
        print("\n4. Проверка статистики...")
        response = session.get(f"{BASE_URL}/api/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Статистика: {stats['users']} пользователей, {stats['areas']} участков")
        
        # 5. Выход
        print("\n5. Выход из системы...")
        response = session.post(f"{BASE_URL}/auth/logout")
        if response.status_code == 200:
            print(f"   ✅ Выход выполнен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if test_system():
        print("\n🎉 Система 5С работает корректно!")
    else:
        print("\n❌ Есть проблемы с системой")