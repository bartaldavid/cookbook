import json
import os
from typing import Annotated

import validators
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from .crud import get_all_recipes, get_recipe_from_db, save_recipe_to_db
from .db import SessionLocal, engine
from .models import Base
from .utils import scrape_recipe_from_url

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("AUTH_SECRET", "unsafe-secret-key")
)
config = Config(".env")
oauth = OAuth(config)

GOOGLE_OAUTH_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth.register(
    name="google",
    server_metadata_url=GOOGLE_OAUTH_CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


HX_Request = Annotated[str | None, Header()]

templates = Jinja2Templates(directory="templates")


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)
    return RedirectResponse(url="/")


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
        request=request, name="recipe-details.html", context=dict(recipe=recipe)
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


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
        request=request, name="recipe-details.html", context=dict(recipe=recipe_from_db)
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):
    recipes = get_all_recipes(db)
    user = request.session.get("user")
    user_json = json.dumps(user)

    return templates.TemplateResponse(
        request=request,
        name="recipe-url-form.html",
        context={"recipes": recipes, "user_data": user_json},
    )

@app.post("/favorites/{recipe_nanoid:str}")
def save_recipe_to_favorites(request: Request, recipe_nanoid: str):
    return templates.TemplateResponse(
        request=request,
        name="remove-recipe-button.html",
        context={'recipe': {'nanoid': recipe_nanoid}}
    )

@app.delete("/favorites/{recipe_nanoid:str}")
def remove_recipe_from_favorites(request: Request, recipe_nanoid: str):
    return templates.TemplateResponse(
        request=request,
        name="save-recipe-button.html",
        context={'recipe': {'nanoid': recipe_nanoid}}
    )