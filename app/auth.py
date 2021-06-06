from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from os import getenv

from .databases import schemas
from .databases.database import get_db
from .databases.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = getenv('SECRET_KEY', 'meow')
ALGORITHM = getenv('ALGORITHM', 'HS256')


async def create_access_token(
    data: schemas.TokenData,
    expires_delta: timedelta = timedelta(days=30),
) -> str:
    payload = data.dict()
    payload.update({'exp': datetime.utcnow() + expires_delta})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> schemas.User:
    credentials_exception = HTTPException(403)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: int = payload.get('id')
        username: str = payload.get('username')

        if username is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id, username=username)
    except PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.id).one_or_none()

    if user is None:
        raise credentials_exception

    return user


# TODO
def is_admin():
    pass
