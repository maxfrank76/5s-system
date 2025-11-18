# init_data.py - Начальные данные для теста
from app import create_app
from app.models import db, User, Role, Department

def create_initial_data():
    app = create_app()
    
    with app.app_context():
        # Создаем базовые роли
        roles = [
            Role(name='worker', description='Работник'),
            Role(name='auditor', description='Аудитор'),
            Role(name='department_head', description='Руководитель подразделения'),
            Role(name='admin', description='Администратор системы'),
        ]
        
        for role in roles:
            db.session.add(role)
        
        # Создаем тестовое подразделение
        dept = Department(name='Тестовый цех', department_type='production')
        db.session.add(dept)
        
        db.session.commit()
        print("✅ Начальные данные созданы!")
        print("📊 Роли: работник, аудитор, руководитель, админ")
        print("🏭 Подразделение: Тестовый цех")

if __name__ == '__main__':
    create_initial_data()