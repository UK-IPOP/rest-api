from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import markdown
from fastapi import status

from .routers import geocoding

# TODO: add custom parameters
# TODO: add subfolders with routers


app = FastAPI(
    title="UK IPOP",
    description="This is a REST API for various endpoints provided by IPOP.",
    version="0.1.0",
)

app.include_router(geocoding.api)


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
    with open("./pages/homepage.md") as f:
        converted = markdown.markdown(f.read())
        return HTMLResponse(converted)
