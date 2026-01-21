# Пошаговая инструкция: Веб-приложение на Flask для мониторинга цен

## 📋 Оглавление
1. [Обзор архитектуры](#обзор-архитектуры)
2. [Структура проекта](#структура-проекта)
3. [Этап 1: Подготовка](#этап-1-подготовка)
4. [Этап 2: Базовая настройка](#этап-2-базовая-настройка)
5. [Этап 3: База данных](#этап-3-база-данных)
6. [Этап 4: Backend API](#этап-4-backend-api)
7. [Этап 5: Frontend Templates](#этап-5-frontend-templates)
8. [Этап 6: Локальный uploader](#этап-6-локальный-uploader)
9. [Этап 7: Тестирование](#этап-7-тестирование)
10. [Этап 8: Деплой на Railway](#этап-8-деплой-на-railway)

---

## Обзор архитектуры

### 🎯 Что мы создаем:

```
┌─────────────────────────────────────────────────────────────┐
│                    ЛОКАЛЬНЫЙ КОМПЬЮТЕР                      │
│                                                             │
│  1. Обновление остатков (вручную)                          │
│  2. python run_full_cycle.py                               │
│  3. python web_uploader.py                                 │
│     └──> Отправка Excel через HTTP POST                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS POST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY.APP (Cloud)                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Flask Web Application                     │ │
│  │                                                        │ │
│  │  Routes:                                               │ │
│  │  • /              → Dashboard (главная)               │ │
│  │  • /login         → Вход                              │ │
│  │  • /comparison    → Таблица сравнения                 │ │
│  │  • /history       → История загрузок                  │ │
│  │  • /api/upload    → API для загрузки данных           │ │
│  │                                                        │ │
│  │  Templates: Jinja2 + Bootstrap 5                      │ │
│  │  Database: PostgreSQL (Railway)                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
                    ┌───────────────┐
                    │   USERS       │
                    │  (Browsers)   │
                    └───────────────┘
```

### 🔑 Ключевые особенности:

**Backend (Flask):**
- Простой и понятный Python код
- Jinja2 для HTML шаблонов
- SQLAlchemy для работы с БД
- Flask-Login для аутентификации

**Frontend:**
- Bootstrap 5 для UI
- DataTables.js для интерактивных таблиц
- Chart.js для графиков
- Адаптивный дизайн

**Database (PostgreSQL):**
- Хранение истории загрузок
- Товары и цены конкурентов
- Пользователи

---

## Структура проекта

### 📁 Новая структура (добавляем к существующему):

```
Coffee machines price scrapper/
│
├── web_app/                          # 🆕 Новая папка для веб-приложения
│   ├── __init__.py
│   ├── app.py                        # Главный файл Flask приложения
│   ├── config.py                     # Конфигурация
│   ├── database.py                   # Подключение к БД
│   │
│   ├── models/                       # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── upload.py                 # Модель Upload
│   │   ├── product.py                # Модель Product
│   │   ├── competitor_price.py       # Модель CompetitorPrice
│   │   ├── statistic.py              # Модель Statistic
│   │   └── user.py                   # Модель User
│   │
│   ├── routes/                       # Flask routes (endpoints)
│   │   ├── __init__.py
│   │   ├── main.py                   # Главные маршруты (/, /dashboard)
│   │   ├── comparison.py             # Маршруты сравнения (/comparison)
│   │   ├── history.py                # Маршруты истории (/history)
│   │   ├── api.py                    # API маршруты (/api/upload)
│   │   └── auth.py                   # Аутентификация (/login, /logout)
│   │
│   ├── services/                     # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── excel_parser.py           # Парсинг Excel файлов
│   │   ├── data_processor.py         # Обработка данных
│   │   └── statistics.py             # Расчет статистики
│   │
│   ├── templates/                    # Jinja2 HTML шаблоны
│   │   ├── base.html                 # Базовый шаблон
│   │   ├── components/               # Переиспользуемые компоненты
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   └── alerts.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── comparison/
│   │   │   └── index.html
│   │   └── history/
│   │       └── index.html
│   │
│   ├── static/                       # Статические файлы
│   │   ├── css/
│   │   │   ├── custom.css            # Кастомные стили
│   │   │   └── bootstrap.min.css     # Bootstrap (CDN лучше)
│   │   ├── js/
│   │   │   ├── main.js               # Главный JS
│   │   │   ├── tables.js             # Логика таблиц
│   │   │   └── charts.js             # Логика графиков
│   │   └── img/
│   │       └── logo.png
│   │
│   └── utils/                        # Вспомогательные функции
│       ├── __init__.py
│       ├── decorators.py             # Декораторы (@login_required)
│       └── helpers.py                # Вспомогательные функции
│
├── web_uploader/                     # 🆕 Локальный скрипт загрузки
│   ├── __init__.py
│   ├── uploader.py                   # Главный скрипт
│   ├── config.ini                    # Конфигурация (URL, токен)
│   └── README.md
│
├── migrations/                       # 🆕 Flask-Migrate миграции БД
│   ├── versions/
│   └── alembic.ini
│
├── tests/                            # 🆕 Тесты (опционально)
│   ├── test_routes.py
│   └── test_services.py
│
├── Dockerfile                        # 🆕 Для деплоя на Railway
├── railway.json                      # 🆕 Конфигурация Railway
├── requirements-web.txt              # 🆕 Зависимости для веб-приложения
├── .env.example                      # 🆕 Пример переменных окружения
├── run_web.py                        # 🆕 Запуск веб-приложения локально
│
└── ... (существующие файлы)
```

### 📊 Размер проекта:

| Компонент | Файлов | Строк кода (примерно) |
|-----------|--------|------------------------|
| Models | 5 | ~300 |
| Routes | 5 | ~600 |
| Services | 3 | ~400 |
| Templates | 8 | ~1,200 |
| Static (JS/CSS) | 4 | ~500 |
| Utils | 2 | ~150 |
| Uploader | 1 | ~200 |
| Config/Setup | 5 | ~200 |
| **ИТОГО** | **33** | **~3,550** |

---

## Этап 1: Подготовка

### 🎯 Что нужно сделать:

#### 1.1. Проверка текущего окружения

```bash
# Проверяем Python версию
python --version
# Должно быть: Python 3.11 или выше

# Проверяем pip
pip --version
```

#### 1.2. Создание виртуального окружения (опционально)

```bash
# Создаем venv для веб-приложения
python -m venv venv_web

# Активируем (Windows)
venv_web\Scripts\activate

# Активируем (Linux/Mac)
source venv_web/bin/activate
```

#### 1.3. Установка зависимостей (локально для разработки)

Сначала создадим файл `requirements-web.txt`:

```txt
# Flask и расширения
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.2.1

# База данных
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Обработка данных
pandas==2.1.3
openpyxl==3.1.2

# Безопасность
Werkzeug==3.0.1
python-dotenv==1.0.0

# Production server
gunicorn==21.2.0

# Утилиты
requests==2.31.0
```

Установка:
```bash
pip install -r requirements-web.txt
```

#### 1.4. Регистрация на Railway (если еще не сделано)

1. Перейти на https://railway.app/
2. Зарегистрироваться через GitHub
3. Создать новый проект
4. Добавить PostgreSQL базу данных
5. Скопировать DATABASE_URL

---

## Этап 2: Базовая настройка

### 📝 2.1. Создание структуры папок

```bash
# Создаем основные папки
mkdir web_app
mkdir web_app/models
mkdir web_app/routes
mkdir web_app/services
mkdir web_app/templates
mkdir web_app/templates/auth
mkdir web_app/templates/dashboard
mkdir web_app/templates/comparison
mkdir web_app/templates/history
mkdir web_app/templates/components
mkdir web_app/static
mkdir web_app/static/css
mkdir web_app/static/js
mkdir web_app/static/img
mkdir web_app/utils
mkdir web_uploader
mkdir migrations
```

### 📝 2.2. Создание файла конфигурации

**Файл: `web_app/config.py`**

```python
"""
Flask application configuration
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/coffee_prices'
    
    # Fix for Railway PostgreSQL URL
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # API
    API_TOKEN = os.environ.get('API_TOKEN') or 'dev-api-token-change-in-production'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Выбор конфигурации
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 📝 2.3. Создание .env файла

**Файл: `.env.example`** (шаблон)

```env
# Flask
FLASK_APP=run_web.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database (получить из Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# API Token для локального uploader
API_TOKEN=your-api-token-here

# Railway (для деплоя)
PORT=8000
```

**Файл: `.env`** (создать локально, не коммитить в Git!)

```env
FLASK_APP=run_web.py
FLASK_ENV=development
SECRET_KEY=local-dev-secret-key
DATABASE_URL=postgresql://localhost/coffee_prices_dev
API_TOKEN=local-dev-token-123
```

### 📝 2.4. Обновление .gitignore

Добавить в `.gitignore`:

```gitignore
# Environment
.env
venv_web/

# Flask
instance/
*.pyc
__pycache__/

# Database
*.db
*.sqlite

# Uploads
web_app/uploads/
```

---

## Этап 3: База данных

### 📊 3.1. Создание моделей SQLAlchemy

**Файл: `web_app/database.py`**

```python
"""
Database connection and initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import models
        from web_app.models import user, upload, product, competitor_price, statistic
        
        # Create tables if they don't exist
        db.create_all()
```

**Файл: `web_app/models/__init__.py`**

```python
"""
Database models
"""
from web_app.models.user import User
from web_app.models.upload import Upload
from web_app.models.product import Product
from web_app.models.competitor_price import CompetitorPrice
from web_app.models.statistic import Statistic

__all__ = ['User', 'Upload', 'Product', 'CompetitorPrice', 'Statistic']
```

**Файл: `web_app/models/user.py`**

```python
"""
User model for authentication
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from web_app.database import db

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='viewer')  # admin, manager, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
```

**Файл: `web_app/models/upload.py`**

```python
"""
Upload model - represents one data upload session
"""
from datetime import datetime
from web_app.database import db

class Upload(db.Model):
    """Upload session model"""
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_name = db.Column(db.String(255))
    total_products = db.Column(db.Integer)
    status = db.Column(db.String(50), default='completed')
    
    # Relationships
    products = db.relationship('Product', backref='upload', lazy='dynamic', cascade='all, delete-orphan')
    statistics = db.relationship('Statistic', backref='upload', uselist=False, cascade='all, delete-orphan')
    user = db.relationship('User', backref='uploads')
    
    def __repr__(self):
        return f'<Upload {self.upload_date}>'
```

**Файл: `web_app/models/product.py`**

```python
"""
Product model - represents a product in our inventory
"""
from web_app.database import db

class Product(db.Model):
    """Product model"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id', ondelete='CASCADE'), nullable=False)
    
    model = db.Column(db.String(100), index=True)
    name = db.Column(db.String(500))
    quantity = db.Column(db.Integer)
    our_price = db.Column(db.Numeric(10, 2))
    brand = db.Column(db.String(50), index=True)  # DeLonghi, Melitta, Nivona
    competitor_count = db.Column(db.Integer, default=0)
    
    # Relationships
    competitor_prices = db.relationship('CompetitorPrice', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.model}>'
```

**Файл: `web_app/models/competitor_price.py`**

```python
"""
CompetitorPrice model - represents competitor's price for a product
"""
from web_app.database import db

class CompetitorPrice(db.Model):
    """Competitor price model"""
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    
    competitor = db.Column(db.String(50), nullable=False, index=True)  # ALTA, KONTAKT, etc.
    price = db.Column(db.Numeric(10, 2))
    regular_price = db.Column(db.Numeric(10, 2))
    discount_price = db.Column(db.Numeric(10, 2))
    has_discount = db.Column(db.Boolean, default=False)
    url = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CompetitorPrice {self.competitor}: {self.price}>'
```

**Файл: `web_app/models/statistic.py`**

```python
"""
Statistic model - aggregated statistics for an upload
"""
from web_app.database import db

class Statistic(db.Model):
    """Statistics model"""
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    total_value = db.Column(db.Numeric(12, 2))
    avg_price = db.Column(db.Numeric(10, 2))
    products_cheaper = db.Column(db.Integer)
    products_expensive = db.Column(db.Integer)
    products_no_competitors = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Statistic for upload {self.upload_id}>'
```

### 📊 3.2. Инициализация миграций

```bash
# Инициализация Flask-Migrate
flask db init

# Создание первой миграции
flask db migrate -m "Initial migration"

# Применение миграции
flask db upgrade
```

---

## Этап 4: Backend API

### 🔌 4.1. Главный файл приложения

**Файл: `web_app/__init__.py`**

```python
"""
Flask application factory
"""
from flask import Flask
from flask_login import LoginManager
from web_app.config import config
from web_app.database import db, init_db

login_manager = LoginManager()

def create_app(config_name='default'):
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from web_app.routes import main, auth, comparison, history, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(comparison.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(api.bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from web_app.models import User
        return User.query.get(int(user_id))
    
    return app
```

**Файл: `run_web.py`** (в корне проекта)

```python
"""
Run Flask application
"""
import os
from web_app import create_app

# Get config from environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 🔌 4.2. Маршруты (Routes)

**Файл: `web_app/routes/__init__.py`**

```python
"""
Application routes (blueprints)
"""
from web_app.routes.main import bp as main_bp
from web_app.routes.auth import bp as auth_bp
from web_app.routes.comparison import bp as comparison_bp
from web_app.routes.history import bp as history_bp
from web_app.routes.api import bp as api_bp

__all__ = ['main_bp', 'auth_bp', 'comparison_bp', 'history_bp', 'api_bp']
```

**Файл: `web_app/routes/auth.py`** (пример)

```python
"""
Authentication routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from web_app.models import User
from web_app.database import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('auth.login'))
```

---

## Этап 5: Frontend Templates

### 🎨 5.1. Базовый шаблон

**Файл: `web_app/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Coffee Price Monitor{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    {% include 'components/navbar.html' %}
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
        <!-- Flash Messages -->
        {% include 'components/alerts.html' %}
        
        <!-- Page Content -->
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'components/footer.html' %}
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## Этап 6: Локальный uploader

### 📤 6.1. Скрипт для загрузки данных

**Файл: `web_uploader/uploader.py`**

```python
"""
Upload price comparison data to web server
"""
import os
import sys
import requests
import configparser
from pathlib import Path
from datetime import datetime

class PriceDataUploader:
    """Upload price data to web application"""
    
    def __init__(self, config_file='config.ini'):
        """Initialize uploader"""
        self.config = self.load_config(config_file)
        self.api_url = self.config.get('api', 'url')
        self.api_token = self.config.get('api', 'token')
    
    def load_config(self, config_file):
        """Load configuration"""
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        config.read(config_path)
        return config
    
    def find_latest_comparison_file(self):
        """Find latest price_comparison_*.xlsx file"""
        output_dir = Path(__file__).parent.parent / 'data' / 'output'
        
        if not output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")
        
        files = list(output_dir.glob('price_comparison_*.xlsx'))
        
        if not files:
            raise FileNotFoundError("No price comparison files found")
        
        # Sort by modification time, newest first
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        return latest_file
    
    def upload_file(self, file_path):
        """Upload file to web server"""
        print(f"Uploading file: {file_path}")
        print(f"API URL: {self.api_url}")
        
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            try:
                response = requests.post(
                    self.api_url,
                    files=files,
                    headers=headers,
                    timeout=60
                )
                
                response.raise_for_status()
                
                result = response.json()
                print(f"✓ Upload successful!")
                print(f"  Date: {result.get('date')}")
                print(f"  Products: {result.get('products')}")
                print(f"  Total value: {result.get('total_value')} GEL")
                
                return True
                
            except requests.exceptions.RequestException as e:
                print(f"✗ Upload failed: {e}")
                return False
    
    def run(self):
        """Main upload process"""
        try:
            # Find latest file
            latest_file = self.find_latest_comparison_file()
            print(f"Found latest file: {latest_file}")
            
            # Upload
            success = self.upload_file(latest_file)
            
            if success:
                print("\nData uploaded successfully to web server!")
                print(f"View at: {self.api_url.replace('/api/upload', '')}")
            else:
                print("\nUpload failed. Check logs for details.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    uploader = PriceDataUploader()
    uploader.run()
```

**Файл: `web_uploader/config.ini.example`**

```ini
[api]
url = https://your-app.railway.app/api/upload
token = your-api-token-here
```

---

## Этап 7: Тестирование

### 🧪 7.1. Локальное тестирование

```bash
# 1. Запуск Flask приложения локально
python run_web.py

# 2. Открыть браузер: http://localhost:5000

# 3. Создать первого пользователя (через Flask shell)
flask shell
>>> from web_app.models import User
>>> from web_app.database import db
>>> user = User(username='admin', email='admin@example.com', role='admin')
>>> user.set_password('admin123')
>>> db.session.add(user)
>>> db.session.commit()
>>> exit()

# 4. Войти в систему (admin / admin123)

# 5. Протестировать загрузку данных
cd web_uploader
python uploader.py
```

---

## Этап 8: Деплой на Railway

### 🚂 8.1. Подготовка файлов для деплоя

**Файл: `Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application
COPY . .

# Expose port
EXPOSE $PORT

# Run application
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run_web:app
```

**Файл: `railway.json`**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run_web:app",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### 🚂 8.2. Деплой на Railway

```bash
# 1. Коммитим все изменения
git add .
git commit -m "Add Flask web application"
git push origin main

# 2. В Railway Dashboard:
#    - New Project → Deploy from GitHub
#    - Выбрать репозиторий
#    - Railway автоматически определит Python проект

# 3. Добавить PostgreSQL:
#    - Add Service → Database → PostgreSQL
#    - Railway создаст БД и добавит DATABASE_URL

# 4. Добавить Environment Variables:
SECRET_KEY=your-production-secret-key
API_TOKEN=your-production-api-token
FLASK_ENV=production

# 5. Deploy!
#    Railway автоматически соберет и запустит приложение

# 6. Инициализация БД (один раз):
#    - Открыть Railway Shell
#    - flask db upgrade
#    - Создать первого пользователя

# 7. Настроить custom domain (опционально):
#    - Settings → Domains → Add Custom Domain
```

---

## 📊 Итоговая проверка

### ✅ Чек-лист перед запуском:

#### Локально:
- [ ] Python 3.11+ установлен
- [ ] Виртуальное окружение создано
- [ ] Зависимости установлены (`pip install -r requirements-web.txt`)
- [ ] PostgreSQL установлен и запущен (или используем Railway)
- [ ] `.env` файл создан с правильными настройками
- [ ] Миграции применены (`flask db upgrade`)
- [ ] Первый пользователь создан
- [ ] Flask приложение запускается (`python run_web.py`)
- [ ] Можно войти в систему

#### Railway:
- [ ] Проект создан на Railway
- [ ] PostgreSQL добавлен
- [ ] Environment variables настроены
- [ ] GitHub подключен
- [ ] Деплой успешен
- [ ] Healthcheck проходит
- [ ] Миграции применены
- [ ] Первый пользователь создан
- [ ] Можно войти в систему

#### Uploader:
- [ ] `config.ini` создан с правильным URL и токеном
- [ ] Тестовая загрузка успешна
- [ ] Данные отображаются на сайте

---

## 📝 Следующие шаги

После базовой настройки:

1. **Неделя 1-2:**
   - Реализовать все маршруты (routes)
   - Создать все шаблоны (templates)
   - Добавить сервисы обработки данных

2. **Неделя 3:**
   - Добавить фильтрацию и поиск
   - Добавить графики (Chart.js)
   - Улучшить UI/UX

3. **Неделя 4:**
   - Тестирование
   - Исправление багов
   - Документация

---

## 🎯 Резюме

**Что мы создадим:**
- Веб-приложение на Flask
- PostgreSQL база данных
- Простой и понятный UI
- Локальный скрипт загрузки
- Деплой на Railway

**Время реализации:**
- MVP: 2-3 недели
- Полная версия: 4-5 недель

**Стоимость:**
- Разработка: собственная (уже делаем)
- Хостинг: $0-5/месяц (Railway)

---

**Готовы начать?** 
Сообщите, и мы начнем реализацию по этапам! 🚀

---

**Последнее обновление:** 28.10.2025
**Версия:** 1.0
