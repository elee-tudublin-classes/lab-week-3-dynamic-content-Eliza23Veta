# import dependencies
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import httpx
from contextlib import asynccontextmanager
import json
from starlette.config import Config

# Load environment variables from .env
config = Config(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()


# create app instance
app = FastAPI(lifespan=lifespan)
from datetime import datetime

# set location for templates
templates = Jinja2Templates(directory="app/view_templates")

# handle http get requests for the site root /
# return the index.html page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    serverTime: datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    return templates.TemplateResponse("index.html", {"request": request, "serverTime": serverTime })

@app.get("/param", response_class=HTMLResponse)
async def param(request: Request, name: Optional[str] = ""):
    return templates.TemplateResponse("param.html", {"request": request, "name": name})

@app.get("/apod", response_class=HTMLResponse)
async def index(request: Request):

    requests_client = request.app.requests_client
    response = await requests_client.get(config("NASA_APOD_URL") + config("NASA_API_KEY"))
    return templates.TemplateResponse("apod.html", {"request": request, "data": response.json() })

    

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

@app.get("/advice", response_class=HTMLResponse)
async def advice(request: Request):
    
    # Define a request_client instance
    requests_client = request.app.requests_client

    # Connect to the API URL and await the response
    response = await requests_client.get(config("ADVICE_URL"))

    # Send the json data from the response in the TemplateResponse data parameter 
    return templates.TemplateResponse("advice.html", {"request": request, "data": response.json() })