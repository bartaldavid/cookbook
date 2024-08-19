from fastapi import FastAPI, HTTPException
from recipe_scrapers import scrape_html
import requests
import validators

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/recipe")
def read_item(url: str):
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
