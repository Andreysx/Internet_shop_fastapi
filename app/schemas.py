from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime


# Модуль для моделей pydantic
# Также обратите внимание на ... (троеточие) в Field(), это специальное значение Ellipsis в Python.
# В контексте Pydantic оно означает что поле обязательно и значение по умолчанию отсутствует. То есть:
#
# Field(..., description="...") → поле обязательно, если его не передать будет ошибка валидации.
# Field(None, description="...") → поле необязательно, и по умолчанию в нём будет None, если его не передать.

class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=50, description="Название категории (3-50 символов)")
    parent_id: int | None = Field(default=None, description="ID родительской категории, если есть")


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории")
    parent_id: int | None = Field(default=None, description="ID родительской категории, если есть")
    is_active: bool = Field(..., description="Активность категории")

    # Настройка ConfigDict(from_attributes=True) обеспечивает совместимость с ORM, позволяя преобразовывать данные из базы в JSON-ответы.
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=100, description="Название товара (3-100 символов)")
    description: str | None = Field(default=None, max_length=500, description="Описание товара (до 500 символов)")
    price: Decimal = Field(..., gt=0, description="Цена товара (больше 0)", decimal_places=2)
    image_url: str | None = Field(default=None, max_length=200, description="URL изображение товара")
    stock: int = Field(..., ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(..., description="ID категории, к которой относится товар")


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    description: str | None = Field(default=None, description="Описание товара")
    price: Decimal = Field(..., description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(default=None, description="URL изображение товара")
    rating: float = Field(..., description="Оценка товара")
    stock: int = Field(..., description="Количество товара на складе")
    category_id: int = Field(..., description="ID категории")
    is_active: bool = Field(..., description="Активность товара")

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """
    Список пагинации для товаров.
    """
    items: list[Product] = Field(description="Товары для текущей страницы")
    total: int = Field(ge=0, description="Общее количество товаров")
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(max_length=8, description="Пароль (минимум 8 символов)")
    # тобы случайно где-нибудь не засветить пароль (в том числе в логах), можно аннотировать его в модели UserCreate как SecretStr.
    # Тогда доступ к значению нужно будет осуществлять через user.password.get_secret_value().
    role: str = Field(default="buyer", pattern="^(buyer|seller)", description="Роль: 'buyer' или 'seller")


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(buyer|seller|admin)$", description="Новая роль")


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CreateReview(BaseModel):
    product_id: int = Field(..., description="ID товара, к которому относится отзыв")
    comment: str | None = Field(None, max_length=500, description="Текст отзыва")
    grade: int = Field(..., ge=1, le=5, description="Оценка товара(1-5)")


class Review(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор отзыва")
    comment: str = Field(..., description="Текст отзыва")
    comment_date: datetime = Field(..., description="Дата и время создания отзыва")
    grade: int = Field(..., ge=1, le=5, description="Оценка товара")
    is_active: bool = Field(..., description="Активность отзыва")
    user_id: int = Field(..., description="ID пользователя")
    product_id: int = Field(..., description="ID товара")

    model_config = ConfigDict(from_attributes=True)


class CartItemBase(BaseModel):
    """Базовая модель корзины"""
    product_id: int = Field(description="ID товара")
    quantity: int = Field(ge=1, description="Количество товара")


class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину"""
    pass


class CartItemUpdate(BaseModel):
    """Модель обновления количества товара в корзине"""
    quantity: int = Field(..., ge=1, description="Новое количество товара")


class CartItem(BaseModel):
    """Товар в корзине с данными продукта"""
    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(..., ge=1, description="Количество товара")
    product: Product = Field(..., description="Информация о товаре")

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """Полная информация о корзине пользователя"""
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItem] = Field(default_factory=list, description="Содержимое корзины")
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)




