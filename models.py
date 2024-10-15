from typing import Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .utils import generate_url_safe_nanoid

Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    language: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    author: Mapped[Optional[str]]
    cook_time: Mapped[Optional[int]]
    host: Mapped[Optional[str]]
    total_time: Mapped[Optional[int]]
    image: Mapped[Optional[str]]
    prep_time: Mapped[Optional[int]]
    description: Mapped[Optional[str]]
    url: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    nanoid: Mapped[str] = mapped_column(
        unique=True, index=True, default=generate_url_safe_nanoid
    )

    instruction_steps: Mapped[list["InstructionStep"]] = relationship(
        back_populates="recipe"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="recipe")
    ingredient_groups: Mapped[list["IngredientGroup"]] = relationship(
        back_populates="recipe"
    )


class InstructionStep(Base):
    __tablename__ = "instruction_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order: Mapped[int]
    instruction: Mapped[str]
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))

    recipe: Mapped[Recipe] = relationship(back_populates="instruction_steps")


class IngredientGroup(Base):
    __tablename__ = "ingredient_groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str | None]
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))

    recipe: Mapped[Recipe] = relationship(back_populates="ingredient_groups")
    ingredients: Mapped[list["Ingredient"]] = relationship(
        back_populates="ingredient_group"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"))
    ingredient_group_id: Mapped[int] = mapped_column(ForeignKey("ingredient_groups.id"))

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient_group: Mapped[IngredientGroup] = relationship(
        back_populates="ingredients"
    )
