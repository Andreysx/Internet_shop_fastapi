#модуль настройки подключения базы данных
#Синхронное подключение к SQlite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Строка подключения для SQLite
#/// для относительного пути к файлу ecommerce.db
#////Для абсолютного пути используйте четыре слэша, например, sqlite:////absolute/path/to/ecommerce.db
#SQLite — это файловая база данных, не требующая отдельного сервера. Она хранит данные в одном файле (ecommerce.db)
# Для SQLite драйвер указывать необязательно, так как используется встроенный модуль sqlite3
# Также SQLAlchemy поддерживает различные базы данных через единый формат URL:
# dialect+driver://username:password@host:port/database
# DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/dbname"

DATABASE_URL = "sqlite:///ecommerce.db"

# Создаём объект Engine
# Управляет подключением к базе данных и пулом соединений
# Перевод команд SQLAlchemy в SQL-запросы
# Определение диалекта для взаимодействия с базой данных
# create_engine - синхронное подключение для синхронных запросов
# create_async_engine - ассинхронное подключение для асинхронных запросов
engine = create_engine(DATABASE_URL, echo=True)


#Настройка фабрики сеансов
# SessionLocal — это фабрика, а не сам сеанс.
# Она создаёт новые экземпляры сеансов (Session) при вызове, например, session = SessionLocal().
# Сеанс (Session) в SQLAlchemy — это объект, который управляет операциями с базой данных, такими как добавление, обновление или удаление данных.
SessionLocal = sessionmaker(bind=engine)

#Определение базового класса для моделей данных(таблиц в бд)
#Базовый класс Base — это основа для создания моделей SQLAlchemy, которые представляют таблицы базы данных.
# class Base(DeclarativeBase):
#     pass


# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


# Строка подключения для PostgreSQl
DATABASE_URL = "postgresql+asyncpg://ecommerce_user:12345@localhost:5432/ecommerce_db"

# Создаём Engine асинхронное взаимодействие с БД
#Параметр echo=True включает логирование SQL-запросов в консоль
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
# Фабрика сессий async_session_maker создаётся с помощью async_sessionmaker, которая настроена для использования AsyncSession —
# асинхронного аналога синхронной Session. expire_on_commit=False — параметр в SQLAlchemy, который отключает «устаревание» (expiration) объектов, хранимых в сессии.
# По умолчанию expire_on_commit=True и после вызова commit() все объекты, которые были изменены в сессии, помечаются как «устаревшие».
# Это означает, что при следующем обращении к этим объектам они будут автоматически перезагружены из базы данных.
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass

