from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .databases import models
from .databases.database import engine

from .routers import (
    auth,
    follows,
    fruits,
    users,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    auth.router,
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    follows.router,
    prefix='/follow',
    tags=['follow']
)

app.include_router(
    fruits.router,
    prefix='/fruit',
    tags=['fruit'],
)

app.include_router(
    users.router,
    prefix='/user',
    tags=['user'],
)


@app.get('/')
async def peko():
    return {'Hello': 'World'}

