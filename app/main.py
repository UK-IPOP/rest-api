from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from faker import Faker

from .routers import geocoding, pct_backend


app = FastAPI(
    title="UK IPOP",
    description="This is a REST API for various endpoints provided by IPOP.",
    version="0.1.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://uk-ipop.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(geocoding.api)
app.include_router(pct_backend.api)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get(
    path="/",
    tags=["home"],
    summary="Homepage request",
    response_description="Welcome page via markdown.",
    include_in_schema=False,
)
async def home() -> HTMLResponse:
    """
    Request homepage information.

    I think this is **very** cool!
    """
    with open("./pages/index.html") as f:
        return HTMLResponse(f.read())


# TODO: can add more complex functionality
# like filter for gender of name
# like prefixes and suffixes
# see: https://faker.readthedocs.io/en/master/providers/faker.providers.person.html
@app.get(
    path="/fake-name",
    summary="Get a fake name",
    response_description="A fake name",
)
async def fake_name() -> JSONResponse:
    """Get a fake name."""
    faker = Faker()
    return JSONResponse({"name": faker.name()}, status_code=status.HTTP_200_OK)
