from datetime import datetime
from models import db, Checklist, CriteriaGroup, Criterion, SelfCheck, SelfCheckAnswer, Department

def create_sample_checklists():
    """Создание примерных чек-листов для самопроверки"""
    
    # Удаляем старые чек-листы если есть
    Checklist.query.filter_by(checklist_type='self_check').delete()
    
    # Чек-лист для производственных подразделений
    production_checklist = Checklist(
        name="Самопроверка 5С - Производство",
        checklist_type="self_check",
        department_type="production",  # Важно: должно совпадать с department_type подразделения
        is_active=True
    )
    db.session.add(production_checklist)
    
    # Чек-лист для складов
    warehouse_checklist = Checklist(
        name="Самопроверка 5С - Склад",
        checklist_type="self_check", 
        department_type="warehouse",
        is_active=True
    )
    db.session.add(warehouse_checklist)
    
    # Чек-лист для отделов качества
    quality_checklist = Checklist(
        name="Самопроверка 5С - ОТК",
        checklist_type="self_check",
        department_type="quality", 
        is_active=True
    )
    db.session.add(quality_checklist)
    
    # Группы критериев для всех чек-листов
    groups_data = [
        {
            'name': 'Сортировка (Сейри)',
            'criteria': [
                'На рабочем месте нет лишних предметов',
                'Инструменты и материалы отсортированы по частоте использования',
                'Отсутствуют сломанные инструменты и оборудование',
                'Четко определены места для хранения'
            ]
        },
        {
            'name': 'Соблюдение порядка (Сейтон)',
            'criteria': [
                'Все предметы имеют постоянные места хранения',
                'Инструменты размещены в зоне легкой досягаемости',
                'Используется визуальная маркировка',
                'Проходы и зоны движения свободны'
            ]
        },
        {
            'name': 'Содержание в чистоте (Сейсо)',
            'criteria': [
                'Рабочее место чистое и убрано',
                'Оборудование содержится в чистоте',
                'Отсутствуют утечки и разливы',
                'Система уборки понятна и соблюдается'
            ]
        },
        {
            'name': 'Стандартизация (Сейкэцу)',
            'criteria': [
                'Существуют стандарты организации рабочего места',
                'Стандарты понятны и доступны',
                'Все сотрудники обучены стандартам',
                'Визуальный контроль состояния осуществляется регулярно'
            ]
        },
        {
            'name': 'Совершенствование (Сицукэ)',
            'criteria': [
                'Самопроверки проводятся регулярно',
                'Выявленные проблемы устраняются своевременно',
                'Работники участвуют в улучшениях',
                'Отмечаются положительные результаты'
            ]
        }
    ]
    
    # Создаем группы и критерии для каждого чек-листа
    checklists = [production_checklist, warehouse_checklist, quality_checklist]
    
    for checklist in checklists:
        order_index = 0
        for group_data in groups_data:
            group = CriteriaGroup(
                checklist=checklist,
                name=group_data['name'],
                order_index=order_index
            )
            db.session.add(group)
            
            criterion_order = 0
            for criterion_desc in group_data['criteria']:
                criterion = Criterion(
                    group=group,
                    description=criterion_desc,
                    order_index=criterion_order
                )
                db.session.add(criterion)
                criterion_order += 1
            
            order_index += 1
    
    db.session.commit()
    print("✅ Примерные чек-листы созданы для всех типов подразделений")

def get_self_checklist(department_type):
    """Получить чек-лист для самопроверки по типу подразделения"""
    print(f"🔍 Поиск чек-листа для типа подразделения: {department_type}")  # Отладочная информация
    
    checklist = Checklist.query.filter_by(
        checklist_type='self_check',
        department_type=department_type,
        is_active=True
    ).first()
    
    if checklist:
        print(f"✅ Найден чек-лист: {checklist.name}")
    else:
        print(f"❌ Чек-лист для типа '{department_type}' не найден")
        # Покажем какие чек-листы есть в базе
        all_checklists = Checklist.query.all()
        print("📋 Все чек-листы в базе:")
        for cl in all_checklists:
            print(f"   - {cl.name} (тип: {cl.department_type}, активен: {cl.is_active})")
    
    return checklist

def create_self_check(user_id, department_id, checklist_id):
    """Создать новую самопроверку"""
    self_check = SelfCheck(
        user_id=user_id,
        department_id=department_id,
        checklist_id=checklist_id,
        check_date=datetime.utcnow(),
        is_completed=False
    )
    db.session.add(self_check)
    db.session.commit()
    return self_check

def save_self_check_answers(self_check_id, answers):
    """Сохранить ответы самопроверки"""
    for criterion_id, score in answers.items():
        answer = SelfCheckAnswer(
            self_check_id=self_check_id,
            criterion_id=criterion_id,
            score=score
        )
        db.session.add(answer)
    
    # Обновляем общий балл
    self_check = SelfCheck.query.get(self_check_id)
    total_score = sum(answers.values()) / len(answers) * 20  # Переводим в проценты
    self_check.total_score = total_score
    self_check.is_completed = True
    
    db.session.commit()
    return self_check