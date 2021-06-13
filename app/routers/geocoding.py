import typing
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel

from geopy.geocoders import ArcGIS
from geopy.adapters import AioHTTPAdapter

import csv
import enum
import codecs

api = APIRouter(prefix="/geo", tags=["geocoding"])


class FileResponseType(enum.Enum):
    _CSV = "CSV"
    _JSON = "JSON"


class GeoData(BaseModel):
    address: str = ""
    altitude: float = 0
    latitude: float = 0
    longitude: float = 0
    score: int = 0


@api.get(
    path="/geocode",
    response_model=GeoData,
    summary="Geocode a single address using ArcGIS geocoder.",
    response_description="Geographic data for the specified address.",
)
async def geocode(address: str) -> GeoData:
    """
    ## Geocode a single address using ArcGIS geocoder.

    Args:

    - address: *Full address you want to geocode*.

    Returns:

    - GeoData: Geographic data for the geocoded address including
    the full geocoded address (which can be compared to the original),
    altitude, latitude, longitude, and a confidence score.
    """
    async with ArcGIS(
        adapter_factory=AioHTTPAdapter,
    ) as geolocator:
        location = await geolocator.geocode(address)
        data_dict = {
            "address": location.address,
            "altitude": location.altitude,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "score": location.raw.get("score"),
        }
        data = GeoData(**data_dict)
        return data


# TODO: create way to link original file to output file
# think joins or something
#  could be as simple as returning an index
@api.post(
    path="/batch-geocode",
    summary="Geocode a file and return a file.",
    response_description="An array of geocoded addresses and details.",
    response_model=list[GeoData],
)
async def batch_geocode(
    output_type: FileResponseType = FileResponseType._JSON,
    file: UploadFile = File(...),
) -> typing.Union[list[GeoData], FileResponse]:
    """Batch geocoding a file.

    This method expects a **\*.csv** file and a column in the
    file labeled `address`.  This may require some pre-processing on
    your part.

    This endpoint will return geocoded results in json or csv depending
    on user specified `output_type` (default to json).
    """
    if output_type not in FileResponseType:
        raise HTTPException(
            status_code=404, detail=f"Invalid output_type {output_type}"
        )
    results = []
    csv_reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    if "address" not in csv_reader.fieldnames:
        raise HTTPException(status_code=404, detail="Column `address` not found.")
    async with ArcGIS(
        adapter_factory=AioHTTPAdapter,
        timeout=5,
    ) as geolocator:
        for row in csv_reader:
            if csv_reader.line_num > 10:
                break
            location = await geolocator.geocode(row["address"])
            data_dict = {
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "score": location.raw.get("score"),
            }
            data = GeoData(**data_dict)
            results.append(data)

    if output_type == FileResponseType._JSON:
        return results
    elif output_type == FileResponseType._CSV:
        records = [r.dict() for r in results]
        keys = records[0].keys()
        with open("data/results.csv", "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(records)
        return FileResponse("data/results.csv")
