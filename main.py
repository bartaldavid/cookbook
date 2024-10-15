from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Header, Request, Response
from fastapi.responses import HTMLResponse
import validators
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .utils import scrape_recipe_from_url

from .crud import get_all_recipes, save_recipe_to_db, get_recipe_from_db
from .db import SessionLocal, engine
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


HX_Request = Annotated[str | None, Header()]

templates = Jinja2Templates(directory="templates")


@app.get("/recipe/url")
async def get_recipe_from_url(
    request: Request,
    url: str,
    hx_request: HX_Request = None,
    db: Session = Depends(get_db),
):
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    recipe = get_recipe_from_db(db, url=url)

    if not recipe:
        recipe = await scrape_recipe_from_url(url)
        save_recipe_to_db(db, recipe)

    # if hx_request != "true":
    #     return recipe

    return templates.TemplateResponse(
        request=request, name="recipe.html", context=dict(recipe=recipe)
    )


@app.get("/recipe/{recipe_nanoid:str}")
def get_recipe_from_db_route(
    request: Request,
    recipe_nanoid: str,
    db: Session = Depends(get_db),
    hx_request: HX_Request = None,
):
    recipe_from_db = get_recipe_from_db(db, nanoid=recipe_nanoid)
    if not recipe_from_db:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # if hx_request != "true":
    #     return recipe_from_db

    return templates.TemplateResponse(
        request=request, name="recipe.html", context=dict(recipe=recipe_from_db)
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):

    recipes = get_all_recipes(db)

    return templates.TemplateResponse(
        request=request, name="recipe-url-form.html", context={"recipes": recipes}
    )
