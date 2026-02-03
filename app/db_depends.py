from sqlalchemy.orm import Session
from fastapi import Depends
from collections.abc import Generator

from app.database import SessionLocal


##Синхронная сессия
def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Создает новую сессию(сеанс) для каждого запроса и закрывает её даже после обработки
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Эта зависимость будет использоваться в эндпоинтах FastAPI через Depends(get_db), передавая сессию в обработчики запросов.

# --------------- Асинхронная сессия -------------------------

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
