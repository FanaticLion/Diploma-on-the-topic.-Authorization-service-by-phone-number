# Реферальная система с авторизацией по телефону

Реферальная система с аутентификацией по номеру телефона, позволяющая пользователям регистрироваться, авторизовываться и использовать инвайт-коды.

## 🚀 Функциональность

- ✅ Авторизация по номеру телефона с SMS-кодом
- ✅ Генерация уникальных 6-значных инвайт-кодов
- ✅ Активация инвайт-кодов других пользователей
- ✅ Просмотр списка рефералов
- ✅ REST API для интеграции
- ✅ Docker контейнеризация

## 🛠 Технологии

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Session-based + CSRF protection
- **Containerization**: Docker + Docker Compose
- **Documentation**: DRF Spectacular (OpenAPI 3.0)

## 📦 Установка и запуск

### Предварительные требования

- Docker
- Docker Compose

### Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd PythonProject17
Запустите проект:

bash
docker-compose up --build
Приложение будет доступно по адресу: http://localhost:8000

Миграции базы данных
bash
docker-compose exec web python manage.py migrate
Создание суперпользователя
bash
docker-compose exec web python manage.py createsuperuser
📚 API Документация
Базовые эндпоинты
1. Запрос кода авторизации
http
POST /api/users/auth/request-code/
Content-Type: application/json

{
    "phone": "+79123456789"
}
Ответ:

json
{
    "message": "Код отправлен",
    "code": "1234"
}
2. Подтверждение кода и авторизация
http
POST /api/users/auth/verify-code/
Content-Type: application/json

{
    "phone": "+79123456789",
    "code": "1234"
}
Ответ:

json
{
    "message": "Успешная авторизация",
    "user_id": 1,
    "phone": "+79123456789",
    "invite_code": "ABC123",
    "is_new_user": true
}
3. Получение профиля пользователя
http
GET /api/users/profile/me/
Headers: 
  Content-Type: application/json
  X-CSRFToken: <your_csrf_token>
Ответ:

json
{
    "id": 1,
    "phone": "+79123456789",
    "invite_code": "ABC123",
    "activated_invite_code": "DEF456",
    "referrals": [
        "+79123456780",
        "+79123456781"
    ]
}
4. Активация инвайт-кода
http
POST /api/users/profile/activate-invite/
Content-Type: application/json
X-CSRFToken: <your_csrf_token>

{
    "invite_code": "DEF456"
}
Ответ:

json
{
    "message": "Инвайт-код успешно активирован",
    "activated_invite_code": "DEF456"
}
5. Получение профиля по номеру телефона
http
GET /api/users/profile/by-phone/?phone=%2B79123456789
Автодокументация API
ReDoc: http://localhost:8000/api/docs/

Swagger UI: http://localhost:8000/api/swagger/

OpenAPI Schema: http://localhost:8000/api/schema/

🗄 Модели данных
User
phone - номер телефона (уникальный)

invite_code - 6-значный инвайт-код пользователя

activated_invite_code - активированный инвайт-код

created_at - дата создания

AuthCode
phone - номер телефона

code - 4-значный код подтверждения

created_at - время создания

is_used - использован ли код

🐳 Docker
Проект использует multi-stage Dockerfile для оптимизации:

dockerfile
FROM python:3.11-slim as builder
# ... этапы сборки

FROM python:3.11-slim as production
# ... финальный образ
Команды управления
bash
# Запуск
docker-compose up --build

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs web

# Выполнение команд в контейнере
docker-compose exec web python manage.py <command>
🧪 Тестирование
Запуск тестов:

bash
docker-compose exec web python manage.py test
Покрытие тестами:

bash
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
📁 Структура проекта
text
PythonProject17/
├── config/                 # Настройки Django
├── users/                  # Приложение пользователей
│   ├── models.py          # Модели User и AuthCode
│   ├── views.py           # API эндпоинты
│   ├── urls.py            # URL маршруты
│   ├── serializers.py     # DRF сериализаторы
│   └── tests.py           # Тесты
├── templates/             # HTML шаблоны
├── static/               # Статические файлы
├── docker-compose.yml    # Docker Compose
├── Dockerfile           # Docker образ
├── requirements.txt     # Зависимости
└── manage.py           # Django manage
🔧 Настройки окружения
Создайте файл .env в корне проекта:

env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@db:5432/referral_db
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web
👥 Разработка
Ветки Git
main - стабильная версия

develop - разработка

feature/* - новые функции

Code Style
PEP8 compliance

Black for code formatting

Flake8 for linting

📄 Лицензия
