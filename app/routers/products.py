from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate as ProductCreateSchema
from app.db_depends import get_async_db

# from fastapi import APIRouter – класс для создания маршрутизатора.

# Создаем маршрутизатор для товаров
router = APIRouter(prefix="/products", tags=["products"])


@router.get(path="/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных товаров
    """
    # products = db.scalars(select(ProductModel).where(ProductModel.is_active == True)).all()
    # stmt = select(ProductModel).where(ProductModel.is_active == True)
    product_result = await db.scalars(select(ProductModel).where(ProductModel.is_active == True))
    # Метод all() возвращает все результаты запроса в виде списка.
    products = product_result.all()
    # проверка в запросе на "удаленную" категорию и количество на складе > 3
    # products = db.scalars(
    #     select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
    #                                                    CategoryModel.is_active == True,
    #                                                    ProductModel.stock > 0)).all()

    return products


@router.post(path="/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар
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
    db_product = ProductModel(**product.model_dump())
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
async def update_product(product_id: int, product: ProductCreateSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    db_product = product_result.first()

    # Проверка существует ли товар и активен ли он через запрос к бд
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

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
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Выполняет мягкое удаление(логическое и возвращает товар) товар по её ID, устанавливая is_active = False.
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    # Метод first() возвращает первый результат запроса или None, если результат пустой.
    product = product_result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # # db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    # db.commit()
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    # product.is_active = False  # напрямую обращаемся к полю ORM объекта
    await db.commit()
    await db.refresh(product)
    return product
