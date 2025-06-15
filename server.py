"""
MCP Google Maps Server - Python based implementation

A Model Context Protocol server providing comprehensive Google Maps API integration
Uses @mcp.tool() decorators and eliminates unnecessary layers
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import attempt with fallback for different execution contexts
try:
    from mcp_google_maps.maps_tools import GoogleMapsTools
except ImportError:
    print("Could not import GoogleMapsTools")
    exit(1)

# Load environment variables
load_dotenv()


# Initialize Fast mcp server
mcp = FastMCP("maps")     # is this how you pass in the server name parameter

# Global Google Maps tools instance
maps_tools: Optional[GoogleMapsTools] = None

@mcp.tool()
def search_nearby(
    center: Dict[str, Any],
    keyword: Optional[str] = None,    # keyword is like are you searching for coffee shops?
    radius: int = 1000,
    openNow: bool = False,
    minRating: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Search for nearby places.

    Args:
        center: Search center point with 'value'(address/ coordinates) and optional 'isCoordinates' boolean value
        keyword: Search with keyword like (e.g. restaurant, cafe)
        radius: Search radius in meters (default: 1000)
        openNow: only show places that are open now (default: False)
        minRating: Minimum rating requirement 0-5 (Optional)

    Return:
        Dictionary with search results and location information
    """

    if maps_tools is None:
        raise RuntimeError("Google Map Tools not initialized")
    
    try:
        # Get location from either coordinates or address
        location = maps_tools.get_location(center)
        # this will return a dict with "lat" and "long" values

        # Search for places with the current location
        places = maps_tools.search_nearby_places(
            {
                "location": location,
                "keyword": keyword,
                "radius": radius,
                "openNow": openNow,
                "minRating": minRating
            }
        )

        # Format the results
        formatted_places = []
        for place in places:
            formatted_place = {
                "name": place.get('name'),
                "place_id": place.get('place_id'),
                "address": place.get('formatted_address'),
                "location": place.get('geometry', {}).get('location'),
                "rating": place.get('rating'),
                "total_ratings": place.get('user_ratings_total'),
                "open_now": place.get('opening_hours', {}).get('open_now'),
                "types": place.get('types', []),
                "price_level": place.get('price_level'),
                "vicinity": place.get('vicinity')
            }

            formatted_places.append(formatted_place)
        
        return {
            "location": location,
            "places": formatted_places,
            "total_results": len(formatted_places)
        }
    
    except Exception as e:
        raise RuntimeError(f"Search failed: {str(e)}")
    

