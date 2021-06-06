from typing import Any, List, Optional
from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    password: str
    registered_at: datetime
    email: str
    location: str

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    username: str
    password: str
    email: str


class TokenData(BaseModel):
    id: int
    username: str
    email: Optional[str]


class FruitMonth(BaseModel):
    fruit_id: str
    month: int

    class Config:
        orm_mode = True


class Location(BaseModel):
    id: int
    name: str


class Fruit(BaseModel):
    id: str
    name: str
    months: List[int]
    prices: float = None
    monthly_price: Optional[Any]
    location: Optional[Location]

    class Config:
        orm_mode = True


class UpdateFruit(BaseModel):
    name: str


class CreateFruit(BaseModel):
    id: str
    name: str


class SearchFruit(BaseModel):
    months: List[int] = []
    id: Optional[str]
    name: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class Follow(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

