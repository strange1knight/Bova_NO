import logging

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field, field_validator


router = APIRouter(prefix='/items', tags=['items'])
logger = logging.getLogger(__name__)
fake_db = {
    1: {'name': 'Foo', 'price': 50.2},
    2: {'name': 'Bar', 'price': 30.0},
}


class Item(BaseModel):
    name: str = Field(title='Название', description='Название товара', examples=['Телефон'])
    price: float = Field(gt=0, title='Цена', description='Цена больше нуля', examples=[199.99])
    is_offer: bool | None = Field(None, title='Акционный товар', description='Есть ли акция')

    @field_validator('name')
    @classmethod
    def clean_name(cls, name):
        name = name.strip()
        if not name:
            raise ValueError('Введите название товара')
        return name


def check_name(name, item_id=None):
    for other_id, other_item in fake_db.items():
        if other_id != item_id and other_item['name'].casefold() == name.casefold():
            logger.warning('Название уже используется товаром %s', other_id)
            raise HTTPException(status_code=409, detail='Item name already exists')


@router.get('/{item_id}', summary='Найти товар', responses={404: {'description': 'Товар не найден'}})
def read_item(
    item_id: int = Path(..., title='ID товара', ge=1),
    q: str | None = Query(None, title='Поисковый запрос', max_length=50),
):
    if item_id not in fake_db:
        logger.warning('Товар %s не найден', item_id)
        raise HTTPException(status_code=404, detail='Item not found')
    return {'item_id': item_id, 'item': fake_db[item_id], 'q': q}


@router.post(
    '/', response_model=Item, summary='Проверить данные нового товара',
    responses={409: {'description': 'Название уже используется'}},
)
def create_item(item: Item):
    check_name(item.name)
    logger.info('Данные нового товара проверены')
    return item


@router.put(
    '/{item_id}', response_model=Item, summary='Обновить товар',
    responses={404: {'description': 'Товар не найден'}, 409: {'description': 'Название уже используется'}},
)
def update_item(item: Item, item_id: int = Path(..., title='ID товара', ge=1)):
    if item_id not in fake_db:
        logger.warning('Товар %s не найден', item_id)
        raise HTTPException(status_code=404, detail='Item not found')
    check_name(item.name, item_id)
    fake_db[item_id] = item.model_dump()
    logger.info('Товар %s обновлён', item_id)
    return item
