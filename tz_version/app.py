from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

# Импортируем модели
from models import db, User, Department, Checklist, CriteriaGroup, Criterion, SelfCheck, SelfCheckAnswer, Audit, Remark
from self_check import create_sample_checklists, get_self_checklist, create_self_check, save_self_check_answers

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
        
        /* Шапка */
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logout-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .logout-btn:hover {
            background: #c0392b;
        }
        
        /* Основной контейнер */
        .app-container {
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: calc(100vh - 80px);
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
        
        /* Экран входа */
        .login-container {
            max-width: 500px;
            margin: 100px auto;
            background: white;
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        /* Навигация */
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
        
        /* Карточки */
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
        
        /* Статистика */
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
        
        /* Формы */
        .hidden { display: none; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; }
        
        input, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e1e8ed; 
            border-radius: 8px; 
            font-size: 16px; 
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #3498db;
        }
        
        button { 
            width: 100%; 
            padding: 15px; 
            background: #3498db; 
            color: white;
            border: none; 
            border-radius: 8px; 
            font-size: 16px; 
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #2980b9;
        }
        
        .nav-btn {
            background: white;
            border: 2px solid #3498db;
            color: #3498db;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .nav-btn:hover {
            background: #3498db;
            color: white;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 1rem;
            text-align: center;
            padding: 10px;
            background: #fdf2f2;
            border-radius: 6px;
            border: 1px solid #f5c6cb;
        }
        
        .success {
            color: #155724;
            margin-top: 1rem;
            text-align: center;
            padding: 10px;
            background: #d4edda;
            border-radius: 6px;
            border: 1px solid #c3e6cb;
        }
        
        /* Стили для чек-листа */
        .criterion-group {
            margin: 2rem 0;
            padding: 1.5rem;
            border: 2px solid #e9ecef;
            border-radius: 10px;
        }
        
        .criterion-item {
            margin: 1rem 0;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <!-- Экран входа -->
    <div id="loginScreen">
        <div class="login-container">
            <h1 style="text-align: center; margin-bottom: 2rem; color: #2c3e50;">🏭 Система 5С</h1>
            
            <div class="form-group">
                <label>Выберите пользователя:</label>
                <select id="usernameSelect" onchange="onUserSelect()">
                    <option value="">-- Выберите пользователя --</option>
                    <option value="worker1">👷 worker1 - Работник (Цех)</option>
                    <option value="worker2">👷 worker2 - Работник (Склад)</option>
                    <option value="auditor1">🔍 auditor1 - Аудитор</option>
                    <option value="manager1">👨‍💼 manager1 - Руководитель цеха</option>
                    <option value="admin">⚙️ admin - Администратор</option>
                    <option value="quality_dir">🎯 quality_dir - Директор по качеству</option>
                    <option value="production_dir">🏭 production_dir - Директор по производству</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Пароль:</label>
                <input type="password" id="password" placeholder="Пароль заполнится автоматически" readonly>
            </div>
            
            <button onclick="login()">Войти в систему</button>
            <div id="loginError" class="error"></div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
                <h4 style="margin-bottom: 1rem;">💡 Подсказка:</h4>
                <p>Выберите пользователя из списка → пароль заполнится автоматически → нажмите "Войти"</p>
                <p style="margin-top: 0.5rem; font-size: 0.9em; color: #666;">Все пароли: <strong>username123</strong></p>
            </div>
        </div>
    </div>

    <!-- Основной интерфейс -->
    <div id="mainApp" class="hidden">
        <!-- Шапка с кнопкой выхода -->
        <div class="header">
            <h1>🏭 Система 5С - Производство</h1>
            <div class="header-actions">
                <span id="currentUserInfo">Пользователь не авторизован</span>
                <button onclick="logout()" class="logout-btn">🚪 Выйти</button>
            </div>
        </div>
        
        <div class="app-container">
            <!-- Боковая панель навигации -->
            <div class="sidebar">
                <h3 style="margin-bottom: 2rem; padding: 0 1rem;">Навигация</h3>
                <div class="nav-item active" onclick="showSection('dashboard')">📊 Дашборд</div>
                <div class="nav-item" onclick="showSection('selfCheck')">✅ Самопроверка</div>
                <div class="nav-item" onclick="showSection('audits')">🔍 Аудиты</div>
                <div class="nav-item" onclick="showSection('remarks')">📋 Замечания</div>
                <div class="nav-item" onclick="showSection('reports')">📈 Отчеты</div>
                <div class="nav-item" id="adminNav" onclick="showSection('admin')" style="display: none;">⚙️ Администрирование</div>
            </div>
            
            <!-- Основной контент -->
            <div class="main-content">
                <!-- Дашборд -->
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

                <!-- Самопроверка -->
                <div id="selfCheckSection" class="hidden">
                    <div class="card">
                        <h3>✅ Самопроверка 5С</h3>
                        
                        <!-- Информация о текущей самопроверке -->
                        <div id="selfCheckInfo" class="hidden" style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <h4>📝 Активная самопроверка</h4>
                            <p>Заполните все критерии и нажмите "Завершить проверку"</p>
                        </div>
                        
                        <!-- История самопроверок -->
                        <div id="selfCheckHistory" class="hidden">
                            <h4>📊 История самопроверок</h4>
                            <div id="historyList"></div>
                        </div>
                        
                        <!-- Кнопки управления -->
                        <div style="display: flex; gap: 1rem; margin-bottom: 2rem;">
                            <button onclick="startSelfCheck()" id="startSelfCheckBtn" class="nav-btn">🔄 Начать новую проверку</button>
                            <button onclick="loadSelfCheckHistory()" class="nav-btn">📋 Показать историю</button>
                        </div>
                        
                        <!-- Чек-лист -->
                        <div id="checklistContainer" class="hidden">
                            <div id="checklistContent"></div>
                            <button onclick="submitSelfCheck()" style="margin-top: 2rem; background: #28a745;">✅ Завершить проверку</button>
                        </div>
                        
                        <!-- Сообщения -->
                        <div id="selfCheckMessage" style="display: none;"></div>
                    </div>
                </div>

                <!-- Аудиты -->
                <div id="auditsSection" class="hidden card">
                    <h3>🔍 Аудиты 5С</h3>
                    <p>Функциональность аудитов будет реализована в следующем обновлении</p>
                    <p style="margin-top: 1rem; color: #666;">Аудиторы проводят плановые и внеплановые аудиты по полному чек-листу, создают замечания</p>
                </div>

                <!-- Замечания -->
                <div id="remarksSection" class="hidden card">
                    <h3>📋 Замечания</h3>
                    <p>Функциональность управления замечаниями будет реализована в следующем обновлении</p>
                    <p style="margin-top: 1rem; color: #666;">Жизненный цикл замечания: Выявлено → Назначен ответственный → Устранено → Проверено/Закрыто</p>
                </div>

                <!-- Отчеты -->
                <div id="reportsSection" class="hidden card">
                    <h3>📈 Отчеты</h3>
                    <p>Функциональность отчетности будет реализована в следующем обновлении</p>
                    <p style="margin-top: 1rem; color: #666;">Сводки по баллам, динамика, списки замечаний, отчеты по самопроверкам</p>
                </div>

                <!-- Администрирование -->
                <div id="adminSection" class="hidden card">
                    <h3>⚙️ Администрирование</h3>
                    <p>Панель администратора будет реализована в следующем обновлении</p>
                    <p style="margin-top: 1rem; color: #666;">Управление пользователями, ролями, структурой подразделений, чек-листами, графиком аудитов</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let currentSelfCheckId = null;

        // Обработчик выбора пользователя
        function onUserSelect() {
            const select = document.getElementById('usernameSelect');
            const username = select.value;
            
            // Автозаполняем пароль
            if (username) {
                document.getElementById('password').value = username + '123';
            } else {
                document.getElementById('password').value = '';
            }
        }

        // Функция входа
        async function login() {
            const username = document.getElementById('usernameSelect').value;
            const password = document.getElementById('password').value;
            
            if (!username) {
                document.getElementById('loginError').textContent = 'Пожалуйста, выберите пользователя из списка';
                return;
            }
            
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
                    
                    // Обновляем информацию в шапке
                    document.getElementById('currentUserInfo').textContent = 
                        `${currentUser.username} (${data.user.role_display})`;
                    document.getElementById('userName').textContent = currentUser.username;
                    document.getElementById('userRole').textContent = data.user.role_display;
                    document.getElementById('userDepartment').textContent = data.user.department_name || 'Не назначено';
                    
                    // Показываем админ-панель для соответствующих ролей
                    if (['admin', 'quality_director', 'production_director'].includes(currentUser.role)) {
                        document.getElementById('adminNav').style.display = 'block';
                    }
                    
                    // Загружаем статистику
                    loadDashboardStats();
                    
                } else {
                    const errorData = await response.json();
                    document.getElementById('loginError').textContent = errorData.message || 'Ошибка входа. Проверьте правильность данных.';
                }
            } catch (error) {
                document.getElementById('loginError').textContent = 'Ошибка сети: ' + error.message;
            }
        }
        
        // Показать секцию
        function showSection(sectionName) {
            // Скрываем все секции
            document.querySelectorAll('.main-content > div').forEach(section => {
                section.classList.add('hidden');
            });
            // Показываем нужную секцию
            document.getElementById(sectionName + 'Section').classList.remove('hidden');
            
            // Обновляем активную навигацию
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        // Загрузка статистики
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
        
        // Выход из системы
        async function logout() {
            try {
                await fetch('/auth/logout', {method: 'POST'});
                
                // Сбрасываем форму
                document.getElementById('usernameSelect').value = '';
                document.getElementById('password').value = '';
                document.getElementById('loginError').textContent = '';
                
                // Переключаем экраны
                document.getElementById('loginScreen').classList.remove('hidden');
                document.getElementById('mainApp').classList.add('hidden');
                
                currentUser = null;
            } catch (error) {
                console.error('Ошибка выхода:', error);
            }
        }

        // ========== ФУНКЦИОНАЛ САМОПРОВЕРКИ ==========

        // Начать самопроверку
        async function startSelfCheck() {
            try {
                const response = await fetch('/api/self-check/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentSelfCheckId = data.self_check_id;
                    
                    // Показываем информацию о самопроверке
                    document.getElementById('selfCheckInfo').classList.remove('hidden');
                    document.getElementById('startSelfCheckBtn').style.display = 'none';
                    document.getElementById('selfCheckHistory').classList.add('hidden');
                    
                    // Загружаем чек-лист
                    await loadChecklist();
                    
                } else {
                    const errorData = await response.json();
                    showSelfCheckMessage(errorData.error, 'error');
                }
            } catch (error) {
                showSelfCheckMessage('Ошибка сети: ' + error.message, 'error');
            }
        }

        // Загрузить чек-лист
        async function loadChecklist() {
            try {
                const response = await fetch('/api/self-check/checklist');
                
                if (response.ok) {
                    const data = await response.json();
                    renderChecklist(data);
                    document.getElementById('checklistContainer').classList.remove('hidden');
                } else {
                    const errorData = await response.json();
                    showSelfCheckMessage(errorData.error, 'error');
                }
            } catch (error) {
                showSelfCheckMessage('Ошибка загрузки чек-листа: ' + error.message, 'error');
            }
        }

        // Отобразить чек-лист
        function renderChecklist(checklist) {
            const container = document.getElementById('checklistContent');
            let html = `<h4>${checklist.name}</h4>`;
            
            checklist.groups.forEach(group => {
                html += `
                    <div class="criterion-group">
                        <h5 style="color: #2c3e50; margin-bottom: 1rem;">${group.name}</h5>
                `;
                
                group.criteria.forEach(criterion => {
                    html += `
                        <div class="criterion-item">
                            <p style="margin-bottom: 0.5rem; font-weight: 500;">${criterion.description}</p>
                            <div style="display: flex; gap: 1rem; align-items: center;">
                                <span style="font-size: 0.9em; color: #666;">Оценка:</span>
                                <select id="criterion_${criterion.id}" style="width: auto;">
                                    <option value="">-- Выберите --</option>
                                    <option value="1">1 - Не выполняется</option>
                                    <option value="2">2 - Выполняется частично</option>
                                    <option value="3">3 - Выполняется удовлетворительно</option>
                                    <option value="4">4 - Выполняется хорошо</option>
                                    <option value="5">5 - Выполняется отлично</option>
                                </select>
                            </div>
                        </div>
                    `;
                });
                
                html += `</div>`;
            });
            
            container.innerHTML = html;
        }

        // Завершить самопроверку
        async function submitSelfCheck() {
            // Собираем ответы
            const answers = {};
            const selects = document.querySelectorAll('select[id^="criterion_"]');
            
            let allFilled = true;
            selects.forEach(select => {
                if (!select.value) {
                    allFilled = false;
                    select.style.borderColor = '#e74c3c';
                } else {
                    const criterionId = select.id.replace('criterion_', '');
                    answers[criterionId] = parseInt(select.value);
                    select.style.borderColor = '';
                }
            });
            
            if (!allFilled) {
                showSelfCheckMessage('Пожалуйста, оцените все критерии', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/api/self-check/${currentSelfCheckId}/submit`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({answers})
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showSelfCheckMessage(`✅ Самопроверка завершена! Ваш результат: ${data.total_score.toFixed(1)}%`, 'success');
                    
                    // Сбрасываем состояние
                    resetSelfCheckUI();
                    
                } else {
                    const errorData = await response.json();
                    showSelfCheckMessage(errorData.error, 'error');
                }
            } catch (error) {
                showSelfCheckMessage('Ошибка отправки: ' + error.message, 'error');
            }
        }

        // Загрузить историю самопроверок
        async function loadSelfCheckHistory() {
            try {
                const response = await fetch('/api/self-check/history');
                
                if (response.ok) {
                    const data = await response.json();
                    renderHistory(data.history);
                    document.getElementById('selfCheckHistory').classList.remove('hidden');
                    document.getElementById('checklistContainer').classList.add('hidden');
                    document.getElementById('selfCheckInfo').classList.add('hidden');
                }
            } catch (error) {
                showSelfCheckMessage('Ошибка загрузки истории: ' + error.message, 'error');
            }
        }

        // Отобразить историю
        function renderHistory(history) {
            const container = document.getElementById('historyList');
            
            if (history.length === 0) {
                container.innerHTML = '<p>История самопроверок пуста</p>';
                return;
            }
            
            let html = '';
            history.forEach(check => {
                const date = new Date(check.check_date).toLocaleDateString('ru-RU');
                const status = check.is_completed ? '✅ Завершена' : '🔄 В процессе';
                const score = check.total_score ? `${check.total_score.toFixed(1)}%` : 'Не оценена';
                
                html += `
                    <div style="padding: 1rem; margin: 0.5rem 0; background: white; border-radius: 8px; border-left: 4px solid #3498db;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${date}</strong> - ${check.department_name}
                            </div>
                            <div>
                                <span style="margin-right: 1rem;">${status}</span>
                                <strong>${score}</strong>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        // Сброс UI самопроверки
        function resetSelfCheckUI() {
            currentSelfCheckId = null;
            document.getElementById('selfCheckInfo').classList.add('hidden');
            document.getElementById('checklistContainer').classList.add('hidden');
            document.getElementById('selfCheckHistory').classList.add('hidden');
            document.getElementById('startSelfCheckBtn').style.display = 'block';
        }

        // Показать сообщение
        function showSelfCheckMessage(message, type) {
            const messageDiv = document.getElementById('selfCheckMessage');
            messageDiv.textContent = message;
            messageDiv.style.display = 'block';
            messageDiv.className = type === 'error' ? 'error' : 'success';
            
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }
        
        // Обработка нажатия Enter в поле пароля
        document.getElementById('password').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                login();
            }
        });
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
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
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

# ========== API ДЛЯ САМОПРОВЕРОК ==========

@app.route('/api/self-check/checklist')
@login_required
def get_self_check_checklist():
    """Получить чек-лист для самопроверки текущего пользователя"""
    if not current_user.department:
        print(f"❌ Пользователь {current_user.username} не привязан к подразделению")
        return jsonify({'error': 'Пользователь не привязан к подразделению'}), 400
    
    print(f"🔍 Поиск чек-листа для пользователя {current_user.username}")
    print(f"   Подразделение: {current_user.department.name}")
    print(f"   Тип подразделения: {current_user.department.department_type}")
    
    checklist = get_self_checklist(current_user.department.department_type)
    if not checklist:
        return jsonify({'error': 'Чек-лист для вашего подразделения не найден'}), 404
    
    # Формируем структурированные данные чек-листа
    checklist_data = {
        'id': checklist.id,
        'name': checklist.name,
        'groups': []
    }
    
    # ИСПРАВЛЕНИЕ: Используем query для сортировки групп
    groups = CriteriaGroup.query.filter_by(checklist_id=checklist.id).order_by(CriteriaGroup.order_index).all()
    
    for group in groups:
        group_data = {
            'id': group.id,
            'name': group.name,
            'criteria': []
        }
        
        # ИСПРАВЛЕНИЕ: Используем query для сортировки критериев
        criteria = Criterion.query.filter_by(group_id=group.id).order_by(Criterion.order_index).all()
        
        for criterion in criteria:
            criterion_data = {
                'id': criterion.id,
                'description': criterion.description
            }
            group_data['criteria'].append(criterion_data)
        
        checklist_data['groups'].append(group_data)
    
    print(f"✅ Чек-лист найден: {checklist.name} с {len(checklist_data['groups'])} группами")
    return jsonify(checklist_data)

@app.route('/api/self-check/start', methods=['POST'])
@login_required
def start_self_check():
    """Начать новую самопроверку"""
    if not current_user.department:
        return jsonify({'error': 'Пользователь не привязан к подразделению'}), 400
    
    checklist = get_self_checklist(current_user.department.department_type)
    if not checklist:
        return jsonify({'error': 'Чек-лист для вашего подразделения не найден'}), 404
    
    # Проверяем, нет ли активной самопроверки
    active_check = SelfCheck.query.filter_by(
        user_id=current_user.id,
        is_completed=False
    ).first()
    
    if active_check:
        return jsonify({'error': 'У вас уже есть активная самопроверка'}), 400
    
    self_check = create_self_check(
        current_user.id,
        current_user.department.id,
        checklist.id
    )
    
    return jsonify({
        'message': 'Самопроверка начата',
        'self_check_id': self_check.id
    })

@app.route('/api/self-check/<int:self_check_id>/submit', methods=['POST'])
@login_required
def submit_self_check(self_check_id):
    """Отправить результаты самопроверки"""
    data = request.get_json()
    answers = data.get('answers', {})
    
    if not answers:
        return jsonify({'error': 'Нет данных для сохранения'}), 400
    
    self_check = SelfCheck.query.get_or_404(self_check_id)
    
    # Проверяем что самопроверка принадлежит пользователю
    if self_check.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
                
    # Проверяем что самопроверка не завершена
    if self_check.is_completed:
        return jsonify({'error': 'Самопроверка уже завершена'}), 400
    
    saved_check = save_self_check_answers(self_check_id, answers)
    
    return jsonify({
        'message': 'Самопроверка завершена',
        'total_score': saved_check.total_score
    })

@app.route('/api/self-check/history')
@login_required
def get_self_check_history():
    """Получить историю самопроверок пользователя"""
    checks = SelfCheck.query.filter_by(user_id=current_user.id).order_by(SelfCheck.check_date.desc()).all()
    
    history = []
    for check in checks:
        history.append({
            'id': check.id,
            'check_date': check.check_date.isoformat(),
            'total_score': check.total_score,
            'is_completed': check.is_completed,
            'department_name': check.department.name
        })
    
    return jsonify({'history': history})

# ========== НОВЫЕ МАРШРУТЫ ДЛЯ АКТИВНЫХ ПРОВЕРОК ==========
# Добавить после существующего маршрута /api/self-check/history

@app.route('/api/self-check/active')
@login_required
def get_active_self_check():
    """Получить активную (незавершенную) самопроверку пользователя"""
    active_check = SelfCheck.query.filter_by(
        user_id=current_user.id,
        is_completed=False
    ).first()
    
    if active_check:
        return jsonify({
            'id': active_check.id,
            'checklist_id': active_check.checklist_id,
            'started_at': active_check.check_date.isoformat(),
            'answers': active_check.answers or {}
        })
    else:
        return jsonify({'active_check': None})

@app.route('/api/self-check/<int:check_id>/cancel', methods=['DELETE'])
@login_required
def cancel_self_check(check_id):
    """Отменить самопроверку"""
    check = SelfCheck.query.get_or_404(check_id)
    if check.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    db.session.delete(check)
    db.session.commit()
    return jsonify({'message': 'Проверка отменена'})

def init_database():
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            # Удаляем старые данные для чистоты
            User.query.delete()
            Department.query.delete()
            Checklist.query.delete()
            
            # Создаем структуру подразделений с правильными типами
            production = Department(name='Производственный цех №1', department_type='production')
            quality = Department(name='Отдел технического контроля', department_type='quality')
            warehouse = Department(name='Склад', department_type='warehouse')
            
            db.session.add_all([production, quality, warehouse])
            db.session.commit()
            
            print("✅ Подразделения созданы:")
            print(f"   - {production.name} (тип: {production.department_type})")
            print(f"   - {quality.name} (тип: {quality.department_type})") 
            print(f"   - {warehouse.name} (тип: {warehouse.department_type})")
            
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
                # Устанавливаем пароль
                user.set_password(user_data['username'] + '123')
                db.session.add(user)
                print(f"✅ Создан пользователь: {user_data['username']} / {user_data['username']}123")
            
            db.session.commit()
            print("✅ Все пользователи созданы успешно")
            
            # Создаем примерные чек-листы
            create_sample_checklists()
            
            # Проверяем создание
            user_count = User.query.count()
            checklist_count = Checklist.query.count()
            print(f"📊 Всего пользователей в системе: {user_count}")
            print(f"📋 Всего чек-листов в системе: {checklist_count}")

if __name__ == '__main__':
    print("🚀 Запуск системы 5С по ТЗ...")
    print("📊 База данных: 5s_tz_system.db")
    print("🌐 Доступно по: http://localhost:5001/")
    print("👥 Тестовые пользователи:")
    print("   worker1 / worker1123 - Работник")
    print("   auditor1 / auditor1123 - Аудитор") 
    print("   manager1 / manager1123 - Руководитель")
    print("   admin / admin123 - Администратор")
    print("   quality_dir / quality_dir123 - Директор по качеству")
    print("   production_dir / production_dir123 - Директор по производству")
    init_database()
    app.run(debug=True, port=5001)