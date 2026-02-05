"""Maritime map provider for nautical charts and shipping lanes."""

import time
from typing import cast

import osmnx as ox
from geopandas import GeoDataFrame

from logging_config import logger


def fetch_maritime_features(point, dist) -> tuple[GeoDataFrame | None, GeoDataFrame | None, GeoDataFrame | None]:
    """
    Fetch maritime features from OpenStreetMap.
    
    Returns:
        (water_features, harbors, seamarks)
    """
    lat, lon = point
    
    # Water features (sea, ocean, large lakes)
    water = None
    try:
        water_tags = {
            "natural": ["water", "coastline"],
            "waterway": ["riverbank"],
            "place": ["sea", "ocean"]
        }
        water = ox.features_from_point(point, tags=water_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch water features: {e}")
    
    # Harbors and ports
    harbors = None
    try:
        harbor_tags = {
            "harbour": "yes",
            "man_made": ["pier", "breakwater", "groyne"],
            "amenity": ["ferry_terminal", "port"]
        }
        harbors = ox.features_from_point(point, tags=harbor_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch harbor features: {e}")
    
    # Seamarks and navigation aids
    seamarks = None
    try:
        seamark_tags = {
            "seamark:type": True,  # Any seamark
            "man_made": ["lighthouse", "beacon"],
            "buoy": True
        }
        seamarks = ox.features_from_point(point, tags=seamark_tags, dist=dist)
        time.sleep(0.3)
    except Exception as e:
        logger.warning(f"Could not fetch seamark features: {e}")
    
    return (
        cast(GeoDataFrame, water) if water is not None else None,
        cast(GeoDataFrame, harbors) if harbors is not None else None,
        cast(GeoDataFrame, seamarks) if seamarks is not None else None
    )


def fetch_coastline(point, dist) -> GeoDataFrame | None:
    """Fetch coastline data for maritime maps."""
    try:
        coastline_tags = {"natural": "coastline"}
        coastline = ox.features_from_point(point, tags=coastline_tags, dist=dist)
        time.sleep(0.3)
        return cast(GeoDataFrame, coastline) if coastline is not None else None
    except Exception as e:
        logger.warning(f"Could not fetch coastline: {e}")
        return None
