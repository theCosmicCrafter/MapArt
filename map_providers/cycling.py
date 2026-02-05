"""Cycling route map data fetching using CyclOSM/OpenStreetMap data."""
import osmnx as ox
import time
from typing import Optional

try:
    from geopandas import GeoDataFrame
except ImportError:
    GeoDataFrame = None

# OSM tags for cycling infrastructure
CYCLE_TAGS = {
    "highway": ["cycleway"],
    "bicycle": ["yes", "designated"],
    "route": ["bicycle"],
}

def fetch_cycling_routes(point, dist) -> Optional[object]:
    """Fetch cycling routes from OpenStreetMap."""
    try:
        # Fetch cycleways
        cycleways = ox.features_from_point(
            point, tags={"highway": "cycleway"}, dist=dist
        )
        time.sleep(0.3)
        
        # Fetch bicycle-designated roads
        bike_roads = ox.features_from_point(
            point, tags={"bicycle": "designated"}, dist=dist
        )
        time.sleep(0.3)
        
        # Combine if both exist
        if cycleways is not None and bike_roads is not None:
            return cycleways.append(bike_roads)
        return cycleways or bike_roads
    except Exception as e:
        print(f"[!] Error fetching cycling data: {e}")
        return None

def fetch_bike_shops(point, dist) -> Optional[object]:
    """Fetch bike shops and repair stations."""
    try:
        shops = ox.features_from_point(
            point, tags={"shop": "bicycle"}, dist=dist
        )
        time.sleep(0.3)
        return shops
    except Exception as e:
        return None

def get_cycling_colors():
    """Return color scheme optimized for cycling maps."""
    return {
        "bg": "#f5f5f5",
        "cycleway": "#16c79a",  # Green for dedicated bike paths
        "bike_lane": "#f9a825",  # Amber for bike lanes
        "shared": "#0f3460",  # Blue for shared routes
        "shop": "#e94560",  # Red for bike shops
        "text": "#1a1a2e",
        "gradient_color": "#f5f5f5",
    }

def get_cycling_line_color(way_type: str) -> str:
    """Get color based on cycling way type."""
    colors = {
        "cycleway": "#16c79a",
        "path": "#4caf50",
        "track": "#8bc34a",
        "shared": "#f9a825",
    }
    return colors.get(way_type, "#0f3460")
