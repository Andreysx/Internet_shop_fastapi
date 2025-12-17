from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
# современный синтаксис mapped_column из SQLAlchemy 2.x, который обеспечивает строгую типизацию и улучшенную читаемость

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)



# Модели соответствуют Pydantic-моделям из файла app/schemas.py, что позволит легко преобразовывать данные между API и базой данных.
# Модульная структура (app/models) делает проект организованным, а проверка SQL-кода помогает убедиться в корректности моделей перед созданием таблиц.


# if __name__ == "__main__":
#     # Проверка SQL-кода, который SQLAlchemy генерирует для создания таблиц
#     from sqlalchemy.schema import CreateTable
#     from app.models.products import Product
#
#     print(CreateTable(Category.__table__))
#     print(CreateTable(Product.__table__))
