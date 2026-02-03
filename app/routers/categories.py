from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate as CategoryCreateSchema
from app.db_depends import get_db, get_async_db

# класс APIRouter позволяет:
# Инструмент для создания подгрупп маршрутов
# Задать общий префикс пути (например, /categories для всех маршрутов категорий).
# Добавить теги для группировки эндпоинтов в документации (Swagger UI).
# Настроить зависимости (например, проверка аутентификации для всех маршрутов).
# Разделить логику на модули, чтобы разработчики могли работать над разными частями проекта независимо.


# Создаем маршрутизатор для категорий товаров APIRouter с префиксом и тегом
# Все эндпоинты в этом файле начинаются с prefix Например, @router.get("/") станет /categories/
# В Swagger UI эти эндпоинты будут сгруппированы под заголовком "categories".
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(path="/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных категорий товаров.
    """
    result = await db.scalars(select(CategoryModel).where(CategoryModel.is_active == True))
    categories = result.all()
    return categories


@router.post(path="/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreateSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Создает новую категорию.
    """
    # методы, такие как db.scalars(), db.commit(), и db.refresh(), являются асинхронными, что значит,
    # что их вызов возвращает корутину (объект, который может быть awaited), а не результат.
    # await заставляет код приостановиться, пока операция не завершится, но без блокировки всего потока
    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id, CategoryModel.is_active == True)
        # Важно всегда использовать await перед db.scalars() в асинхронных сессиях БД
        result = await db.scalars(stmt)
        # await заставляет код приостановиться, пока операция не завершится, но без блокировки всего потока.
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    # await db.refresh(db_category)
    # await db.refresh(db_category) пока не нужен, так как expire_on_commit=False предотвращает истечение (expiration) объекта db_category после коммита,
    # и данные объекта остаются актуальными.
    # Вы можете безопасно вернуть db_category без дополнительного вызова refresh
    # лучше всегда использовать await db.refresh(obj),
    # особенно когда нам важно гарантированно вернуть актуальное состояние именно из базы после коммита
    return db_category


@router.put(path="/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryCreateSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет категорию по её ID
    """
    # Проверяем существование категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверяем parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        parent_result = await db.scalars(parent_stmt)
        parent = parent_result.first()

        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent")

    # Обновляем категорию
    # параметр exclude_unset=True обновляет только переданные поля
    update_data = category.model_dump(exclude_unset=True)
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**update_data)
    )
    await db.commit()
    # db.refresh(db_category)
    return db_category


@router.delete(path="/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Выполняет мягкое удаление(логическое и возвращает категорию) категории по её ID, устанавливая is_active = False.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Логическое удаление категории (установка is_active=False)
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()
    return db_category
