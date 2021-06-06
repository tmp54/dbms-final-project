from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, text
from sqlalchemy.orm import joinedload, noload, Session
from sqlalchemy.sql import func
from typing import List

from ..databases.database import get_db
from ..databases import schemas

from ..databases.models import (
    DailyHistoryPrice,
    Fruit,
    FruitLocation,
    MonthlyHistoryPrice,
)

router = APIRouter()

responses = {
    404: {},
}


def transform(fruits) -> List[schemas.Fruit]:
    try:
        res = jsonable_encoder(fruits)
    except:
        res = fruits

    #  print(res)

    if isinstance(res, list):
        if len(res) > 0:
            if 'months' in res[0]:
                for i in range(len(res)):
                    res[i]['months'] = [m['month'] for m in res[i]['months']]
            #  if 'prices' in res[0]:
            #      for i in range(len(res)):
            #          res[i]['prices'] = res[i]['prices']['price']
            if 'monthly_price' in res[0]:
                for i in range(len(res)):
                    res[i]['monthly_price'] = [{
                        'price': m['price'],
                        'year': m['year'],
                        'month': m['month']
                    } for m in res[i]['monthly_price']]
    elif res is not None:
        if 'months' in res:
            res['months'] = [m['month'] for m in res['months']]
        #  if 'prices' in res:
        #      res['prices'] = res['prices']['price']
        if 'monthly_price' in res:
            res['monthly_price'] = [{
                'price': m['price'],
                'year': m['year'],
                'month': m['month']
            } for m in res['monthly_price']]

    return res


@router.get('', response_model=List[schemas.Fruit])
async def get_all_fruits(db: Session = Depends(get_db)):
    yesterday = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')

    res = db.query(Fruit) \
        .options(noload('monthly_price')) \
        .all()

    res = jsonable_encoder(res)

    prices = db.query(DailyHistoryPrice) \
        .filter(DailyHistoryPrice.trading_date == yesterday) \
        .all()

    prices = jsonable_encoder(prices)

    locations = db.query(FruitLocation) \
        .all()

    locations = jsonable_encoder(locations)

    location_data = {}
    for i in locations:
        if i['fruit_id'] not in location_data:
            location_data[i['fruit_id']] = []
        location_data[i['fruit_id']].append({
            'id': i['location']['id'],
            'name': i['location']['name'],
        })

    for i in range(len(res)):
        price = next(filter(lambda x: x['fruit_id'] == res[i]['id'], prices), None)
        res[i]['prices'] = price['price'] if price is not None and 'price' in price else None
        res[i]['locations'] = location_data[res[i]['id']] if res[i]['id'] in location_data else []

    return transform(res)


@router.post('/search', response_model=List[schemas.Fruit])
async def wip_search_fruits(
    data: schemas.SearchFruit,
    db: Session = Depends(get_db)
):
    query = db.query(Fruit)

    if data.months:
        query = query.join(Fruit.months).filter(and_(Fruit.months.any(month=m) for m in data.months))

    if data.id:
        query = query.filter(Fruit.id.like(f'%{data.id}%'))

    if data.name:
        query = query.filter(Fruit.name.like(f'%{data.name}%'))

    res = jsonable_encoder(query.all())

    yesterday = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    prices = db.query(DailyHistoryPrice) \
        .filter(DailyHistoryPrice.trading_date == yesterday) \
        .all()

    prices = jsonable_encoder(prices)

    locations = db.query(FruitLocation).all()

    locations = jsonable_encoder(locations)

    location_data = {}
    for i in locations:
        if i['fruit_id'] not in location_data:
            location_data[i['fruit_id']] = []
        location_data[i['fruit_id']].append({
            'id': i['location']['id'],
            'name': i['location']['name'],
        })

    for i in range(len(res)):
        price = next(filter(lambda x: x['fruit_id'] == res[i]['id'], prices), None)
        res[i]['prices'] = price['price'] if price is not None and 'price' in price else None
        res[i]['locations'] = location_data[res[i]['id']] if res[i]['id'] in location_data else []

    res = list(filter(lambda x: any(data.location in y for y in map(lambda l: l['name'], x['locations'])), res))

    return transform(res)


@router.get('/test')
async def test(db: Session = Depends(get_db)):
    res = db.execute(text('select "hello"')).one_or_none()
    return {'hello': res}


@router.get('/{id}', response_model=schemas.Fruit)
async def get_fruit_by_id(id: str, db: Session = Depends(get_db)):
    res = db.query(Fruit) \
        .filter(Fruit.id == id) \
        .first()

    res = jsonable_encoder(res)

    yesterday = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    prices = db.query(DailyHistoryPrice) \
        .filter(DailyHistoryPrice.trading_date == yesterday) \
        .all()

    prices = jsonable_encoder(prices)

    locations = db.query(FruitLocation).all()

    locations = jsonable_encoder(locations)

    location_data = {}
    for i in locations:
        if i['fruit_id'] not in location_data:
            location_data[i['fruit_id']] = []
        location_data[i['fruit_id']].append({
            'id': i['location']['id'],
            'name': i['location']['name'],
        })


    price = next(filter(lambda x: x['fruit_id'] == res['id'], prices), None)
    res['prices'] = price['price'] if price is not None and 'price' in price else None
    res['locations'] = location_data[res['id']] if res['id'] in location_data else []

    return transform(res)


@router.put(
    '/{id}',
    response_model=schemas.Fruit,
    responses={**responses}
)
async def update_fruit_by_id(
    id: str,
    update_fruit: schemas.UpdateFruit,
    db: Session = Depends(get_db)
):
    fruit = db.query(Fruit) \
        .filter(Fruit.id == id) \
        .one_or_none()

    if fruit is None:
        raise HTTPException(404)

    data = jsonable_encoder(update_fruit)

    fruit.name = data['name']

    db.add(fruit)
    db.commit()
    db.refresh(fruit)

    return transform(fruit)


@router.post('', response_model=schemas.Fruit)
async def create_fruit(
    fruit: schemas.CreateFruit,
    db: Session = Depends(get_db)
):
    new_fruit = Fruit(id=fruit.id, name=fruit.name)
    db.add(new_fruit)
    db.commit()
    db.refresh(new_fruit)
    return transform(new_fruit)


@router.delete(
    '/{id}',
    response_model=schemas.Fruit,
    responses={**responses},
)
async def delete_fruit_by_id(id: str, db: Session = Depends(get_db)):
    fruit = db.query(Fruit) \
        .filter(Fruit.id == id) \
        .one_or_none()

    if fruit is None:
        raise HTTPException(404)

    db.query(Fruit) \
        .filter(Fruit.id == id) \
        .delete()
    db.commit()

    return transform(fruit)

