from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import categories, products, users, reviews, cart, orders, payments

# Основной файл проекта - точка входа


app = FastAPI(title="FastAPI Интернет-магазин", version="0.1.0", description="Приложение Интернет-магазин на FastAPI")

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)

app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get(path="/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазин"}
