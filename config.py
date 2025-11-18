# config.py - Настройки приложения
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-5s-system'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '5s_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки для загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # PWA настройки
    PWA_NAME = 'Система 5С'
    PWA_DESCRIPTION = 'Система аудитов и самопроверок 5С'
    PWA_THEME_COLOR = '#0d6efd'
    PWA_BACKGROUND_COLOR = '#ffffff'