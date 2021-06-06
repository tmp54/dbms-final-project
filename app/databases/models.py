from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(String)
    location = Column(String)

    follows = relationship('Follow', backref='user', lazy='joined')


class Fruit(Base):
    __tablename__ = 'fruits'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)

    months = relationship('FruitMonth', backref='fruit', lazy='joined')
    #  prices = relationship('DailyHistoryPrice', backref='fruit', lazy='joined')
    monthly_price = relationship('MonthlyHistoryPrice', backref='fruit', lazy='joined')
    #  locations = relationship('Location', secondary='FruitLocation')


class FruitMonth(Base):
    __tablename__ = 'fruit_months'

    fruit_id = Column(String, ForeignKey('fruits.id'), primary_key=True)
    month = Column(Integer, primary_key=True)


class DailyHistoryPrice(Base):
    __tablename__ = 'daily_history_prices'

    fruit_id = Column(String, ForeignKey('fruits.id'), primary_key=True)
    trading_date = Column(Date(), primary_key=True)
    price = Column(Float)

    #  fruit = relationship('Fruit', uselist=False, backref='prices', lazy='joined')


class MonthlyHistoryPrice(Base):
    __tablename__ = 'monthly_history_prices'

    fruit_id = Column(String, ForeignKey('fruits.id'), primary_key=True)
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    price = Column(Float)


class Follow(Base):
    __tablename__ = 'follows'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    fruit_id = Column(String, ForeignKey('fruits.id'), primary_key=True)
    followed_at = Column(DateTime(), server_default=func.now())

    fruit = relationship('Fruit', lazy='joined')


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Market(Base):
    __tablename__ = 'markets'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class FruitLocation(Base):
    __tablename__ = 'fruit_locations'

    fruit_id = Column(String, ForeignKey('fruits.id'), primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), primary_key=True)

    location = relationship('Location', lazy='joined')

