from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from ..auth import get_current_user
from ..databases.database import get_db
from ..databases import schemas

from ..databases.models import Follow, Fruit

router = APIRouter()


@router.post(
    '/{id}',
    response_model=schemas.Follow,
    responses={
        404: { 'description': 'Fruit not found.' },
        409: { 'description': 'Already followed.' },
    },
)
async def create_follow_by_id(
    id: str,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user),
):
    fruit = db.query(Fruit) \
        .filter(Fruit.id == id) \
        .one_or_none()

    if fruit is None:
        raise HTTPException(404)

    try:
        follow = Follow(user_id=user.id, fruit_id=id)

        db.add(follow)
        db.commit()
        db.refresh(follow)

        print(jsonable_encoder(follow))

        return {
            'id': follow.fruit_id,
            'name': follow.fruit.name,
        }
    except:
        raise HTTPException(409)


@router.delete(
    '/{id}',
    response_model=schemas.Follow,
    responses={
        404: { 'description': 'Not found.' },
    },
)
async def delete_follow_by_id(
    id: str,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user),
):
    follow = db.query(Follow) \
        .filter(Follow.user_id == user.id) \
        .filter(Follow.fruit_id == id) \
        .one_or_none()

    if follow is None:
        raise HTTPException(404)

    db.query(Follow) \
        .filter(Follow.user_id == user.id) \
        .filter(Follow.fruit_id == id) \
        .delete()
    db.commit()

    return


@router.get(
    '',
    response_model=List[schemas.Follow]
)
async def get_all_follows(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user),
):
    follows = db.query(Follow).filter(Follow.user_id == user.id).all()

    return [{
        'id': f.fruit_id,
        'name': f.fruit.name,
    } for f in follows]