@mcp.tool()
def get_place_details(placeId: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific place

    Args:
        placeId: Google Maps place ID

    Returns:
        Dictionary with detailed place information
    """

    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        details = maps_tools.get_place_details(placeId)

        # Format the details nicely
        formatted_details = {
            "name": details.get('name'),
            "place_id": placeId,
            "address": details.get('formatted_address'),
            "location": details.get('geometry', {}).get('location'),
            "rating": details.get('rating'),
            "total_ratings": details.get('user_ratings_total'),
            "open_now": details.get('opening_hours', {}).get('open_now'),
            "opening_hours": details.get('opening_hours', {}).get('weekday_text', []),
            "phone": details.get('formatted_phone_number'),
            "international_phone": details.get('international_phone_number'),
            "website": details.get('website'),
            "url": details.get('url'),
            "price_level": details.get('price_level'),
            "types": details.get('types', []),
            "photos": [
                {
                    "photo_reference": photo.get('photo_reference'),
                    "height": photo.get('height'),
                    "width": photo.get('width')
                }
                for photo in details.get('photos', [])
            ],
            "reviews": [
                {
                    "rating": review.get('rating'),
                    "text": review.get('text'),
                    "time": review.get('time'),
                    "author_name": review.get('author_name'),
                    "author_url": review.get('author_url'),
                    "language": review.get('language'),
                    "profile_photo_url": review.get('profile_photo_url'),
                    "relative_time_description": review.get('relative_time_description')
                }
                for review in details.get('reviews', [])
            ]
        }
        
        return formatted_details

    except Exception as e:
        raise RuntimeError(f"Failed to get place details: {str(e)}")
    

@mcp.tool()
def maps_geocode(address: str) -> Dict[str, Any]:
    """
    Convert address to coordinates.
    
    Args:
        address: Address or landmark name to convert
        
    Returns:
        Dictionary with location coordinates and formatted address
    """
    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        result = maps_tools.geocode(address)
        return result
    except Exception as e:
        raise RuntimeError(f"Geocoding failed: {str(e)}")
    

@mcp.tool()
def maps_reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Convert coordinates to address.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with formatted address and address components
    """
    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        result = maps_tools.reverse_geocode(latitude, longitude)
        return result
    except Exception as e:
        raise RuntimeError(f"Reverse geocoding failed: {str(e)}")
    

@mcp.tool()
def maps_distance_matrix(
    origins: List[str], 
    destinations: List[str], 
    mode: str = "driving"
) -> Dict[str, Any]:
    """
    Calculate distances and times between multiple origins and destinations.
    
    Args:
        origins: List of origin addresses or coordinates
        destinations: List of destination addresses or coordinates
        mode: Travel mode - 'driving', 'walking', 'bicycling', or 'transit'
        
    Returns:
        Dictionary with distance and duration matrices
    """
    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        result = maps_tools.calculate_distance_matrix(origins, destinations, mode)
        return result
    except Exception as e:
        raise RuntimeError(f"Distance matrix calculation failed: {str(e)}")
    

@mcp.tool()
def maps_directions(
    origin: str,
    destination: str,
    mode: str = "driving",
    departure_time: Optional[str] = None,
    arrival_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed navigation directions between two points.
    
    Args:
        origin: Origin address or coordinates
        destination: Destination address or coordinates
        mode: Travel mode - 'driving', 'walking', 'bicycling', or 'transit'
        departure_time: Departure time in ISO format (optional)
        arrival_time: Arrival time in ISO format (optional)
        
    Returns:
        Dictionary with route information and step-by-step directions
    """
    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        # Parse datetime strings if provided
        dept_time = None
        arr_time = None
        
        if departure_time:
            try:
                dept_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
            except ValueError:
                dept_time = datetime.fromisoformat(departure_time)
        
        if arrival_time:
            try:
                arr_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
            except ValueError:
                arr_time = datetime.fromisoformat(arrival_time)
        
        result = maps_tools.get_directions(origin, destination, mode, dept_time, arr_time)
        return result
        
    except Exception as e:
        raise RuntimeError(f"Failed to get directions: {str(e)}")


@mcp.tool()
def maps_elevation(locations: List[Dict[str, float]]) -> List[Dict[str, Any]]:
    """
    Get elevation data for locations.
    
    Args:
        locations: List of location dictionaries with 'latitude' and 'longitude' keys
        
    Returns:
        List of elevation data for each location
    """
    if maps_tools is None:
        raise RuntimeError("Google Maps tools not initialized")
    
    try:
        result = maps_tools.get_elevation(locations)
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to get elevation data: {str(e)}")
    

@mcp.resource("google-maps://status")
def get_server_status() -> str:
    """Get the current status of the Google Maps server."""
    if maps_tools is None:
        return "Google Maps tools not initialized"
    
    try:
        # Test with a simple geocoding request
        maps_tools.geocode("Google")
        return "Google Maps API is working correctly"
    except Exception as e:
        return f"Google Maps API error: {str(e)}"
    
def validate_api_key() -> bool:
    """
    Validate that the API key is working by making a simple request.
    
    Returns:
        True if API key is valid, False otherwise
    """
    if maps_tools is None:
        return False
    
    try:
        # Try a simple geocoding request
        maps_tools.geocode("Google")
        return True
    except Exception:
        return False
    
def main():
    """Main function to run the server."""
    global maps_tools
    
    try:
        # Initialize the Google Maps tools
        maps_tools = GoogleMapsTools()
        
        # Validate API key on startup
        if not validate_api_key():
            print("Warning: Google Maps API key validation failed. Please check your API key.")
            print("Make sure GOOGLE_MAPS_API_KEY environment variable is set correctly.")
        else:
            print("✅ Google Maps API key validated successfully.")
        
        print("Starting MCP Google Maps Server...")
        print("Server is ready to receive requests!")
        
        # Run the FastMCP server
        mcp.run()
        
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as error:
        print(f"Server error: {error}")
        raise


if __name__ == "__main__":
    main()