from app import create_app, db

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Создание таблиц базы данных...")
        
        # Получаем модели из app контекста
        User = app.models['User']
        Area5S = app.models['Area5S']
        
        # Создаем все таблиды
        db.create_all()
        
        print("✅ Таблицы созданы")
        
        # Создаем тестового администратора
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@5s-system.com',
                role='admin',
                department='Администрация',
                position='Системный администратор'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Создаем тестового пользователя
            user = User(
                username='user1',
                email='user1@company.com',
                role='user',
                department='Производство',
                position='Оператор'
            )
            user.set_password('user123')
            db.session.add(user)
            
            # Создаем тестового менеджера
            manager = User(
                username='manager1',
                email='manager1@company.com',
                role='manager',
                department='ОТК',
                position='Менеджер качества'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            
            db.session.commit()
            print("✅ Тестовые пользователи созданы")
            
            # Создаем тестовые участки
            area1 = Area5S(
                name='Производственный цех №1',
                description='Основной производственный цех',
                department='Производство',
                location='Здание А, этаж 1',
                responsible_person_id=manager.id
            )
            db.session.add(area1)
            
            area2 = Area5S(
                name='Склад материалов',
                description='Склад сырья и материалов',
                department='Логистика', 
                location='Здание Б, этаж 1',
                responsible_person_id=manager.id
            )
            db.session.add(area2)
            
            db.session.commit()
            print("✅ Тестовые участки созданы")
            
            print("\n👥 Тестовые данные:")
            print("   👤 admin / admin123 (администратор)")
            print("   👤 user1 / user123 (пользователь)") 
            print("   👤 manager1 / manager123 (менеджер)")
            print("   🏭 Производственный цех №1")
            print("   🏭 Склад материалов")
        else:
            print("ℹ️  Данные уже существуют")
        
        # Проверяем количество
        user_count = User.query.count()
        area_count = Area5S.query.count()
        print(f"📊 Статистика: {user_count} пользователей, {area_count} участков")

if __name__ == '__main__':
    init_database()