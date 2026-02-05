"""Railway map data fetching and rendering using OpenStreetMap data."""

import osmnx as ox
import time
from typing import Optional

try:
    from geopandas import GeoDataFrame
except ImportError:
    GeoDataFrame = None

RAILWAY_TAGS = {
    "railway": [
        "rail",
        "subway",
        "tram",
        "light_rail",
        "monorail",
        "funicular",
    ]
}

STATION_TAGS = {"railway": ["station", "halt", "tram_stop"]}


def fetch_railway_network(point, dist) -> Optional[object]:
    """Fetch railway network from OpenStreetMap."""
    try:
        # Fetch railway lines
        railways = ox.features_from_point(
            point, tags={"railway": RAILWAY_TAGS["railway"]}, dist=dist
        )
        time.sleep(0.3)  # Rate limiting
        return railways
    except Exception as e:
        print(f"[!] Error fetching railway data: {e}")
        return None


def fetch_railway_stations(point, dist) -> Optional[object]:
    """Fetch railway stations from OpenStreetMap."""
    try:
        stations = ox.features_from_point(
            point, tags={"railway": STATION_TAGS["railway"]}, dist=dist
        )
        time.sleep(0.3)
        return stations
    except Exception as e:
        print(f"[!] Error fetching station data: {e}")
        return None


def get_railway_colors():
    """Return color scheme optimized for railway maps."""
    return {
        "bg": "#1a1a2e",
        "rail": "#e94560",  # Bright red for main rails
        "subway": "#0f3460",  # Dark blue for subway
        "tram": "#16c79a",  # Green for tram
        "light_rail": "#f9a825",  # Amber for light rail
        "station": "#ffffff",  # White for stations
        "text": "#eaeaea",
        "gradient_color": "#1a1a2e",
    }


def get_railway_line_color(railway_type: str) -> str:
    """Get color based on railway type."""
    colors = {
        "rail": "#e94560",
        "subway": "#0f3460",
        "tram": "#16c79a",
        "light_rail": "#f9a825",
        "monorail": "#9c27b0",
        "funicular": "#ff5722",
    }
    return colors.get(railway_type, "#888888")


def get_railway_line_width(railway_type: str) -> float:
    """Get line width based on railway type."""
    widths = {
        "rail": 1.2,
        "subway": 1.0,
        "tram": 0.8,
        "light_rail": 0.8,
        "monorail": 0.6,
        "funicular": 0.6,
    }
    return widths.get(railway_type, 0.5)


# Alias for compatibility
fetch_railways = fetch_railway_network
