from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

print("🚀 Запуск системы 5С с аутентификацией и фронтендом...")

# Удаляем старую базу данных если существует
if os.path.exists('5s_system.db'):
    os.remove('5s_system.db')
    print("🗑️  Старая база данных удалена")

# Создаем приложение
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///5s_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Обязательные методы для Flask-Login
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.is_active
    
    def is_anonymous(self):
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return self.role == role_name or self.role == 'admin'

    def get_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'position': self.position
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель участка
class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    location = db.Column(db.String(200))
    responsible_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    responsible_person = db.relationship('User', backref='responsible_areas')

    def get_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department': self.department,
            'location': self.location,
            'responsible_person': self.responsible_person.username if self.responsible_person else None
        }

# Маршруты API
@app.route('/')
def home():
    """Главная страница с фронтендом"""
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Система 5С</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px; display: flex; align-items: center; justify-content: center;
            }
            .container { 
                max-width: 400px; width: 100%; 
            }
            .card { 
                background: white; border-radius: 15px; padding: 30px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center;
            }
            h1 { color: white; margin-bottom: 30px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .logo { font-size: 4em; margin-bottom: 20px; }
            .btn { 
                display: block; width: 100%; padding: 15px; margin: 10px 0;
                background: linear-gradient(135deg, #007bff, #0056b3); color: white;
                border: none; border-radius: 8px; font-size: 16px; font-weight: 600;
                text-decoration: none; cursor: pointer; transition: transform 0.2s;
            }
            .btn:hover { transform: translateY(-2px); }
            .info { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 Система 5С</h1>
            <div class="card">
                <div class="logo">🔐</div>
                <h2>Добро пожаловать!</h2>
                <p style="margin: 20px 0; color: #666;">Система управления производственными участками</p>
                
                <a href="/app" class="btn">📱 Открыть веб-приложение</a>
                <a href="/api/docs" class="btn" style="background: linear-gradient(135deg, #28a745, #20c997);">🌐 API Документация</a>
                
                <div class="info">
                    <h4>Тестовые пользователи:</h4>
                    <p>👤 user1 / user1123</p>
                    <p>👨‍💼 manager / manager123</p>
                    <p>👑 admin / admin123</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/app')
def serve_app():
    """Веб-приложение 5С"""
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Система 5С - Приложение</title>
        <meta name="theme-color" content="#007bff">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { max-width: 400px; margin: 0 auto; }
            .card { 
                background: white; border-radius: 15px; padding: 30px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px;
            }
            h1 { text-align: center; color: white; margin-bottom: 30px; font-size: 2em; }
            .logo { text-align: center; font-size: 3em; margin-bottom: 10px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
            input { 
                width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; 
                font-size: 16px; transition: border-color 0.3s;
            }
            input:focus { outline: none; border-color: #007bff; }
            button { 
                width: 100%; padding: 12px; background: linear-gradient(135deg, #007bff, #0056b3); 
                color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; 
                cursor: pointer; transition: transform 0.2s;
            }
            button:hover { transform: translateY(-2px); }
            .error { 
                color: #dc3545; text-align: center; margin-top: 10px; padding: 10px; 
                background: #f8d7da; border-radius: 5px; display: none;
            }
            .dashboard { display: none; }
            .user-info { 
                background: linear-gradient(135deg, #28a745, #20c997); color: white; 
                padding: 15px; border-radius: 10px; margin-bottom: 20px;
            }
            .nav-buttons { display: grid; gap: 10px; margin-bottom: 20px; }
            .nav-btn { 
                background: white; border: 2px solid #007bff; color: #007bff; padding: 15px;
                border-radius: 10px; text-align: center; font-weight: 600; cursor: pointer;
                transition: all 0.3s;
            }
            .nav-btn:hover { background: #007bff; color: white; }
            .content-area { 
                background: white; border-radius: 10px; padding: 20px; min-height: 200px;
            }
            .area-item { 
                border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <h1>🏭 Система 5С</h1>
        
        <div class="container">
            <!-- Экран входа -->
            <div id="login-screen">
                <div class="card">
                    <div class="logo">🔐</div>
                    <h2 style="text-align: center; margin-bottom: 20px;">Вход в систему</h2>
                    
                    <div class="form-group">
                        <label for="username">Имя пользователя:</label>
                        <input type="text" id="username" placeholder="Введите имя пользователя" value="user1">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль:</label>
                        <input type="password" id="password" placeholder="Введите пароль" value="user1123">
                    </div>
                    
                    <button onclick="login()">Войти в систему</button>
                    
                    <div id="login-error" class="error"></div>
                </div>
            </div>
            
            <!-- Основной дашборд -->
            <div id="dashboard" class="dashboard">
                <div class="user-info">
                    <h3>Добро пожаловать, <span id="user-name"></span>!</h3>
                    <p>Роль: <span id="user-role"></span></p>
                </div>
                
                <div class="nav-buttons">
                    <button class="nav-btn" onclick="showSection('areas')">🏭 Участки</button>
                    <button class="nav-btn" onclick="showSection('stats')">📊 Статистика</button>
                    <button class="nav-btn" onclick="logout()">🚪 Выйти</button>
                </div>
                
                <!-- Секция участков -->
                <div id="areas-section" class="content-area">
                    <h3>Список участков</h3>
                    <button onclick="loadAreas()" style="margin: 10px 0; padding: 8px 15px; font-size: 14px;">🔄 Обновить</button>
                    <div id="areas-list"></div>
                </div>
                
                <!-- Секция статистики -->
                <div id="stats-section" class="content-area" style="display: none;">
                    <h3>Статистика системы</h3>
                    <button onclick="loadStats()" style="margin: 10px 0; padding: 8px 15px; font-size: 14px;">🔄 Обновить</button>
                    <div id="stats-content"></div>
                </div>
            </div>
        </div>

        <script>
            let currentUser = null;
            
            function showSection(sectionName) {
                document.querySelectorAll('.content-area').forEach(section => {
                    section.style.display = 'none';
                });
                document.getElementById(sectionName + '-section').style.display = 'block';
            }
            
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('login-error');
                
                errorDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password}),
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        currentUser = data.user;
                        
                        document.getElementById('login-screen').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'block';
                        
                        document.getElementById('user-name').textContent = currentUser.username;
                        document.getElementById('user-role').textContent = getRoleDisplay(currentUser.role);
                        
                        loadAreas();
                        showSection('areas');
                        
                    } else {
                        const errorData = await response.json();
                        errorDiv.textContent = errorData.message || 'Ошибка входа';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка сети: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            }
            
            async function loadAreas() {
                try {
                    const response = await fetch('/api/areas', {credentials: 'include'});
                    
                    if (response.ok) {
                        const data = await response.json();
                        const areasList = document.getElementById('areas-list');
                        
                        if (data.areas.length === 0) {
                            areasList.innerHTML = '<p>Нет доступных участков</p>';
                        } else {
                            areasList.innerHTML = data.areas.map(area => `
                                <div class="area-item">
                                    <h4>${area.name}</h4>
                                    <p><strong>Отдел:</strong> ${area.department}</p>
                                    <p><strong>Местоположение:</strong> ${area.location || 'Не указано'}</p>
                                    <p><strong>Ответственный:</strong> ${area.responsible_person || 'Не назначен'}</p>
                                    ${area.description ? `<p><strong>Описание:</strong> ${area.description}</p>` : ''}
                                </div>
                            `).join('');
                        }
                    }
                } catch (error) {
                    document.getElementById('areas-list').innerHTML = '<p>Ошибка загрузки участков</p>';
                }
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/api/dashboard/stats', {credentials: 'include'});
                    
                    if (response.ok) {
                        const data = await response.json();
                        document.getElementById('stats-content').innerHTML = `
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
                                    <h3>👥</h3>
                                    <h2>${data.users}</h2>
                                    <p>Пользователей</p>
                                </div>
                                <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center;">
                                    <h3>🏭</h3>
                                    <h2>${data.areas}</h2>
                                    <p>Участков</p>
                                </div>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('stats-content').innerHTML = '<p>Ошибка загрузки статистики</p>';
                }
            }
            
            async function logout() {
                try {
                    await fetch('/auth/logout', {method: 'POST', credentials: 'include'});
                    document.getElementById('login-screen').style.display = 'block';
                    document.getElementById('dashboard').style.display = 'none';
                    currentUser = null;
                } catch (error) {
                    console.error('Ошибка выхода:', error);
                }
            }
            
            function getRoleDisplay(role) {
                const roles = {'admin': 'Администратор', 'manager': 'Менеджер', 'user': 'Пользователь'};
                return roles[role] || role;
            }
            
            document.getElementById('password').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') login();
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/docs')
def api_docs():
    """Документация API"""
    return jsonify({
        'message': 'API системы 5С',
        'endpoints': {
            'POST /auth/login': 'Вход в систему',
            'POST /auth/logout': 'Выход из системы', 
            'GET /auth/profile': 'Профиль пользователя',
            'GET /api/areas': 'Список участков',
            'POST /api/areas': 'Создать участок (требуются права manager/admin)',
            'GET /api/dashboard/stats': 'Статистика системы'
        },
        'test_users': {
            'user1': 'user1123 (user)',
            'manager': 'manager123 (manager)',
            'admin': 'admin123 (admin)'
        }
    })

# Аутентификация
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Требуется имя пользователя и пароль'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        login_user(user, remember=True)
        return jsonify({
            'message': 'Вход выполнен успешно',
            'user': user.get_dict()
        })
    
    return jsonify({'message': 'Неверные учетные данные'}), 401

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Выход выполнен успешно'})

@app.route('/auth/profile')
@login_required
def profile():
    return jsonify({'user': current_user.get_dict()})

# API участков
@app.route('/api/areas')
@login_required
def get_areas():
    areas = Area.query.filter_by(is_active=True).all()
    return jsonify({'areas': [area.get_dict() for area in areas]})

@app.route('/api/areas', methods=['POST'])
@login_required
def create_area():
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        return jsonify({'message': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    area = Area(
        name=data['name'],
        description=data.get('description'),
        department=data.get('department'),
        location=data.get('location'),
        responsible_person_id=data.get('responsible_person_id')
    )
    db.session.add(area)
    db.session.commit()
    
    return jsonify({'message': 'Участок создан', 'area': area.get_dict()}), 201

# Статистика
@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    user_count = User.query.count()
    area_count = Area.query.count()
    
    return jsonify({
        'users': user_count,
        'areas': area_count,
        'message': 'Статистика системы'
    })

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    with app.app_context():
        print("🗄️ Создание таблиц...")
        
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ Таблицы созданы успешно")
            
            # Создаем тестовых пользователей
            if not User.query.filter_by(username='admin').first():
                users_data = [
                    {'username': 'admin', 'email': 'admin@5s.com', 'role': 'admin', 'department': 'Администрация', 'position': 'Администратор'},
                    {'username': 'manager', 'email': 'manager@5s.com', 'role': 'manager', 'department': 'ОТК', 'position': 'Менеджер'},
                    {'username': 'user1', 'email': 'user1@5s.com', 'role': 'user', 'department': 'Производство', 'position': 'Оператор'}
                ]
                
                for user_data in users_data:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        role=user_data['role'],
                        department=user_data['department'],
                        position=user_data['position']
                    )
                    user.set_password(user_data['username'] + '123')
                    db.session.add(user)
                
                db.session.commit()
                print("✅ Тестовые пользователи созданы")
            else:
                print("ℹ️  Пользователи уже существуют")
            
            # Создаем тестовые участки
            if not Area.query.first():
                areas_data = [
                    {'name': 'Производственный цех №1', 'department': 'Производство', 'location': 'Здание А'},
                    {'name': 'Склад материалов', 'department': 'Логистика', 'location': 'Здание Б'},
                    {'name': 'Зона сборки', 'department': 'Производство', 'location': 'Здание А, 2 этаж'}
                ]
                
                for area_data in areas_data:
                    area = Area(
                        name=area_data['name'],
                        department=area_data['department'],
                        location=area_data['location']
                    )
                    db.session.add(area)
                
                db.session.commit()
                print("✅ Тестовые участки созданы")
            else:
                print("ℹ️  Участки уже существуют")
            
            # Статистика
            user_count = User.query.count()
            area_count = Area.query.count()
            print(f"📊 Статистика: {user_count} пользователей, {area_count} участков")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации базы данных: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("🔧 Инициализация системы...")
    init_database()
    
    print("\n🌐 Сервер запущен!")
    print("   Главная страница: http://localhost:5000/")
    print("   Веб-приложение: http://localhost:5000/app")
    print("   API документация: http://localhost:5000/api/docs")
    
    app.run(debug=True, host='0.0.0.0', port=5000)