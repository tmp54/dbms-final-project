from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from ..databases.database import get_db
from ..databases import schemas

from ..databases.models import Fruit

router = APIRouter()

