# FastAPI E-commerce Интернет-магазин

Реализация API интернет-магазина на FastAPI с аутентификацией, ролями (buyer/seller/admin), товарами, категориями, отзывами, корзиной и заказами.

##  Функциональность

- **Пользователи**: регистрация, вход, JWT-аутентификация (access + refresh токены) stateless реализация
- **Роли**: 
  - `buyer` — может просматривать товары, оставлять отзывы, управлять корзиной и оформлять заказы
  - `seller` — может управлять своими товарами и видеть связанные с ними заказы
  - `admin` — управляет категориями и ролями пользователей
- **Категории**: вложенные (parent-child), CRUD (только для admin)
- **Товары**: 
  - просмотр — публичный
  - создание/редактирование/удаление — только для продавцов (только свои товары)
  - загрузка изображений напрямую через API
  - пагинация (offset-based), фильтрация (по категории, цене, наличию), сортировка и Postgres full-text search(GIN)
- **Отзывы**: 
  - оставить отзыв может только покупатель
  - автоматический пересчёт рейтинга товара
  - мягкое удаление
- **Корзина**: 
  - добавление, обновление, удаление и очистка
  - привязана к авторизованному пользователю
- **Заказы**:
  - оформление заказа из корзины (`POST /orders/checkout`),
  - просмотр списка заказов и деталей заказа
  - фиксация цен и данных товара на момент покупки
  - эндпоинт `GET /orders/{id}/status` для проверки статуса заказа
  
- **Оплата**:
  - интеграция с YooKassa
  - автоматическое создание платежа при оформлении заказа
  - безопасный вебхук для обновления статуса оплаты

##  Технологии

- **Backend**: FastAPI
- **База данных**: PostgreSQL (асинхронно через asyncpg)
- **ORM**: SQLAlchemy 2.0 (асинхронный режим)
- **Миграции**: Alembic
- **Аутентификация**: JWT (PyJWT), bcrypt (passlib)
- **Валидация**: Pydantic v2
- **Файлы**: локальное хранение изображений с раздачей через StaticFiles
- **Платежи**: YooKassa API

##  Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Andreysx/Internet_shop_fastapi.git
cd Internet_shop_fastapi
```

2. Создайте виртуальное окружение и установите зависимости(requirements.txt):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Настройте переменные окружения:
Создайте файл `.env` на основе `.env.example`:
```env
DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
SECRET_KEY=ваш_секретный_ключ
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=live_xxxxxx..... # или test_xxxxxx.....
YOOKASSA_RETURN_URL=http://localhost:8000/
```

4. Примените миграции с alembic:
```bash
alembic upgrade head
```

5. Запустите сервер:
```bash
uvicorn app.main:app --reload --port XXXX
```

6. Откройте http://localhost:8000/docs — интерактивная документация Swagger UI.

## Медиафайлы

Загруженные изображения товаров сохраняются в папку `media/products/` и доступны по пути `/media/products/...`.

Убедитесь, что папка `media/` существует (создаётся автоматически при первой загрузке).

##  Админка

Для работы с категориями и ролями нужен пользователь с ролью `admin`.

Создайте его вручную в БД или через эндпоинт (если реализован):
```sql
INSERT INTO users (email, hashed_password, is_active, role)
VALUES ('admin@example.com', '<хеш_пароля>', true, 'admin');
```
>Хеш пароля можно получить через `hash_password()` из `app/auth.py`.

##  Структура проекта

```
app/
├── auth.py          # JWT, хеширование, зависимости аутентификации
├── config.py        # Загрузка .env
├── database.py      # Подключение к базе данных (PostgreSql/Squlite...), AsyncEngine, сессии
├── db_depends.py    # Зависимисть получения ассинхронной сессии (get_async_db)
├── main.py          # Точка входа, подключение статики
├── payments.py      # Функция отправки платежа для YooKassa
├── models/          # SQLAlchemy модели
├── routers/         # Маршрутизаторы (основная логика)
├── schemas.py       # Pydantic схемы валидации запросов- ответов
└── migrations/      # Alembic (версии миграций)
```