from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix='/items', tags=['items'])
fake_db = {1: {'name': 'Foo', 'price': 50.2}}


class Item(BaseModel):
    name: str = Field(title='Название', description='Название товара', examples=['Телефон'])
    price: float = Field(gt=0, title='Цена', description='Цена больше нуля', examples=[199.99])
    is_offer: bool | None = Field(None, title='Акционный товар', description='Есть ли акция')


@router.get('/{item_id}', summary='Найти товар', responses={404: {'description': 'Товар не найден'}})
def read_item(
    item_id: int = Path(..., title='ID товара', ge=1),
    q: str | None = Query(None, title='Поисковый запрос', max_length=50),
):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail='Item not found')
    return {'item_id': item_id, 'item': fake_db[item_id], 'q': q}


@router.post('/', response_model=Item, summary='Проверить данные нового товара')
def create_item(item: Item):
    return item
