import os
from typing import Dict, Any, Optional, List
import googlemaps
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the parent directory path and load .env from there
parent_dir = Path(__file__).resolve().parent.parent
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)

class LocationService:
    """Service for handling location-based operations using Google Maps API."""
    
    def __init__(self):
        # Initialize configuration - .env is already loaded by main.py
        self.mock_mode = os.getenv("MOCK_LOCATION_SERVICE", "false").lower() == "true"
        
        # Initialize clients
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize API clients with proper error handling."""
        if not self.mock_mode:
            try:
                api_key = os.getenv("GOOGLE_MAPS_API_KEY")
                if not api_key:
                    logger.warning("GOOGLE_MAPS_API_KEY not found in environment, falling back to mock mode")
                    self.mock_mode = True
                    return
                    
                self.gmaps = googlemaps.Client(key=api_key)
                self.tf = TimezoneFinder()
                logger.info("Successfully initialized Google Maps client")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {str(e)}")
                self.mock_mode = True
                logger.warning("Falling back to mock mode due to initialization error")

    def _get_mock_location(self, address: str) -> Dict[str, Any]:
        """Generate mock location data for testing."""
        return {
            "formatted_address": f"Mock address for: {address}",
            "coordinates": {"lat": 37.7749, "lng": -122.4194},
            "timezone": {
                "name": "America/Los_Angeles",
                "current_time": datetime.now().isoformat(),
                "offset": -7.0
            },
            "nearby_places": [
                {
                    "name": "Mock Restaurant",
                    "type": "restaurant",
                    "rating": 4.5,
                    "vicinity": "123 Mock St"
                }
            ]
        }

    def _get_mock_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Generate mock route data for testing."""
        return {
            "distance": {"text": "5.0 km", "value": 5000},
            "duration": {"text": "10 mins", "value": 600},
            "steps": [
                {
                    "instruction": "Mock instruction",
                    "distance": {"text": "1 km"},
                    "duration": {"text": "2 mins"}
                }
            ]
        }

    def get_location_details(self, address: str) -> Dict[str, Any]:
        """Get detailed information about a location."""
        if self.mock_mode:
            logger.info(f"Using mock data for address: {address}")
            return self._get_mock_location(address)

        try:
            # Geocode the address
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                return {"error": "Location not found"}
            
            location = geocode_result[0]
            lat = location['geometry']['location']['lat']
            lng = location['geometry']['location']['lng']
            
            # Get timezone
            timezone_str = self.tf.timezone_at(lat=lat, lng=lng)
            timezone = pytz.timezone(timezone_str)
            current_time = datetime.now(timezone)
            
            # Get nearby places
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=1000,
                type=['restaurant', 'cafe', 'grocery_or_supermarket', 'park']
            )
            
            return {
                "formatted_address": location['formatted_address'],
                "coordinates": {"lat": lat, "lng": lng},
                "timezone": {
                    "name": timezone_str,
                    "current_time": current_time.isoformat(),
                    "offset": timezone.utcoffset(datetime.now()).total_seconds() / 3600
                },
                "nearby_places": [
                    {
                        "name": place['name'],
                        "type": place['types'][0],
                        "rating": place.get('rating'),
                        "vicinity": place['vicinity']
                    }
                    for place in places_result.get('results', [])[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Error getting location details: {str(e)}")
            return {"error": f"Error getting location details: {str(e)}"}

    def get_contextual_advice(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual advice based on location data."""
        if "error" in location_data:
            return location_data

        try:
            advice = {"general": [], "activities": [], "time": []}
            
            # Time-based advice
            if "timezone" in location_data:
                current_time = datetime.fromisoformat(location_data["timezone"]["current_time"])
                self._add_time_based_advice(advice, current_time.hour)
            
            # Activity suggestions
            if "nearby_places" in location_data:
                self._add_place_based_advice(advice, location_data["nearby_places"])
            
            return advice
        except Exception as e:
            logger.error(f"Error generating advice: {str(e)}")
            return {"error": f"Error generating advice: {str(e)}"}

    def _add_time_based_advice(self, advice: Dict[str, List[str]], hour: int) -> None:
        """Add time-based advice to the advice dictionary."""
        if 6 <= hour < 10:
            advice["time"].append("Good morning! Perfect time for breakfast.")
        elif 11 <= hour < 14:
            advice["time"].append("Lunchtime approaching - check out nearby restaurants!")
        elif 17 <= hour < 21:
            advice["time"].append("Evening time - consider dinner plans.")
        elif hour >= 22 or hour < 6:
            advice["time"].append("It's late - make sure to get enough rest.")

    def _add_place_based_advice(self, advice: Dict[str, List[str]], places: List[Dict[str, Any]]) -> None:
        """Add place-based advice to the advice dictionary."""
        restaurants = [p for p in places if p["type"] == "restaurant"]
        parks = [p for p in places if p["type"] == "park"]
        
        if restaurants:
            top_restaurant = max(restaurants, key=lambda x: x.get("rating", 0))
            advice["activities"].append(
                f"Highly rated restaurant nearby: {top_restaurant['name']}"
            )
        
        if parks:
            advice["activities"].append(
                f"There's a park nearby ({parks[0]['name']}) - perfect for a walk!"
            )

    def get_commute_info(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get commute information between two locations."""
        if self.mock_mode:
            logger.info(f"Using mock data for commute from {origin} to {destination}")
            return {"routes": [self._get_mock_route(origin, destination)]}

        try:
            directions = self.gmaps.directions(
                origin,
                destination,
                mode="driving",
                alternatives=True,
                departure_time=datetime.now()
            )
            
            if not directions:
                return {"error": "No route found"}
            
            routes = []
            for route in directions:
                leg = route['legs'][0]
                routes.append({
                    "distance": leg['distance'],
                    "duration": leg['duration'],
                    "duration_in_traffic": leg.get('duration_in_traffic'),
                    "steps": [
                        {
                            "instruction": step['html_instructions'],
                            "distance": step['distance'],
                            "duration": step['duration']
                        }
                        for step in leg['steps']
                    ]
                })
            
            return {
                "routes": routes,
                "best_route": routes[0],
                "alternative_count": len(routes) - 1
            }
        except Exception as e:
            logger.error(f"Error getting commute info: {str(e)}")
            return {"error": f"Error getting commute info: {str(e)}"}

    def get_location_info(self, address: str) -> Dict[str, Any]:
        if self.mock_mode:
            # Return mock data for testing
            return {
                "formatted_address": f"Mock address for: {address}",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timezone": "America/Los_Angeles"
            }

        try:
            # Geocode the address
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                return None

            location = geocode_result[0]
            lat = location['geometry']['location']['lat']
            lng = location['geometry']['location']['lng']
            
            # Get timezone
            timezone = self.tf.timezone_at(lat=lat, lng=lng)

            return {
                "formatted_address": location['formatted_address'],
                "latitude": lat,
                "longitude": lng,
                "timezone": timezone
            }
        except Exception as e:
            print(f"Error getting location info: {str(e)}")
            return None

    def get_distance_matrix(
        self, origin: str, destination: str
    ) -> Dict[str, Any]:
        if self.mock_mode:
            # Return mock data for testing
            return {
                "distance": {
                    "text": "5.0 km",
                    "value": 5000
                },
                "duration": {
                    "text": "10 mins",
                    "value": 600
                }
            }
        
        try:
            matrix = self.gmaps.distance_matrix(origin, destination)
            if matrix["rows"]:
                element = matrix["rows"][0]["elements"][0]
                return {
                    "distance": element["distance"],
                    "duration": element["duration"]
                }
            return {"error": "Route not found"}
        except Exception as e:
            return {"error": str(e)} 