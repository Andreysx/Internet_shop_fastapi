from fastapi import APIRouter

# класс APIRouter позволяет:
# Задать общий префикс пути (например, /categories для всех маршрутов категорий).
# Добавить теги для группировки эндпоинтов в документации (Swagger UI).
# Настроить зависимости (например, проверка аутентификации для всех маршрутов).
# Разделить логику на модули, чтобы разработчики могли работать над разными частями проекта независимо.


# Создаем маршрутизатор для категорий товаров APIRouter с префиксом и тегом
#Все эндпоинты в этом файле начинаются с prefix Например, @router.get("/") станет /categories/
#В Swagger UI эти эндпоинты будут сгруппированы под заголовком "categories".
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(path="/")
async def get_all_categories():
    """
    Возвращает список всех категорий товаров.
    """
    return {"message": "Список всех категорий (заглушка)"}


@router.post(path="/")
async def create_category():
    """
    Создает новую категорию.
    """
    return {"message": "Категория создана (заглушка)"}


@router.put(path="/{category_id}")
async def update_category(category_id: int):
    """
    Обновляет категорию по её ID
    """
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete(path="/{category_id}")
async def delete_category(category_id: int):
    """
    Удаляет категорию по её ID
    """
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}
