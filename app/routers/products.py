from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.sql import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.schemas import Product as ProductSchema, ProductCreate as ProductCreateSchema, ProductList
from app.db_depends import get_async_db
from app.auth import get_current_seller
from datetime import datetime

# from fastapi import APIRouter – класс для создания маршрутизатора.
# Аутентификация выполняется через JWT, а авторизация — через проверку роли и владения
# Создаем маршрутизатор для товаров
router = APIRouter(prefix="/products", tags=["products"])

#Вынести параметры запроса в pydantic модель валидации, сделать обработку даты
@router.get(path="/", response_model=ProductList, status_code=status.HTTP_200_OK)
async def get_all_products(page: int = Query(1, ge=1),
                           page_size: int = Query(20, ge=1, le=100),
                           category_id: int | None = Query(None, description="ID категории для фильтрации"),
                           min_price: float | None = Query(None, ge=0, description="Минимальная цена товара для фильтрации"),
                           max_price: float | None = Query(None, ge=0, description="Максимальная цена товара для фильтрации"),
                           in_stock: bool | None = Query(None, description="true -только товары в наличии, false - только без остатка для фильтрации"),
                           created_at: datetime | None = Query(None, description="Дата создания товара и время YYYY-MM-DD HH:MM:SS"),
                           seller_id: int | None = Query(None, description="ID продавца для фильтрации"),
                           db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных товаров с поддержкой пагинации и фильтрации(фильтры применяются только при наличии соответствующих параметров запроса,
    что оптимизирует производительность. И ненужные условия не включаются в SQL-запрос, минимизируя нагрузку на базу данных.)
    """
    # Проверка логики min_price <= max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="min_price не может быть больше max_price")

    # Формируем список фильтров
    # все запросы (с фильтрами или без) будут возвращать только активные товары (где поле is_active равно True в базе данных)

    filters = [ProductModel.is_active == True]

    # Реализоция динамических фильтров
    if category_id is not None:
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= min_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if in_stock is not None:
        # тернарный оператор возвращает не bool, а само выражение - инструкция для будущего SQL-запроса(SQLAlchemy переопределяет __gt__, __eq__, и т.д)
        filters.append(ProductModel.stock > 0 if in_stock else ProductModel.stock == 0)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)
    if created_at is not None:
        filters.append(ProductModel.created_at >= created_at)

    # Подсчёт общего количества с учётом фильтров
    total_stmt = select(func.count()).select_from(ProductModel).where(*filters)
    total = await db.scalar(total_stmt) or 0

    products_result = (
        select(ProductModel)
        .where(*filters)
        .order_by(ProductModel.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.scalars(products_result)).all()
    # # Метод all() возвращает все результаты запроса в виде списка.

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post(path="/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateSchema,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    # Проверка существования и активности категории

    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True))
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    # Создание нового продукта в БД
    # model_dump() - pydantic -> dict
    # model_dump_json() pydantic - json_string
    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(path="/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True))
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")
    product_result = await db.scalars(select(ProductModel).where(ProductModel.category_id == category_id,
                                                                 ProductModel.is_active == True))
    products = product_result.all()
    return products


@router.get(path="/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    category_result = await db.scalars(select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                                   CategoryModel.is_active == True))
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    return product


@router.put(path="/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int,
                         product: ProductCreateSchema,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller')
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    db_product = product_result.first()

    # Проверка существует ли товар и активен ли он через запрос к бд
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    # Проверка НОВОЙ переданной категории в category_id - product(ProductCreateSchema)
    category_result = await db.scalars(select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                                   CategoryModel.is_active == True))
    db_category = category_result.first()

    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    # Обновление товара в БД именно из данных полученных при создании Pydantic-модели product: ProductCreateSchema, а не из результата запроса к базе(db_product)
    # update_data = product.model_dump(exclude_unset=True)
    # await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**update_data))
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product


@router.delete(path="/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Выполняет мягкое удаление(логическое и возвращает товар) товар по её ID, устанавливая is_active = False, если он принадлежит текущему продавцу (только для 'seller').
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    # Метод first() возвращает первый результат запроса или None, если результат пустой.
    product = product_result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    # # db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    # db.commit()
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    # product.is_active = False  # напрямую обращаемся к полю ORM объекта
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product
