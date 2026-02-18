from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchema, CreateReview as CreateReviewSchema
from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(select(func.avg(ReviewModel.grade))
                              .where(ReviewModel.product_id == product_id))
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get(path="/", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает все активные отзывы
    """
    reviews_result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = reviews_result.all()
    return reviews


@router.get(path="/products/{product_id}", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_review_by_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает все отзывы для конкретного товара по его ID
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    reviews_result = await db.scalars(
        select(ReviewModel).where(ReviewModel.product_id == product.id, ReviewModel.is_active == True))
    reviews = reviews_result.all()
    return reviews


@router.post(path="/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: CreateReviewSchema,
                        db: AsyncSession = Depends(get_async_db),
                        current_buyer: UserModel = Depends(get_current_buyer)):
    """
    Создает новый отзыв о товаре по его ID
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True))
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    db_review = ReviewModel(**review.model_dump(), user_id=current_buyer.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    await update_product_rating(db, product.id)

    return db_review


@router.delete(path="/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user)):
    """
    Мягкое удаление отзыва(логическое) от имени автора или админа
    """
    review_result = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True))
    review = review_result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can`t perform this action")

    review.is_active = False
    # await db.commit()
    # await db.refresh(review)
    await update_product_rating(db, review.product_id)

    return {"message": "Review deleted"}
