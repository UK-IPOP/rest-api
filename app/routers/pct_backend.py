import enum
import requests
import datetime
import json
import os


from github import Github
from fastapi import APIRouter
from pytz import timezone

api = APIRouter(prefix="/pct", tags=["pct"])

eastern = timezone("US/Eastern")
token = os.environ.get("GITHUB_TOKEN")
g = Github(token)


class TrackEnum(enum.Enum):
    HIGH = "LRTI high-acuity or Sepsis"
    LOW = "LRTI low/moderate-acuity"


class LevelEnum(enum.Enum):
    A = "<0.25 or drop by >90%"
    B = "0.25 - 0.49 or drop by >80%"
    C = "0.50 - 0.99"
    D = ">1.00%"
    E = "<0.10 or drop by >90%"
    F = "0.10 - 0.24 or drop by >80%"
    G = "0.25 - 0.50"
    H = ">0.50"


@api.get(
    "/update",
    summary="Backend for PCT-Decision Tool.",
    response_description="Returns simple message stating query accepted.",
    include_in_schema=False,
)
async def home(track: TrackEnum, level: LevelEnum) -> dict[str, dict[str, str]]:
    """
    ## Update json records for PCT-Decision tool.

    This route updates the json file found on the GitHub repo for the
    UK IPOP PCT Decision tool.

    Args:
    # TODO: add validation for level?  usable in swagger docs?

    - track: *The track of the patient.*
    - level: *The level of procalictonin.*

    Returns:

    - Message specifying that query was handled successfully.
    """

    # setup
    repo = g.get_repo("UK-IPOP/pct-decision-tool")

    # get current data inside file
    data = requests.get(
        "https://raw.githubusercontent.com/uk-ipop/pct-decision-tool/main/data/records.json"
    ).json()

    # get sha value from last commit
    sha_val = (
        requests.get(
            "https://api.github.com/repos/uk-ipop/pct-decision-tool/contents/data/records.json"
        )
        .json()
        .get("sha")
    )

    new_data = {
        "track": track.value,
        "range": level.value,
        "timestamp": str(datetime.datetime.now(eastern)),
    }
    data.append(new_data)

    # update file using PUT

    # dynamic commit message
    repo.update_file(
        path="data/records.json",
        message=f"Adding more data at {datetime.datetime.now(eastern)}",
        content=json.dumps(data),
        sha=sha_val,
    )
    return {"data": {"message": "Data successfully added."}}
