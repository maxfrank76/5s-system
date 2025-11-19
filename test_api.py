import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("🧪 Тестирование API системы 5С")
    print("=" * 50)
    
    # Создаем сессию для сохранения cookies
    session = requests.Session()
    
    try:
        # 1. Тест главной страницы
        print("\n1. Тест главной страницы")
        response = session.get(f"{BASE_URL}/")
        print(f"   ✅ GET / - {response.status_code}: {response.json()}")
        
        # 2. Тест аутентификации
        print("\n2. Тест аутентификации")
        login_data = {"username": "user1", "password": "user1123"}
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Вход успешен: {user_data['user']['username']} ({user_data['user']['role']})")
        else:
            print(f"   ❌ Ошибка входа: {response.status_code} - {response.text}")
            return False
        
        # 3. Тест профиля
        print("\n3. Тест профиля пользователя")
        response = session.get(f"{BASE_URL}/auth/profile")
        if response.status_code == 200:
            print(f"   ✅ Профиль получен: {response.json()['user']['username']}")
        else:
            print(f"   ❌ Ошибка профиля: {response.status_code}")
        
        # 4. Тест получения участков
        print("\n4. Тест получения участков")
        response = session.get(f"{BASE_URL}/api/areas")
        if response.status_code == 200:
            areas = response.json()['areas']
            print(f"   ✅ Участки получены: {len(areas)} шт.")
            for area in areas:
                print(f"      🏭 {area['name']} ({area['department']})")
        else:
            print(f"   ❌ Ошибка получения участков: {response.status_code}")
        
        # 5. Тест статистики
        print("\n5. Тест статистики")
        response = session.get(f"{BASE_URL}/api/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Статистика: {stats['users']} пользователей, {stats['areas']} участков")
        else:
            print(f"   ❌ Ошибка статистики: {response.status_code}")
        
        # 6. Тест выхода
        print("\n6. Тест выхода из системы")
        response = session.post(f"{BASE_URL}/auth/logout")
        if response.status_code == 200:
            print(f"   ✅ Выход выполнен успешно")
        else:
            print(f"   ❌ Ошибка выхода: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования API")
    if test_api():
        print("\n🎉 Все тесты пройдены успешно! Система 5С готова к работе.")
    else:
        print("\n❌ Есть проблемы с API")