import requests
import json

BASE_URL = "http://localhost:5000"

def test_connection():
    """Тест подключения к серверу"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Сервер работает")
        print(f"Ответ: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_auth():
    """Тест аутентификации"""
    print("\n🔐 Тестирование аутентификации...")
    
    # Тестовые данные для входа
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "user1", "password": "user123"},
        {"username": "manager1", "password": "manager123"}
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Успешный вход: {user_data['username']}")
                print(f"   Пользователь: {data['user']['username']} ({data['user']['role']})")
                
                # Сохраняем cookies для следующих запросов
                session = requests.Session()
                session.cookies = response.cookies
                
                # Тест получения профиля
                profile_response = session.get(f"{BASE_URL}/auth/profile")
                if profile_response.status_code == 200:
                    print(f"✅ Профиль получен: {profile_response.json()['username']}")
                else:
                    print(f"❌ Ошибка получения профиля: {profile_response.status_code}")
                
                # Тест выхода
                logout_response = session.post(f"{BASE_URL}/auth/logout")
                if logout_response.status_code == 200:
                    print(f"✅ Выход выполнен успешно")
                else:
                    print(f"❌ Ошибка выхода: {logout_response.status_code}")
                    
            else:
                print(f"❌ Ошибка входа для {user_data['username']}: {response.status_code}")
                print(f"   Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка при тесте аутентификации: {e}")

def test_api_endpoints():
    """Тест API endpoints"""
    print("\n🌐 Тестирование API endpoints...")
    
    # Сначала логинимся как админ
    session = requests.Session()
    login_response = session.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ Не удалось войти для тестирования API")
        return
    
    print("✅ Успешный вход для тестирования API")
    
    # Тест получения участков
    try:
        areas_response = session.get(f"{BASE_URL}/api/areas")
        if areas_response.status_code == 200:
            areas = areas_response.json()
            print(f"✅ Участки получены: {len(areas)} шт.")
        else:
            print(f"❌ Ошибка получения участков: {areas_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при получении участков: {e}")
    
    # Тест получения статистики
    try:
        stats_response = session.get(f"{BASE_URL}/api/dashboard/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Статистика получена:")
            print(f"   Участки: {stats['total_areas']}")
            print(f"   Проверки: {stats['total_checks']}")
            print(f"   Аудиты: {stats['total_audits']}")
        else:
            print(f"❌ Ошибка получения статистики: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
    
    # Тест получения пользователей (только для админа)
    try:
        users_response = session.get(f"{BASE_URL}/api/users")
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ Пользователи получены: {len(users)} шт.")
        else:
            print(f"❌ Ошибка получения пользователей: {users_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")

def test_role_permissions():
    """Тест ролевой системы"""
    print("\n👥 Тестирование ролевой системы...")
    
    # Тестируем доступ пользователя user1
    session = requests.Session()
    login_response = session.post(
        f"{BASE_URL}/auth/login",
        json={"username": "user1", "password": "user123"},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        print("✅ Успешный вход как user1")
        
        # Пользователь user1 не должен иметь доступ к списку пользователей
        users_response = session.get(f"{BASE_URL}/api/users")
        if users_response.status_code == 403:
            print("✅ Ролевая система работает: user1 не может получить список пользователей")
        else:
            print(f"❌ Неожиданный ответ для user1: {users_response.status_code}")
    else:
        print("❌ Не удалось войти как user1")

if __name__ == "__main__":
    print("🚀 Начало тестирования бэкенда системы 5С")
    print("=" * 50)
    
    if test_connection():
        test_auth()
        test_api_endpoints()
        test_role_permissions()
    
    print("\n" + "=" * 50)
    print("Тестирование завершено!")