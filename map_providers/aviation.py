"""
Aviation map provider for airports, flight paths, and airways.
Uses OpenStreetMap data for aviation features.
"""

import time
from typing import cast

import osmnx as ox
from geopandas import GeoDataFrame

from logging_config import logger


def fetch_aviation_features(point, dist) -> tuple[GeoDataFrame | None, GeoDataFrame | None, GeoDataFrame | None]:
    """
    Fetch aviation features from OpenStreetMap.
    
    Returns:
        (airports, runways, airways)
    """
    lat, lon = point
    
    # Airports and airfields
    airports = None
    try:
        airport_tags = {
            "aeroway": ["aerodrome", "airport", "helipad"],
            "amenity": "airport"
        }
        airports = ox.features_from_point(point, tags=airport_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch airports: {e}")
    
    # Runways and taxiways
    runways = None
    try:
        runway_tags = {
            "aeroway": ["runway", "taxiway", "apron", "hangar"]
        }
        runways = ox.features_from_point(point, tags=runway_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch runways: {e}")
    
    # Airways (simplified - typically not in OSM, but we can get air corridors)
    airways = None
    try:
        # Airways are typically not mapped in OSM, but we can look for navigation aids
        airway_tags = {
            "aeroway": ["navigationaid", "beacon", "ils"],
            "man_made": "beacon"
        }
        airways = ox.features_from_point(point, tags=airway_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch airways: {e}")
    
    return (
        cast(GeoDataFrame, airports) if airports is not None else None,
        cast(GeoDataFrame, runways) if runways is not None else None,
        cast(GeoDataFrame, airways) if airways is not None else None
    )


def get_aviation_color_scheme() -> dict:
    """
    Get color scheme optimized for aviation maps.
    
    Returns:
        dict with color values for aviation features
    """
    return {
        "airport": "#4169E1",      # Royal blue for airports
        "runway": "#2F4F4F",       # Dark slate gray for runways
        "taxiway": "#696969",      # Dim gray for taxiways
        "airway": "#FF6347",       # Tomato red for airways
        "beacon": "#FFD700",       # Gold for beacons
        "text": "#FFFFFF",
        "bg": "#0a0a0a"
    }
