from recipe_scrapers import scrape_html
from .schemas import RecipeScraperResult
from nanoid import generate
import httpx

async def scrape_recipe_from_url(url: str) -> RecipeScraperResult:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        scraper = scrape_html(html=response.text, org_url=url)
        recipe_json = scraper.to_json()
        return RecipeScraperResult(**recipe_json)


def generate_url_safe_nanoid() -> str:
    return generate(
        alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz",
        size=12,
    )
