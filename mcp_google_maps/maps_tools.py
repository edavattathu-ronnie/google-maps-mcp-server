"""
Google Maps API Tools Module

This module provides a wrapper around the Google Maps API for various operations
including geocoding, place search, directions, distance matrix and elevation data.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GoogleMapsTools:
    """
    A comprehensive wrapper for Google Maps API operations.

    This class handles all the interactions with the Google Maps API including:
    - Place search and details
    - Geocoding and reverse geocoding
    - Directions and distance calculations
    - Elevation data retrieval
    """

    def __init__(self, api_key: Optional[str] = None, language: str = 'zh-TW'):
        """
        Initialize the Google Maps Tools

        Args:
            api_key: Google Maps API key. If not provided, will use GOOGLE_MAPS_API_KEY env var
            language: Default language for API responses
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """

        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API Key is required. Set GOOGLE_MAPS_API_KEY environment variable or pass api_key parameter.")
        
        # Create a client object
        self.client = googlemaps.Client(key=self.api_key)
        self.default_language = language

    def parse_coordinates(self, coord_string: str) -> Dict[str, float]:
        """
        Parse coordinate string in format 'lat, long'

        Args:
            coord_string: Coordinates in 'Latitude, Longitude' format

        Returns:
            Dict with 'lat' key and its corresponding value as well as 'long' key with its corresponding value

        Raises:
            ValueError: If coordinate format is invalid
        """
        try:
            coords = [float(c.strip()) for c in coord_string.split(",")]
            if len(coords) != 2:
                # That means both the latitude and the longitude are not present in sync then raise a ValueError
                raise ValueError("Invalid coordinate format")
            return {"lat": coords[0], "lng": coords[1]}
        except (ValueError, IndexError) as e:
            raise ValueError("Invalid coorindate format, please use 'latitude, longitude' format") from e
        
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Convert address to coordinates using Google Maps Geocoding API

        Args:
            address: Address or place name to geocode
            -> which basically means given a name/ place-name, this method/ tool finds the latitude and the longitude of this place

        Returns:
            Dict containing location coordinates and metadata

        Raises:
            ValueError: If address cannot be geocoded
        """

        try:
            result = self.client.geocode(address, language=self.default_language)
            if not result:
                raise ValueError("Address not found")
            
            location_data = result[0]
            location = location_data["geometry"]["location"]

            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": location_data.get("formatted_address", ""),
                "place_id": location_data.get("place_id", "")
            }
        except Exception as e:
            raise ValueError(f"Error geocoding address: {str(e)}") from e

    def get_location(self, center: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get location coordinates from either coordinates string or the address(coming as a string value)

        Args:
            center: Dict with 'value' (string) and optionally 'isCoordinates' (bool)

        Returns:
            Dict with location coordinates
        """

        if center.get("isCoordinates", False):
            return self.parse_coordinates(center["value"])    # this will return a dictionary with two keys, "Latitude" and "Longitude"
        else:
            return self.geocode_address(center["value"])     # center["value"]-> this might be the address (name) of the place, we convert it to dict containing longitude and latitude info along with some other meta_data
        
    def search_nearby_places(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for nearby places using Google Places API.
        
        Args:
            params: Search parameters including location, radius, keyword, etc
            # params would look something like this:
            # location: Geldropseweg, radius: 2km, and keyword: would be find me cafes open right now
            -> and taking all these parameters it searches for nearby options

        Returns:
            List of place results (nearby places)
        
        Raises:
            ValueError: If search fails
        """

        try:
            location = params["location"]
            location_tuple = (location["lat"], location["lng"])

            search_params = {
                'location': location_tuple,     # current origin/ current location
                'radius': params.get("radius", 1000),
                'language': self.default_language
            }

            if params.get("keyword"):
                search_params["keyword"] = params["keyword"]

            if params.get("openNow"):
                search_params["openNow"] = True
                # only find the nearby places which are open right now

            result = self.client.places_nearby(**search_params)    
            places = result.get("results", [])      # "results are actually list of dictionaries, each specifying each nearby places"

            # Filter by minimum rating if specified
            if params.get("minRating"):
                min_rating = params["minRating"]
                places = [place for place in places if place.get("rating", 0) >= min_rating]
            
            return places

        except Exception as e:
            raise ValueError(f"Error searching nearby places: {str(e)}") from e
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific place

        Args:
            place_id: Google Places place ID
        
        Returns:
            Dict containing detailed place information

        Raises:
            ValueError: If place details cannot be retrieved
        """
        try:
            fields = [
                "name", "rating", "formatted_address", "opening_hours",
                "reviews", "geometry", "formatted_phone_number", "website", 
                "price_level", "photos", "user_ratings_total"
            ]

            result = self.client.place(
                place_id=place_id,
                fields=fields,
                language=self.default_language
            )

            return result.get("result", {})    # now here result is just showing detail of a place, and not list of places, so we just have dictionary value in here

        except Exception as e:
            raise ValueError(f"Error getting place details: {str(e)}") from e
        
    def geocode(self, address: str) -> Dict[str, Any]:
        """
        Public method for geocoding an address

        Args:
            address: Address to geocode

        Returns:
            Dict with location, formatted address and place_id
        """

        try:
            result = self.geocode_address(address)
            return {
                "location": {"lat": result["lat"], "lng": result["lng"]},
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"]
            }
        except Exception as e:
            raise ValueError(f"Error geocoding: {str(e)}") from e
        
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Convert coordinates to address (reverse geocoding)

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dict with formatted address and place information
        
        Raises:
            ValueError: If reverse geocoding fails
        """
        try:
            result = self.client.reverse_geocode(
                (latitude, longitude),
                language=self.default_language
            )

            if not result:
                raise ValueError("No address found for coordinates")
            
            location_data = result[0]
            return {
                "formatted_address": location_data.get('formatted_address', ''),
                "place_id": location_data.get('place_id', ''),
                "address_components": location_data.get('address_components', [])
            }
        
        except Exception as e:
            raise ValueError(f"Error reverse geocoding: {str(e)}") from e
        
    def calculate_distance_matrix(self, origins: List[str], destinations: List[str], mode: str = "driving") -> Dict[str, Any]:
        """
        Calculate distance matrix between multiple origins and destinations

        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit')
        
        Returns:
            Dict containing distance and duration matrices
        Raises:
            ValueError: If distance matrix calculation fails
        """

        try:
            result = self.client.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode=mode,
                language=self.default_language
            )

            if result['status'] != 'OK':
                raise ValueError(f"Distance matrix calculation failed: {result['status']}")
            
            distances = []
            durations = []

            for row in result['rows']:
                distance_row = []
                duration_row = []

                for element in row['elements']:
                    if element['status'] == "OK":
                        distance_row.append({
                            'value': element['distance']['value'],
                            'text': element['distance']['text']
                        })
                        duration_row.append({
                            'value': element['duration']['value'],
                            'text': element['duration']['text']
                        })
                    else:
                        distance_row.append(None)
                        duration_row.append(None)

                distances.append(distance_row)
                durations.append(duration_row)

            return {
                "distances": distances,
                "durations": durations,
                "origin_addresses": result['origin_addresses'],
                "destination_addresses": result['destination_addresses']
            }

        except Exception as e:
            raise ValueError(f"Error calculating distance matrix: {str(e)}") from e
        
    def get_directions(self, origin: str, destination: str, mode: str = "driving",
                       departure_time: Optional[datetime] = None,
                       arrival_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get directions between two points.

        Args:
            origin: Origin addresses or the coordinates
            destination: Destination addresses or the coordinates of the same
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit')
            departure_time: Departure time (Optional)
            arrival_time: Arrival time (Optional, mutually exclusive with departure time)

            Why is time a factor for deciding the direction to move, is it something like let's say at this time we have a lot of traffic, and we or the google maps change the direction based on the on-going current traffic

        Returns:
            Dict containing route information and directions
        
        Raises:
            ValueError: If directions cannot be calculated
        """

        try:
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,   # cycle will have a different route compared to car, car will have a different route compared to train, etc, etc!
                "language": self.default_language
            }

            # either we are feeding in the departure time or we are feeding in the arrival time
            if arrival_time:
                params["arrival_time"] = arrival_time
            elif departure_time:
                params["departure_time"] = departure_time
            else:
                params["departure_time"] = departure_time
            
            result = self.client.directions(**params)

            if not result:
                raise ValueError("No route found")
            
            route = result[0]
            leg = route["legs"][0]

            def format_time(time_info):
                """
                Format time info from API response
                """
                if not time_info or 'value' not in time_info:
                    return ""
                return datetime.fromtimestamp(time_info["value"]).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                "routes": result,
                "summary": route.get("summary", ""),
                "total_distance": {
                    "value": leg["distance"]["value"],
                    "text": leg["distance"]["text"]
                },
                "total_duration": {
                    "value": leg['duration']['value'],
                    "text": leg['duration']['text']
                },
                "arrival_time": format_time(leg.get('arrival_time')),
                "departure_time": format_time(leg.get('departure_time'))
            }
        except Exception as e:
            raise ValueError(f"Error getting directions: {str(e)}") from e
        
    def get_elevation(self, locations: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Get elevation data for specified locations.
        
        Args:
            locations: List of dicts with 'latitude' and 'longitude' keys
            
        Returns:
            List of elevation data for each location
            
        Raises:
            ValueError: If elevation data cannot be retrieved
        """
        try:
            formatted_locations = [(loc["latitude"], loc["longitude"]) for loc in locations]

            result = self.client.elevation(formatted_locations)

            return [
                {
                    "elevation": item["elevation"],
                    "location": {"lat": item["location"]["lat"], "lng": item["location"]["lng"]}
                }
                for item in result
            ]
        except Exception as e:
            raise ValueError(f"Error getting elevation data: {str(e)}") from e