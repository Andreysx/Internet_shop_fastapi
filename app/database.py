#модуль настройки подключения базы данных

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

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
class Base(DeclarativeBase):
    pass

