from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from shared.location_service import LocationService

router = APIRouter(
    prefix="/location",
    tags=["location"],
    responses={404: {"description": "Not found"}}
)

def get_location_service() -> LocationService:
    """Dependency to get LocationService instance."""
    return LocationService()

@router.get("/details/{address}")
async def get_location_details(
    address: str,
    location_service: LocationService = Depends(get_location_service)
) -> Dict[str, Any]:
    """Get detailed information about a location including weather and nearby places."""
    result = location_service.get_location_details(address)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/advice/{address}")
async def get_location_advice(
    address: str,
    location_service: LocationService = Depends(get_location_service)
) -> Dict[str, Any]:
    """Get contextual advice based on location."""
    location_details = location_service.get_location_details(address)
    if "error" in location_details:
        raise HTTPException(status_code=404, detail=location_details["error"])
    
    advice = location_service.get_contextual_advice(location_details)
    if "error" in advice:
        raise HTTPException(status_code=500, detail=advice["error"])
    
    return {
        "location": location_details["formatted_address"],
        "advice": advice
    }

@router.get("/commute")
async def get_commute_info(
    origin: str,
    destination: str,
    location_service: LocationService = Depends(get_location_service)
) -> Dict[str, Any]:
    """Get commute information between two locations."""
    result = location_service.get_commute_info(origin, destination)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result 