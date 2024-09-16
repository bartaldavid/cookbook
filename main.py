from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from recipe_scrapers import scrape_html
import requests
import validators
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import db.models as models
from db.crud import create_recipe
from db.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")


class RecipeJSON(BaseModel):
    title: str
    author: str
    host: str
    cook_time: int | None = None
    total_time: int | None = None
    prep_time: int | None = None
    image: str
    ingredients: list[str]
    # ingredient_groups: AbstractScraper.ingredient_groups
    instructions: str
    instructions_list: list[str]
    language: str
    site_name: str
    image: str


@app.get("/recipe")
def read_item(
    request: Request,
    url: str,
    hx_request: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> RecipeJSON | HTMLResponse:
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        res = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Could not fetch the URL" + str(e))

    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="Request failed with status code: " + str(res.status_code),
        )

    try:
        scraper = scrape_html(html=str(res.content), org_url=url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Could not scrape html: " + str(e),
        )

    recipe = RecipeJSON.model_validate_json(scraper.to_json())

    create_recipe(db, recipe)

    if hx_request != "true":
        return recipe

    return templates.TemplateResponse(
        request=request, name="recipe.html", context=dict(recipe=recipe)
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="recipe-url-form.html", context={}
    )
