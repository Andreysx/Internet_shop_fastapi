from fastapi import FastAPI

from app.routers import categories, products

# Основной файл проекта - точка входа


# Создаем приложение FastфAPI
app = FastAPI(title="FastAPI Интернет-магазин", version="0.1.0", description="Приложение Интернет-магазин на FastAPI")

# Подключаем маршруты категорий(categories.py) и продуктов(products.py)при помощи метода include_router()
app.include_router(categories.router)
app.include_router(products.router)


# Корневой эндпоинт для проверки
@app.get(path="/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазин"}
