from sqlalchemy.orm import Session

from db.models import Recipe
from main import RecipeJSON


def create_recipe(db: Session, recipe: RecipeJSON):
    db_recipe = Recipe(
        language=recipe.language,
        title=recipe.title,
        author=recipe.author,
        cook_time=recipe.cook_time,
        host=recipe.host,
        total_time=recipe.total_time,
        image=recipe.image,
        ingredients=str(recipe.ingredients),
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe
