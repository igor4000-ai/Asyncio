from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, autoincrement=True)
    swapi_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    height = Column(String(20), default='')
    mass = Column(String(20), default='')
    hair_color = Column(String(50), default='')
    skin_color = Column(String(50), default='')
    eye_color = Column(String(50), default='')
    birth_year = Column(String(20), default='')
    gender = Column(String(50), default='')
    homeworld = Column(Text, default='')
    starships = Column(Text, default='')
    vehicles = Column(Text, default='')
    films = Column(Text, default='')
