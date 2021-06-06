from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from bcrypt import hashpw, checkpw, gensalt

from ..auth import create_access_token, oauth2_scheme

from ..databases import schemas
from ..databases.database import get_db
from ..databases.models import User

router = APIRouter()


@router.post(
    '/login',
    response_model=schemas.Token,
    responses={
        401: { 'description': 'Login failed.' },
    },
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form.username).one_or_none()

    if not user:
        raise HTTPException(401)

    if not checkpw(form.password.encode(), user.password):
        raise HTTPException(401)

    token = await create_access_token(schemas.TokenData(
        id=user.id,
        username=user.username,
        email=user.email,
    ))

    return {
        'access_token': token,
        'token_type': 'Bearer',
    }


@router.post('/logout')
async def todo_logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    pass


@router.post(
    '/register',
    status_code=201,
    responses={
        409: { 'description': 'Username already exists' },
    },
)
async def register(
    register: schemas.UserRegister,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == register.username).one_or_none()

    if user is not None:
        raise HTTPException(409)

    user = User(
        username=register.username,
        password=hashpw(register.password.encode(), gensalt()),
        email=register.email,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return

