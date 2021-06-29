from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import markdown
from fastapi.middleware.cors import CORSMiddleware

from .routers import geocoding, pct_backend


app = FastAPI(
    title="UK IPOP",
    description="This is a REST API for various endpoints provided by IPOP.",
    version="0.1.0",
)

origins = [
    "http://localhost",
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


@app.get(
    path="/",
    tags=["home"],
    summary="Homepage request",
    response_description="Welcome page via markdown.",
)
async def home() -> HTMLResponse:
    """
    Request homepage information.

    I think this is **very** cool!
    """
    with open("./pages/index.html") as f:
        return HTMLResponse(f.read())
