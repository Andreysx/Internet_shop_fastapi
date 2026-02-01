from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate as ProductCreateSchema
from app.db_depends import get_db

# from fastapi import APIRouter – класс для создания маршрутизатора.

# Создаем маршрутизатор для товаров
router = APIRouter(prefix="/products", tags=["products"])


@router.get(path="/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех активных товаров
    """
    # products = db.scalars(select(ProductModel).where(ProductModel.is_active == True)).all()
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    products = db.scalars(stmt).all()
    # проверка в запросе на "удаленную" категорию и количество на складе > 3
    # products = db.scalars(
    #     select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
    #                                                    CategoryModel.is_active == True,
    #                                                    ProductModel.stock > 0)).all()

    return products


@router.post(path="/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    """
    Создаёт новый товар
    """
    # Проверка существования и активности категории
    if product.category_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
        category = db.scalars(stmt).first()
        if category is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    # Создание нового продукта в БД
    #model_dump() - pydantic -> dict
    #model_dump_json() pydantic - json_string
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get(path="/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")
    stmt_product = select(ProductModel).where(ProductModel.category_id == category_id,
                                              ProductModel.is_active == True)
    products = db.scalars(stmt_product).all()
    return products


@router.get(path="/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product = db.scalars(stmt).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    category_stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                CategoryModel.is_active == True)
    category = db.scalars(category_stmt).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    return product


@router.put(path="/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreateSchema, db: Session = Depends(get_db)):
    """
    Обновляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    db_product = db.scalars(stmt).first()

    # Проверка существует ли товар и активен ли он через запрос к бд
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Проверка НОВОЙ переданной категории в category_id - product(ProductCreateSchema)
    category_stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                CategoryModel.is_active == True)
    db_category = db.scalars(category_stmt).first()

    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    # Обновление товара в БД именно из данных полученных при создании Pydantic-модели product: ProductCreateSchema, а не из результата запроса к базе(db_product)
    db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump()))
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    product.is_active = False #напрямую обращаемся к полю ORM объекта
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
