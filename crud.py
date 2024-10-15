import logging

from pydantic import ValidationError
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from .models import Ingredient, IngredientGroup, InstructionStep, Recipe
from .schemas import (
    IngredientGroupSchema as IngredientGroupSchema,
)
from .schemas import (
    RecipeFromDatabase,
    RecipeScraperResult,
)


def save_recipe_to_db(db: Session, recipe: RecipeScraperResult) -> int:
    db_recipe_id = db.execute(
        insert(Recipe)
        .values(
            language=recipe.language,
            title=recipe.title,
            author=recipe.author,
            cook_time=recipe.cook_time,
            host=recipe.host,
            total_time=recipe.total_time,
            image=recipe.image,
            prep_time=recipe.prep_time,
            url=recipe.canonical_url,
            description=recipe.description,
        )
        .returning(Recipe.id)
    ).scalar_one()

    for ingredient_group in recipe.ingredient_groups:
        ingredient_group_db = db.execute(
            insert(IngredientGroup)
            .values(name=ingredient_group.purpose, recipe_id=db_recipe_id)
            .returning(IngredientGroup)
        )
        ingredient_group_db = ingredient_group_db.scalar_one()

        for ingredient in ingredient_group.ingredients:
            db.execute(
                insert(Ingredient).values(
                    name=ingredient,
                    recipe_id=db_recipe_id,
                    ingredient_group_id=ingredient_group_db.id,
                )
            )

    instructions = [
        {"instruction": instruction, "recipe_id": db_recipe_id, "order": idx}
        for idx, instruction in enumerate(recipe.instructions_list)
    ]
    db.execute(insert(InstructionStep), instructions)

    db.commit()

    return db_recipe_id


def get_recipe_from_db(
    db: Session,
    recipe_id: int | None = None,
    url: str | None = None,
    nanoid: str | None = None,
) -> RecipeFromDatabase | None:
    
    recipe: Recipe | None = None

    if recipe_id:
        recipe = db.get(Recipe, recipe_id)
    if url:
        recipe = db.execute(
            select(Recipe).where(Recipe.url == url)
        ).scalar_one_or_none()
    if nanoid:
        recipe = db.execute(
            select(Recipe).where(Recipe.nanoid == nanoid)
        ).scalar_one_or_none()

    if not recipe:
        return None

    ingredient_groups = db.execute(
        select(
            IngredientGroup.id,
            IngredientGroup.name,
            func.group_concat(Ingredient.name, ",").label("ingredients"),
        )
        .join(Ingredient, IngredientGroup.id == Ingredient.ingredient_group_id)
        .where(IngredientGroup.recipe_id == recipe.id)
        .group_by(IngredientGroup.id, IngredientGroup.name)
    ).all()

    ingredient_groups_processed = [
        IngredientGroupSchema(
            purpose=group.name,
            ingredients=group.ingredients.split(",") if group.ingredients else [],
        )
        for group in ingredient_groups
    ]

    instructions = db.scalars(
        select(InstructionStep)
        .where(InstructionStep.recipe_id == recipe.id)
        .order_by(InstructionStep.order)
    ).all()

    try:
        result = RecipeFromDatabase(
            **recipe.__dict__,
            ingredient_groups=ingredient_groups_processed,
            instructions_list=[step.instruction for step in instructions],
        )

        return result
    except ValidationError as e:
        logging.error(f"Error validating recipe {e.errors()}")
        return None


def get_all_recipes(db: Session):
    recipes = db.execute(select(Recipe.nanoid, Recipe.title)).all()
    return recipes
