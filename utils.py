import requests
from recipe_scrapers import scrape_html
from .schemas import RecipeScraperResult
from nanoid import generate


def download_recipe(url: str) -> RecipeScraperResult:
    response = requests.get(url)
    response.raise_for_status()
    scraper = scrape_html(html=str(response.content, encoding="utf-8"), org_url=url)
    recipe_json = scraper.to_json()
    recipe = RecipeScraperResult(**recipe_json)
    return recipe


def generate_url_safe_nanoid() -> str:
    return generate(
        alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz",
        size=12,
    )
