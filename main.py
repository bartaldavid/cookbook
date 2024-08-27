from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from recipe_scrapers import scrape_html
import requests
import validators
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates


app = FastAPI()

templates = Jinja2Templates(directory="templates")


class RecipeJSON(BaseModel):
    title: str
    author: str
    cook_time: int | None
    host: str
    total_time: int | None
    image: str
    ingredients: list[str]
    # ingredient_groups: AbstractScraper.ingredient_groups
    instructions: str
    instructions_list: list[str]
    language: str
    site_name: str
    image: str


@app.get("/recipe")
def read_item(url: str) -> RecipeJSON:
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
        scraper = scrape_html(html=res.content, org_url=url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Could not scrape html: " + str(e),
        )

    return scraper.to_json()
