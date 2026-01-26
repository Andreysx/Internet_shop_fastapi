from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Mapped, mapped_column Инструменты SQLAlchemy 2.x для строгой типизации.
# современный синтаксис mapped_column из SQLAlchemy 2.x, который обеспечивает строгую типизацию и улучшенную читаемость
# relationship, ForeignKey: Используются для настройки связей.
# Атрибуты products, parent, и children не влияют на SQL-схему, так как relationship работает на уровне Python.

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

    #   Реализация самоссылающейся таблицы(самоссылающуюся связь) в sqlalchemy
    #   Самоссылающаяся таблица - это таблица, которая ссылается на себя через внешний ключ (ForeignKey)
    #   Позволяет создавать иерархию одной и той же сущности для гибкости
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id")

    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")

# Модели соответствуют Pydantic-моделям из файла app/schemas.py, что позволит легко преобразовывать данные между API и базой данных.
# Модели данных определяют структуру таблиц в БД
# Модульная структура (app/models) делает проект организованным, а проверка SQL-кода помогает убедиться в корректности моделей перед созданием таблиц.

#
# if __name__ == "__main__":
#     # Проверка SQL-кода, который SQLAlchemy генерирует для создания таблиц
#     from sqlalchemy.schema import CreateTable
#     from app.models.products import Product
#
#     print(CreateTable(Category.__table__))
#     print(CreateTable(Product.__table__))
