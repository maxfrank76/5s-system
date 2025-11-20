from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

# Импортируем модели
from models import db, User, Department, Checklist, SelfCheck, Audit, Remark

app = Flask(__name__)
app.config['SECRET_KEY'] = '5s-system-tz-version'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///5s_tz_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# HTML шаблон для десктопного интерфейса
DESKTOP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система 5С - Производство</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f5f8fa; 
            min-height: 100vh;
        }
        .app-container {
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }
        .sidebar {
            background: #2c3e50;
            color: white;
            padding: 2rem 1rem;
        }
        .main-content {
            padding: 2rem;
            background: white;
        }
        .login-container {
            max-width: 500px;
            margin: 100px auto;
            background: white;
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .nav-item {
            padding: 1rem 1.5rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .nav-item:hover {
            background: #34495e;
        }
        .nav-item.active {
            background: #3498db;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e1e8ed;
        }
        .user-panel {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #3498db;
        }
        .hidden { display: none; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        input, select { 
            width: 100%; padding: 12px; border: 2px solid #e1e8ed; 
            border-radius: 8px; font-size: 16px; 
        }
        button { 
            width: 100%; padding: 15px; background: #3498db; color: white;
            border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="loginScreen">
        <div class="login-container">
            <h1 style="text-align: center; margin-bottom: 2rem; color: #2c3e50;">🏭 Система 5С</h1>
            <div class="form-group">
                <label>Имя пользователя:</label>
                <input type="text" id="username" value="worker1">
            </div>
            <div class="form-group">
                <label>Пароль:</label>
                <input type="password" id="password" value="worker1123">
            </div>
            <button onclick="login()">Войти в систему</button>
            <div id="loginError" style="color: #e74c3c; margin-top: 1rem; text-align: center;"></div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
                <h4>Тестовые пользователи (все пароли: username123):</h4>
                <p>👷 worker1 - Работник</p>
                <p>🔍 auditor1 - Аудитор</p>
                <p>👨‍💼 manager1 - Руководитель</p>
                <p>⚙️ admin - Администратор</p>
                <p>🎯 quality_dir - Директор по качеству</p>
            </div>
        </div>
    </div>

    <div id="mainApp" class="hidden">
        <div class="app-container">
            <div class="sidebar">
                <h3 style="margin-bottom: 2rem; padding: 0 1rem;">Навигация</h3>
                <div class="nav-item active" onclick="showSection('dashboard')">📊 Дашборд</div>
                <div class="nav-item" onclick="showSection('selfCheck')">✅ Самопроверка</div>
                <div class="nav-item" onclick="showSection('audits')">🔍 Аудиты</div>
                <div class="nav-item" onclick="showSection('remarks')">📋 Замечания</div>
                <div class="nav-item" onclick="showSection('reports')">📈 Отчеты</div>
                <div class="nav-item" id="adminNav" onclick="showSection('admin')" style="display: none;">⚙️ Администрирование</div>
            </div>
            
            <div class="main-content">
                <div id="dashboardSection">
                    <div class="user-panel">
                        <h2>Добро пожаловать, <span id="userName"></span>!</h2>
                        <p>Роль: <span id="userRole"></span> | Подразделение: <span id="userDepartment"></span></p>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Статистика системы</h3>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <h3>✅</h3>
                                <h2 id="statsSelfChecks">0</h2>
                                <p>Самопроверок</p>
                            </div>
                            <div class="stat-card">
                                <h3>🔍</h3>
                                <h2 id="statsAudits">0</h2>
                                <p>Аудитов</p>
                            </div>
                            <div class="stat-card">
                                <h3>📋</h3>
                                <h2 id="statsRemarks">0</h2>
                                <p>Замечаний</p>
                            </div>
                            <div class="stat-card">
                                <h3>✔️</h3>
                                <h2 id="statsResolved">0</h2>
                                <p>Решено</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Остальные секции -->
                <div id="selfCheckSection" class="hidden card">
                    <h3>✅ Самопроверка 5С</h3>
                    <p>Функциональность в разработке...</p>
                </div>

                <div id="auditsSection" class="hidden card">
                    <h3>🔍 Аудиты 5С</h3>
                    <p>Функциональность в разработке...</p>
                </div>

                <div id="remarksSection" class="hidden card">
                    <h3>📋 Замечания</h3>
                    <p>Функциональность в разработке...</p>
                </div>

                <div id="reportsSection" class="hidden card">
                    <h3>📈 Отчеты</h3>
                    <p>Функциональность в разработке...</p>
                </div>

                <div id="adminSection" class="hidden card">
                    <h3>⚙️ Администрирование</h3>
                    <p>Функциональность в разработке...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentUser = data.user;
                    
                    // Переключаем экраны
                    document.getElementById('loginScreen').classList.add('hidden');
                    document.getElementById('mainApp').classList.remove('hidden');
                    
                    // Обновляем информацию
                    document.getElementById('userName').textContent = currentUser.username;
                    document.getElementById('userRole').textContent = data.user.role_display;
                    document.getElementById('userDepartment').textContent = data.user.department_name || 'Не назначено';
                    
                    // Показываем админ-панель для админов
                    if (['admin', 'quality_director', 'production_director'].includes(currentUser.role)) {
                        document.getElementById('adminNav').style.display = 'block';
                    }
                    
                    loadDashboardStats();
                    
                } else {
                    document.getElementById('loginError').textContent = 'Ошибка входа';
                }
            } catch (error) {
                document.getElementById('loginError').textContent = 'Ошибка сети';
            }
        }
        
        function showSection(sectionName) {
            // Скрываем все секции
            document.querySelectorAll('.main-content > div').forEach(section => {
                section.classList.add('hidden');
            });
            // Показываем нужную
            document.getElementById(sectionName + 'Section').classList.remove('hidden');
            
            // Обновляем навигацию
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        async function loadDashboardStats() {
            try {
                const response = await fetch('/api/dashboard/stats');
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('statsSelfChecks').textContent = data.self_checks;
                    document.getElementById('statsAudits').textContent = data.audits;
                    document.getElementById('statsRemarks').textContent = data.remarks;
                    document.getElementById('statsResolved').textContent = data.resolved_remarks;
                }
            } catch (error) {
                console.error('Ошибка загрузки статистики:', error);
            }
        }
        
        async function logout() {
            try {
                await fetch('/auth/logout', {method: 'POST'});
                location.reload();
            } catch (error) {
                console.error('Ошибка выхода:', error);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return DESKTOP_TEMPLATE

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({
            'message': 'Вход выполнен успешно',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'role_display': user.get_role_display(),
                'department_name': user.department.name if user.department else None
            }
        })
    
    return jsonify({'message': 'Неверные учетные данные'}), 401

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Выход выполнен успешно'})

@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    stats = {
        'self_checks': SelfCheck.query.count(),
        'audits': Audit.query.count(),
        'remarks': Remark.query.count(),
        'resolved_remarks': Remark.query.filter_by(status='resolved').count()
    }
    return jsonify(stats)

def init_database():
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            # Создаем структуру подразделений
            production = Department(name='Производственный цех №1', department_type='production')
            quality = Department(name='Отдел технического контроля', department_type='quality')
            warehouse = Department(name='Склад', department_type='warehouse')
            
            db.session.add_all([production, quality, warehouse])
            db.session.commit()
            
            # Создаем пользователей по всем ролям из ТЗ
            users_data = [
                {'username': 'worker1', 'role': 'worker', 'department': production, 'position': 'Оператор станка'},
                {'username': 'worker2', 'role': 'worker', 'department': warehouse, 'position': 'Кладовщик'},
                {'username': 'auditor1', 'role': 'auditor', 'department': quality, 'position': 'Аудитор'},
                {'username': 'manager1', 'role': 'manager', 'department': production, 'position': 'Начальник цеха'},
                {'username': 'admin', 'role': 'admin', 'department': quality, 'position': 'Специалист по БП'},
                {'username': 'quality_dir', 'role': 'quality_director', 'department': quality, 'position': 'Директор по качеству'},
                {'username': 'production_dir', 'role': 'production_director', 'department': production, 'position': 'Директор по производству'}
            ]
            
            for user_data in users_data:
                user = User(
                    username=user_data['username'],
                    email=f"{user_data['username']}@company.com",
                    role=user_data['role'],
                    department_id=user_data['department'].id,
                    position=user_data['position']
                )
                user.set_password(user_data['username'] + '123')
                db.session.add(user)
            
            db.session.commit()
            print("✅ База данных инициализирована с тестовыми данными")

if __name__ == '__main__':
    print("🚀 Запуск системы 5С по ТЗ...")
    print("📊 База данных: 5s_tz_system.db")
    print("🌐 Доступно по: http://localhost:5001/")
    init_database()
    app.run(debug=True, port=5001)  # Запускаем на другом порту