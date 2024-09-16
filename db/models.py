from sqlalchemy import Column, ForeignKey, Integer, String
from .db import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String)
    title = Column(String)
    author = Column(String)
    cook_time = Column(Integer)
    host = Column(String)
    total_time = Column(Integer)
    image = Column(String)
    ingredients = Column(String)


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))


class InstructionStep(Base):
    __tablename__ = "instruction_steps"

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer)
    step = Column(String)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
