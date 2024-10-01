from pydantic import BaseModel


class IngredientGroupSchema(BaseModel):
    ingredients: list[str]
    purpose: str | None = None


class RecipeScraperResult(BaseModel):
    title: str
    author: str
    description: str | None = None
    host: str
    cook_time: int | None = None
    total_time: int | None = None
    prep_time: int | None = None
    image: str
    ingredients: list[str]
    ingredient_groups: list[IngredientGroupSchema]
    instructions: str
    instructions_list: list[str]
    language: str
    site_name: str | None = None
    image: str
    canonical_url: str


class RecipeFromDatabase(BaseModel):
    id: int
    language: str | None = None
    author: str | None = None
    description: str | None = None
    host: str | None = None
    cook_time: int | None = None
    total_time: int | None = None
    prep_time: int | None = None
    image: str | None = None
    title: str | None = None
    ingredient_groups: list[IngredientGroupSchema]
    instructions_list: list[str]
    url: str | None = None
