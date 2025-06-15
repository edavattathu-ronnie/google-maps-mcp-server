import asyncio
import os
from dotenv import load_dotenv
from mcp_google_maps.maps_tools import GoogleMapsTools

load_dotenv()


async def test_google_maps():
    """
    Test Google Maps functionality
    """

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("GOOGLE_MAPS_API_KEY not found in .env file")

    try:
        tools = GoogleMapsTools()
        print("Testing API keys...")
        result = tools.geocode("Google Headquarters")
        print(f"API key works, Google HQ is at: {result['location']}")

        print("Now next let's test the functionality of searching nearby places")
        location = tools.get_location({
            "value": "Eindhoven Central",
            "isCoordinate": False
        })

        places = tools.search_nearby_places({
            "location": location,
            "keyword": "pizza",
            "radius": 1000
        })

        print(f"Found {len(places)} pizza places near Eindhoven Central")
        if places:
            print(f"First result: {places[0].get('name')}")
        print("\n All tests passed!")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_maps())