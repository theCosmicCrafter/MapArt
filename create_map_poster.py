import argparse
import asyncio
import json
import logging_config
import os
import pickle
import sys
import time
from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import cast

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import numpy as np
import osmnx as ox
from geopy.geocoders import Nominatim
from matplotlib.font_manager import FontProperties
from networkx import MultiDiGraph
from shapely.geometry import Point
from tqdm import tqdm

try:
    from geopandas import GeoDataFrame
except ImportError:
    GeoDataFrame = None

logger = logging_config.logger


class CacheError(Exception):
    """Raised when a cache operation fails."""

    pass


CACHE_DIR_PATH = os.environ.get("CACHE_DIR", ".cache")
CACHE_DIR = Path(CACHE_DIR_PATH)
CACHE_DIR.mkdir(exist_ok=True)


THEMES_DIR = "themes"
FONTS_DIR = "assets/fonts"
POSTERS_DIR = "outputs"


def _cache_path(key: str) -> str:
    safe = key.replace(os.sep, "_")
    return os.path.join(CACHE_DIR, f"{safe}.pkl")


def cache_get(key: str):
    try:
        path = _cache_path(key)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise CacheError(f"Cache read failed: {e}")


def cache_set(key: str, value):
    try:
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        path = _cache_path(key)
        with open(path, "wb") as f:
            pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        raise CacheError(f"Cache write failed: {e}")


def load_fonts():
    """
    Load Roboto fonts from the fonts directory.
    Returns dict with font paths for different weights.
    """
    fonts = {
        "bold": os.path.join(FONTS_DIR, "Roboto-Bold.ttf"),
        "regular": os.path.join(FONTS_DIR, "Roboto-Regular.ttf"),
        "light": os.path.join(FONTS_DIR, "Roboto-Light.ttf"),
    }

    # Verify fonts exist
    for weight, path in fonts.items():
        if not os.path.exists(path):
            print(f"[!] Font not found: {path}")
            return None

    return fonts


FONTS = load_fonts()


def generate_output_filename(city, theme_name, output_format):
    """
    Generate unique output filename with city, theme, and datetime.
    """
    if not os.path.exists(POSTERS_DIR):
        os.makedirs(POSTERS_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(" ", "_")
    ext = output_format.lower()
    filename = f"{city_slug}_{theme_name}_{timestamp}.{ext}"
    return os.path.join(POSTERS_DIR, filename)


def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []

    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith(".json"):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes


def normalize_theme_colors(theme):
    """
    Normalize theme colors - convert arrays to single colors
    """
    # Handle colors that might be arrays
    color_keys = [
        "water",
        "parks",
        "bg",
        "text",
        "gradient_color",
        "road_motorway",
        "road_primary",
        "road_secondary",
        "road_tertiary",
        "road_residential",
        "road_default",
    ]

    for key in color_keys:
        if key in theme:
            value = theme[key]
            if isinstance(value, list) and len(value) > 0:
                # Take the first color from array
                theme[key] = value[0]
        elif "colors" in theme and key in theme["colors"]:
            value = theme["colors"][key]
            if isinstance(value, list) and len(value) > 0:
                # Take the first color from array
                theme[key] = value[0]
            else:
                theme[key] = value

    return theme


def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    logger.info(f"Loading theme: {theme_name}")
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")

    if not os.path.exists(theme_file):
        print(
            f"[!] Theme file '{theme_file}' not found. Using default feature_based theme."
        )
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
            "bg": "#FFFFFF",
            "text": "#000000",
            "gradient_color": "#FFFFFF",
            "water": "#C0C0C0",
            "parks": "#F0F0F0",
            "road_motorway": "#0A0A0A",
            "road_primary": "#1A1A1A",
            "road_secondary": "#2A2A2A",
            "road_tertiary": "#3A3A3A",
            "road_residential": "#4A4A4A",
            "road_default": "#3A3A3A",
        }

    with open(theme_file, "r", encoding="utf-8") as f:
        theme = json.load(f)
        theme = normalize_theme_colors(theme)
        print(f"[+] Loaded theme: {theme.get('name', theme_name)}")
        if "description" in theme:
            print(f"  {theme['description']}")
        return theme


# Load theme (can be changed via command line or input)
THEME = dict[str, str]()  # Will be loaded later


def create_gradient_fade(ax, color, location="bottom", zorder=10):
    """
    Creates a fade effect at the top or bottom of the map.
    """
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))

    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]

    if location == "bottom":
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]

    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end

    ax.imshow(
        gradient,
        extent=[xlim[0], xlim[1], y_bottom, y_top],
        aspect="auto",
        cmap=custom_cmap,
        zorder=zorder,
        origin="lower",
    )


def get_edge_colors_by_type(G):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    """
    edge_colors = []

    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get("highway", "unclassified")

        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"

        # Assign color based on road type
        if highway in ["motorway", "motorway_link"]:
            color = THEME["road_motorway"]
        elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            color = THEME["road_primary"]
        elif highway in ["secondary", "secondary_link"]:
            color = THEME["road_secondary"]
        elif highway in ["tertiary", "tertiary_link"]:
            color = THEME["road_tertiary"]
        elif highway in ["residential", "living_street", "unclassified"]:
            color = THEME["road_residential"]
        else:
            color = THEME["road_default"]

        edge_colors.append(color)

    return edge_colors


def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []

    for u, v, data in G.edges(data=True):
        highway = data.get("highway", "unclassified")

        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"

        # Assign width based on road importance
        if highway in ["motorway", "motorway_link"]:
            width = 1.2
        elif highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            width = 1.0
        elif highway in ["secondary", "secondary_link"]:
            width = 0.8
        elif highway in ["tertiary", "tertiary_link"]:
            width = 0.6
        else:
            width = 0.4

        edge_widths.append(width)

    return edge_widths


def get_coordinates(city, country, max_retries=3):
    """
    Fetches coordinates for a given city and country using geopy.
    Implements proper rate limiting and retry logic according to OSM API policy.
    Includes fallback coordinates for common US cities when API is unavailable.
    Returns: (latitude, longitude, display_city)
    """
    # Default country to USA if not provided
    if not country:
        country = "USA"

    # Clean city name for geocoding but preserve original for display
    city_clean = city.split(",")[0].strip()
    display_city = city_clean  # Use this for the map label

    coords = f"coords_{city_clean.lower()}_{country.lower()}"
    cached = cache_get(coords)
    if cached:
        print(f"[*] Using cached coordinates for {city_clean}, {country}")
        # Return coordinates with the original city name for display
        return cached[0], cached[1], display_city

    print("Looking up coordinates...")

    # Fallback coordinates for common US cities when API is down
    fallback_coords = {
        "cary": (35.7915, -78.7811),  # Cary, NC
        "raleigh": (35.7796, -78.6382),  # Raleigh, NC
        "new york": (40.7128, -74.0060),  # New York, NY
        "los angeles": (34.0522, -118.2437),  # Los Angeles, CA
        "chicago": (41.8781, -87.6298),  # Chicago, IL
        "houston": (29.7604, -95.3698),  # Houston, TX
        "philadelphia": (39.9526, -75.1652),  # Philadelphia, PA
        "phoenix": (33.4484, -112.0740),  # Phoenix, AZ
        "san antonio": (29.4241, -98.4936),  # San Antonio, TX
        "san diego": (32.7157, -117.1611),  # San Diego, CA
        "dallas": (32.7767, -96.7970),  # Dallas, TX
        "san jose": (37.3382, -121.8863),  # San Jose, CA
        "austin": (30.2672, -97.7431),  # Austin, TX
        "jacksonville": (30.3322, -81.6557),  # Jacksonville, FL
        "fort worth": (32.7555, -97.3308),  # Fort Worth, TX
        "columbus": (39.9612, -82.9988),  # Columbus, OH
        "charlotte": (35.2271, -80.8431),  # Charlotte, NC
        "san francisco": (37.7749, -122.4194),  # San Francisco, CA
        "indianapolis": (39.7684, -86.1581),  # Indianapolis, IN
        "seattle": (47.6062, -122.3321),  # Seattle, WA
        "denver": (39.7392, -104.9903),  # Denver, CO
        "boston": (42.3601, -71.0589),  # Boston, MA
        "washington": (38.9072, -77.0369),  # Washington, DC
        "nashville": (36.1627, -86.7816),  # Nashville, TN
        "oklahoma city": (35.4676, -97.5164),  # Oklahoma City, OK
        "las vegas": (36.1699, -115.1398),  # Las Vegas, NV
        "detroit": (42.3314, -83.0458),  # Detroit, MI
        "portland": (45.5152, -122.6784),  # Portland, OR
        "memphis": (35.1495, -90.0490),  # Memphis, TN
        "louisville": (38.2527, -85.7585),  # Louisville, KY
        "milwaukee": (43.0389, -87.9065),  # Milwaukee, WI
        "baltimore": (39.2904, -76.6122),  # Baltimore, MD
        "albuquerque": (35.0844, -106.6504),  # Albuquerque, NM
        "tucson": (32.2226, -110.9747),  # Tucson, AZ
        "fresno": (36.7378, -119.7871),  # Fresno, CA
        "sacramento": (38.5816, -121.4944),  # Sacramento, CA
        "kansas city": (39.0997, -94.5786),  # Kansas City, MO
        "mesa": (33.4152, -111.8315),  # Mesa, AZ
        "atlanta": (33.7490, -84.3880),  # Atlanta, GA
        "omaha": (41.2565, -95.9345),  # Omaha, NE
        "colorado springs": (38.8339, -104.8214),  # Colorado Springs, CO
        "miami": (25.7617, -80.1918),  # Miami, FL
        "oakland": (37.8044, -122.2712),  # Oakland, CA
        "tulsa": (36.1540, -95.9940),  # Tulsa, OK
        "minneapolis": (44.9778, -93.2650),  # Minneapolis, MN
        "cleveland": (41.4993, -81.6944),  # Cleveland, OH
        "wichita": (37.6872, -97.3301),  # Wichita, KS
        "arlington": (32.7357, -97.1081),  # Arlington, TX
    }

    for attempt in range(max_retries):
        try:
            # Use proper user agent with contact info as required by Nominatim policy
            geolocator = Nominatim(
                user_agent="MapPosterGenerator/1.0 (educational use - map-poster@example.com)",
                timeout=15,  # Increased timeout
            )

            # Rate limiting: minimum 1 second between requests (OSM requirement)
            # Add exponential backoff for retries
            delay = max(1.0, 1.5 + (attempt * 1.0))  # Increased delays
            time.sleep(delay)

            location = geolocator.geocode(f"{city_clean}, {country}")

            # If geocode returned a coroutine in some environments, run it to get the result.
            if asyncio.iscoroutine(location):
                try:
                    location = asyncio.run(location)
                except RuntimeError as exc:
                    # If an event loop is already running, try using it to complete the coroutine.
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Running event loop in the same thread; raise a clear error.
                        raise RuntimeError(
                            "Geocoder returned a coroutine while an event loop is already running. Run this script in a synchronous environment."
                        ) from exc
                    location = loop.run_until_complete(location)

            if location:
                # Use getattr to safely access address (helps static analyzers)
                addr = getattr(location, "address", None)
                if addr:
                    print(f"[+] Found: {addr}")
                else:
                    print("[*] Found location (address not available)")
                print(f"[*] Coordinates: {location.latitude}, {location.longitude}")
                try:
                    cache_set(coords, (location.latitude, location.longitude))
                except Exception:
                    pass  # Cache failure is not critical
                return location.latitude, location.longitude, display_city
            else:
                if attempt < max_retries - 1:
                    print(
                        f"[*] No results found, retrying... (attempt {attempt + 2}/{max_retries})"
                    )
                    continue
                else:
                    raise ValueError(f"Location not found for {city}, {country}")

        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"[*] Geocoding failed, retrying... (attempt {attempt + 2}/{max_retries})"
                )
                print(f"    Error: {str(e)}")
                # Add extra delay for rate limit errors
                if "429" in str(e) or "rate limit" in str(e).lower():
                    time.sleep(5)
                continue
            else:
                # Final attempt failed - try fallback coordinates
                city_lower = city_clean.lower()
                if country.lower() == "usa" and city_lower in fallback_coords:
                    lat, lon = fallback_coords[city_lower]
                    print(
                        f"[*] API unavailable - using fallback coordinates for {city_clean}"
                    )
                    print(f"[*] Coordinates: {lat}, {lon}")
                    cache_set(coords, (lat, lon))
                    return lat, lon, display_city
                else:
                    raise ValueError(
                        f"Geocoding failed for {city_clean}, {country} after {max_retries} attempts: {e}"
                    )


def get_crop_limits(G_proj, center_lat_lon, fig, dist):
    """
    Crop inward to preserve aspect ratio while guaranteeing
    full coverage of the requested radius.
    """
    lat, lon = center_lat_lon

    # Project center point into graph CRS
    center = ox.projection.project_geometry(
        Point(lon, lat), crs="EPSG:4326", to_crs=G_proj.graph["crs"]
    )[0]
    center_x, center_y = center.x, center.y

    fig_width, fig_height = fig.get_size_inches()
    aspect = fig_width / fig_height

    # Start from the *requested* radius
    half_x = dist
    half_y = dist

    # Cut inward to match aspect
    if aspect > 1:  # landscape → reduce height
        half_y = half_x / aspect
    else:  # portrait → reduce width
        half_x = half_y * aspect

    return (
        (center_x - half_x, center_x + half_x),
        (center_y - half_y, center_y + half_y),
    )


def fetch_graph(point, dist) -> MultiDiGraph | None:
    lat, lon = point
    graph = f"graph_{lat}_{lon}_{dist}"
    cached = cache_get(graph)
    if cached is not None:
        print("[*] Using cached street network")
        return cast(MultiDiGraph, cached)

    try:
        G = ox.graph_from_point(
            point,
            dist=dist,
            dist_type="bbox",
            network_type="all",
            truncate_by_edge=True,
        )
        # Rate limit between requests
        time.sleep(0.5)
        try:
            cache_set(graph, G)
        except CacheError as e:
            print(e)
        return G
    except Exception as e:
        print(f"OSMnx error while fetching graph: {e}")
        return None


def fetch_features(point, dist, tags, name) -> GeoDataFrame | None:
    lat, lon = point
    tag_str = "_".join(tags.keys())
    features = f"{name}_{lat}_{lon}_{dist}_{tag_str}"
    cached = cache_get(features)
    if cached is not None:
        print(f"[*] Using cached {name}")
        return cast(GeoDataFrame, cached)

    try:
        data = ox.features_from_point(point, tags=tags, dist=dist)
        # Rate limit between requests
        time.sleep(0.3)
        try:
            cache_set(features, data)
        except CacheError as e:
            print(e)
        return data
    except Exception as e:
        print(f"OSMnx error while fetching features: {e}")
        return None


def generate_3d_terrain(width, height, output_file):
    """Generate a 3D terrain visualization"""
    print("Generating 3D terrain map...")

    # Convert float dimensions to integers for array generation
    grid_width = int(width * 100)  # Convert inches to pixels at 100 dpi
    grid_height = int(height * 100)

    # Create synthetic elevation data
    x = np.linspace(-5, 5, grid_width)
    y = np.linspace(-5, 5, grid_height)
    X, Y = np.meshgrid(x, y)

    # Generate terrain with multiple peaks
    Z = (
        np.sin(X) * np.cos(Y)
        + 0.5 * np.sin(2 * X + 1) * np.cos(2 * Y)
        + 0.3 * np.sin(3 * X) * np.cos(3 * Y + 2)
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(width / 2, height / 2), dpi=100)
    ax.set_aspect("equal")

    # Hill shading
    ls = LightSource(azdeg=315, altdeg=45)
    rgb = ls.shade(Z, cmap=plt.cm.terrain, vert_exag=0.1, blend_mode="soft")

    ax.imshow(rgb, extent=[-5, 5, -5, 5])

    # Add contour lines
    ax.contour(X, Y, Z, levels=15, colors="black", alpha=0.3, linewidths=0.5)

    ax.set_title("3D Terrain Visualization", fontsize=20, pad=20)
    ax.set_xlabel("Longitude", fontsize=14)
    ax.set_ylabel("Latitude", fontsize=14)

    # Remove ticks but keep clean look
    ax.set_xticks([])
    ax.set_yticks([])

    # Add subtle grid
    ax.grid(True, alpha=0.1, linestyle="-", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"[+] 3D terrain map saved to {output_file}")


def apply_shape_to_image(image_path, shape):
    """Apply shape mask to an image while maintaining overall dimensions"""
    try:
        from PIL import Image as PILImage, ImageDraw

        # Open the image
        img = PILImage.open(image_path).convert("RGBA")
        width, height = img.size

        if shape == "circle":
            # Create circular mask that fits the smaller dimension
            # This ensures the circle is as large as possible while fitting in the rectangle
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2

            # Create white background for the areas outside the circle
            background = PILImage.new("RGBA", (width, height), (255, 255, 255, 255))

            # Create circular mask
            mask_img = PILImage.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask_img)
            mask_draw.ellipse(
                [
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                ],
                fill=255,
            )

            # Apply mask to original image
            img.putalpha(mask_img)

            # Composite onto white background
            result = PILImage.alpha_composite(background, img)
            result = result.convert("RGB")

        elif shape == "triangle":
            # Create equilateral triangle that maximizes use of canvas
            # Calculate triangle points to fill the canvas as much as possible
            margin = int(min(width, height) * 0.05)  # 5% margin

            points = [
                (width // 2, margin),  # Top point (centered, near top)
                (margin, height - margin),  # Bottom left
                (width - margin, height - margin),  # Bottom right
            ]

            # Create white background
            background = PILImage.new("RGBA", (width, height), (255, 255, 255, 255))

            # Create triangular mask
            mask_img = PILImage.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask_img)
            mask_draw.polygon(points, fill=255)

            # Apply mask to original image
            img.putalpha(mask_img)

            # Composite onto white background
            result = PILImage.alpha_composite(background, img)
            result = result.convert("RGB")

        else:
            # Rectangle or unknown shape - no changes
            result = img.convert("RGB")

        # Save the result (maintaining original dimensions)
        result.save(image_path, quality=95)
        print(
            f"[+] Shape '{shape}' applied successfully (dimensions: {width}x{height})"
        )

    except Exception as e:
        print(f"[!] Failed to apply shape: {e}")


def apply_texture_to_image(image_path, texture):
    """Apply texture to an existing image file"""
    try:
        from PIL import Image as PILImage, ImageEnhance

        # Open the image
        base_image = PILImage.open(image_path).convert("RGB")

        # Load texture
        texture_path = os.path.join("assets", "textures", f"{texture}")
        if os.path.exists(texture_path):
            texture_img = PILImage.open(texture_path)
            texture_img = texture_img.resize(base_image.size)

            # Convert texture to RGB if needed
            if texture_img.mode != "RGB":
                texture_img = texture_img.convert("RGB")

            # Apply texture with proper blending
            base_array = np.array(base_image)
            texture_array = np.array(texture_img)

            # Normalize arrays to 0-1 range
            base_norm = base_array.astype(float) / 255.0
            texture_norm = texture_array.astype(float) / 255.0

            # Apply texture with 30% strength
            textured = base_norm * 0.7 + texture_norm * 0.3

            # Ensure values stay in valid range
            textured = np.clip(textured * 1.1, 0, 1)

            # Convert back to image
            textured_array = (textured * 255).astype(np.uint8)
            textured_image = PILImage.fromarray(textured_array)

            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(textured_image)
            textured_image = enhancer.enhance(1.1)

            # Save the result
            textured_image.save(image_path, quality=95)
            print(f"[+] Texture '{texture}' applied successfully")
    except Exception as e:
        print(f"[!] Failed to apply texture: {e}")


def create_poster(
    city,
    country,
    point,
    dist,
    output_file,
    output_format,
    width=12,
    height=16,
    country_label=None,
    name_label=None,
    font_family=None,
    texture="none",
    artistic_effect="none",
    color_enhancement="none",
    map_shape="rectangle",  # New parameter: rectangle, circle, triangle
):
    print("\n=== DEBUG: create_poster Parameters ===")
    print(f"City: {city}")
    print(f"Country: {country}")
    print(f"Distance: {dist}")
    print(f"Output File: {output_file}")
    print(f"Format: {output_format}")
    print(f"Width: {width}")
    print(f"Height: {height}")
    print(f"Font Family: {font_family}")
    print(f"Texture: {texture}")
    print(f"Artistic Effect: {artistic_effect}")
    print(f"Color Enhancement: {color_enhancement}")
    # Map Style: real (only option)
    print(f"Current Theme: {THEME.get('name', 'Unknown')}")
    print("====================================\n")

    # 3D terrain removed - was not properly implemented
    # Only real OpenStreetMap data is supported

    print("\nGenerating map for {city}, {country}...")

    # Progress bar for data fetching
    with tqdm(
        total=3,
        desc="Fetching map data",
        unit="step",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
    ) as pbar:
        # 1. Fetch Street Network
        pbar.set_description("Downloading street network")
        compensated_dist = (
            dist * (max(height, width) / min(height, width)) / 4
        )  # To compensate for viewport crop
        G = fetch_graph(point, compensated_dist)
        if G is None:
            raise RuntimeError("Failed to retrieve street network data.")
        pbar.update(1)

        # 2. Fetch Water Features
        pbar.set_description("Downloading water features")
        water = fetch_features(
            point,
            compensated_dist,
            tags={"natural": "water", "waterway": "riverbank"},
            name="water",
        )
        pbar.update(1)

        # 3. Fetch Parks
        pbar.set_description("Downloading parks/green spaces")
        parks = fetch_features(
            point,
            compensated_dist,
            tags={"leisure": "park", "landuse": "grass"},
            name="parks",
        )
        pbar.update(1)

    print("[*] All data retrieved successfully!")

    # 2. Setup Plot
    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(width, height), facecolor=THEME["bg"])
    ax.set_facecolor(THEME["bg"])
    ax.set_position((0.0, 0.0, 1.0, 1.0))

    # Project graph to a metric CRS so distances and aspect are linear (meters)
    G_proj = ox.project_graph(G)

    # 3. Plot Layers
    # Layer 1: Polygons (filter to only plot polygon/multipolygon geometries, not points)
    if water is not None and not water.empty:
        # Filter to only polygon/multipolygon geometries to avoid point features showing as dots
        water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not water_polys.empty:
            # Project water features in the same CRS as the graph
            try:
                water_polys = ox.projection.project_gdf(water_polys)
            except Exception:
                water_polys = water_polys.to_crs(G_proj.graph["crs"])
            water_polys.plot(
                ax=ax, facecolor=THEME["water"], edgecolor="none", zorder=1
            )

    if parks is not None and not parks.empty:
        # Filter to only polygon/multipolygon geometries to avoid point features showing as dots
        parks_polys = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not parks_polys.empty:
            # Project park features in the same CRS as the graph
            try:
                parks_polys = ox.projection.project_gdf(parks_polys)
            except Exception:
                parks_polys = parks_polys.to_crs(G_proj.graph["crs"])
            parks_polys.plot(
                ax=ax, facecolor=THEME["parks"], edgecolor="none", zorder=2
            )

    # Layer 2: Roads with hierarchy coloring
    print("Applying road hierarchy colors...")
    edge_colors = get_edge_colors_by_type(G_proj)
    edge_widths = get_edge_widths_by_type(G_proj)

    # Determine cropping limits to maintain the poster aspect ratio
    crop_xlim, crop_ylim = get_crop_limits(G_proj, point, fig, compensated_dist)
    # Plot the projected graph and then apply the cropped limits
    ox.plot_graph(
        G_proj,
        ax=ax,
        bgcolor=THEME["bg"],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False,
        close=False,
    )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(crop_xlim)
    ax.set_ylim(crop_ylim)

    # Layer 3: Gradients (Top and Bottom)
    create_gradient_fade(ax, THEME["gradient_color"], location="bottom", zorder=10)
    create_gradient_fade(ax, THEME["gradient_color"], location="top", zorder=10)

    # Calculate scale factor based on poster width (reference width 12 inches)
    scale_factor = width / 12.0

    # Base font sizes (at 12 inches width)
    BASE_MAIN = 60
    BASE_TOP = 40
    BASE_SUB = 22
    BASE_COORDS = 14
    BASE_ATTR = 8

    # 4. Typography using Roboto font
    if FONTS:
        font_main = FontProperties(fname=FONTS["bold"], size=BASE_MAIN * scale_factor)
        font_top = FontProperties(fname=FONTS["bold"], size=BASE_TOP * scale_factor)
        font_sub = FontProperties(fname=FONTS["light"], size=BASE_SUB * scale_factor)
        font_coords = FontProperties(
            fname=FONTS["regular"], size=BASE_COORDS * scale_factor
        )
        font_attr = FontProperties(fname=FONTS["light"], size=BASE_ATTR * scale_factor)
    else:
        # Fallback to system fonts
        font_main = FontProperties(
            family="monospace", weight="bold", size=BASE_MAIN * scale_factor
        )
        font_top = FontProperties(
            family="monospace", weight="bold", size=BASE_TOP * scale_factor
        )
        font_sub = FontProperties(
            family="monospace", weight="normal", size=BASE_SUB * scale_factor
        )
        font_coords = FontProperties(
            family="monospace", size=BASE_COORDS * scale_factor
        )
        font_attr = FontProperties(family="monospace", size=BASE_ATTR * scale_factor)

    spaced_city = "  ".join(list(city.upper()))

    # Dynamically adjust font size based on city name length to prevent truncation
    # We use the already scaled "main" font size as the starting point.
    base_adjusted_main = BASE_MAIN * scale_factor
    city_char_count = len(city)

    # Heuristic: If length is > 10, start reducing.
    if city_char_count > 10:
        length_factor = 10 / city_char_count
        adjusted_font_size = max(base_adjusted_main * length_factor, 10 * scale_factor)
    else:
        adjusted_font_size = base_adjusted_main

    if FONTS:
        font_main_adjusted = FontProperties(
            fname=FONTS["bold"], size=adjusted_font_size
        )
    else:
        font_main_adjusted = FontProperties(
            family="monospace", weight="bold", size=adjusted_font_size
        )

    # --- BOTTOM TEXT ---
    ax.text(
        0.5,
        0.14,
        spaced_city,
        transform=ax.transAxes,
        color=THEME["text"],
        ha="center",
        fontproperties=font_main_adjusted,
        zorder=11,
    )

    country_text = country_label if country_label is not None else country
    ax.text(
        0.5,
        0.10,
        country_text.upper(),
        transform=ax.transAxes,
        color=THEME["text"],
        ha="center",
        fontproperties=font_sub,
        zorder=11,
    )

    lat, lon = point
    coords = (
        f"{lat:.4f}° N / {lon:.4f}° E"
        if lat >= 0
        else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    )
    if lon < 0:
        coords = coords.replace("E", "W")

    ax.text(
        0.5,
        0.07,
        coords,
        transform=ax.transAxes,
        color=THEME["text"],
        alpha=0.7,
        ha="center",
        fontproperties=font_coords,
        zorder=11,
    )

    ax.plot(
        [0.4, 0.6],
        [0.125, 0.125],
        transform=ax.transAxes,
        color=THEME["text"],
        linewidth=1 * scale_factor,
        zorder=11,
    )

    # --- ATTRIBUTION (bottom right) ---
    # Attribution removed - logo/text hidden

    # 5. Save
    print(f"Saving to {output_file}...")

    fmt = output_format.lower()
    save_kwargs = dict(
        facecolor=THEME["bg"],
        bbox_inches="tight",
        pad_inches=0.05,
    )

    # DPI matters mainly for raster formats
    if fmt == "png":
        save_kwargs["dpi"] = 300

    plt.savefig(output_file, format=fmt, **save_kwargs)

    plt.close()

    # Apply texture if specified
    if texture != "none":
        print(f"Applying texture: {texture}")
        try:
            from PIL import Image as PILImage, ImageEnhance
            import json

            # Open the generated poster
            base_image = PILImage.open(output_file).convert("RGB")

            # Load texture manifest to find the correct path
            manifest_path = os.path.join("assets", "textures", "manifest.json")
            texture_found = False
            texture_path = None

            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                # Search for texture in all categories
                for category, data in manifest.get("categories", {}).items():
                    for tex in data.get("textures", []):
                        # Match by filename without extension
                        tex_name = os.path.splitext(tex["filename"])[0]
                        if tex_name == texture:
                            texture_path = os.path.join(
                                "assets", "textures", tex["path"]
                            )
                            texture_found = True
                            break
                    if texture_found:
                        break

            # Fallback: try common extensions if not found in manifest
            if not texture_found:
                for ext in [".jpg", ".png", ".jpeg"]:
                    for subdir in [
                        "base",
                        "specialty",
                        "artistic",
                        "edges",
                        "stains",
                        "",
                    ]:
                        test_path = os.path.join(
                            "assets", "textures", subdir, f"{texture}{ext}"
                        )
                        if os.path.exists(test_path):
                            texture_path = test_path
                            texture_found = True
                            break
                    if texture_found:
                        break

            if texture_path and os.path.exists(texture_path):
                print(f"[+] Loading texture from: {texture_path}")
                texture_img = PILImage.open(texture_path)
                texture_img = texture_img.resize(base_image.size)

                # Convert texture to RGB if needed
                if texture_img.mode != "RGB":
                    texture_img = texture_img.convert("RGB")

                # Apply texture with proper blending
                # Method 1: Multiply blend for subtle texture
                base_array = np.array(base_image)
                texture_array = np.array(texture_img)

                # Normalize arrays to 0-1 range
                base_norm = base_array.astype(float) / 255.0
                texture_norm = texture_array.astype(float) / 255.0

                # Apply texture with 30% strength
                textured = base_norm * 0.7 + texture_norm * 0.3

                # Ensure values stay in valid range
                textured = np.clip(textured * 1.1, 0, 1)  # Slight brightness boost

                # Convert back to image
                textured_array = (textured * 255).astype(np.uint8)
                textured_image = PILImage.fromarray(textured_array)

                # Enhance contrast slightly
                enhancer = ImageEnhance.Contrast(textured_image)
                textured_image = enhancer.enhance(1.1)

                # Save the result
                textured_image.save(output_file, quality=95)
                print(f"[+] Texture '{texture}' applied successfully")
            else:
                print(f"[!] Texture file not found: {texture_path}")
        except Exception as e:
            print(f"[!] Failed to apply texture: {e}")

    # Apply shape if specified
    if map_shape != "rectangle":
        print(f"Applying shape: {map_shape}")
        apply_shape_to_image(output_file, map_shape)

    # Apply color enhancement if specified
    if color_enhancement != "none":
        print(f"Applying color enhancement: {color_enhancement}")
        try:
            # Import color enhancement module
            import color_enhancement

            enhancer = color_enhancement.ColorEnhancer()
            enhancer.apply_enhancement(output_file, color_enhancement, city)
            print(f"[+] Color enhancement '{color_enhancement}' applied successfully")
        except Exception as e:
            print(f"[!] Failed to apply color enhancement: {e}")

    print(f"[+] Done! Poster saved as {output_file}")


def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]

Examples:
  # Iconic grid patterns
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district grid
  
  # Waterfront & canals
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
  python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
  python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline
  
  # Radial patterns
  python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
  python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads
  
  # Organic old cities
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
  python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
  python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient street layout
  
  # Coastal cities
  python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
  python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
  python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula
  
  # River cities
  python create_map_poster.py -c "London" -C "UK" -t noir -d 15000              # Thames curves
  python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split
  
  # List themes
  python create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --country-label   Override country text displayed on poster
  --theme, -t       Theme name (default: feature_based)
  --all-themes      Generate posters for all themes
  --distance, -d    Map radius in meters (default: 29000)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities (Venice, Amsterdam old center)
  8000-12000m  Medium cities, focused downtown (Paris, Barcelona)
  15000-20000m Large metros, full city view (Tokyo, Mumbai)

Available themes can be found in the 'themes/' directory.
Generated posters are saved to 'outputs/' directory.
""")


def list_themes():
    """List all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return

    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.json")
        try:
            with open(theme_path, "r") as f:
                theme_data = json.load(f)
                display_name = theme_data.get("name", theme_name)
                description = theme_data.get("description", "")
        except Exception:
            display_name = theme_name
            description = ""
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate beautiful map posters for any city",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_map_poster.py --city "New York" --country "USA"
  python create_map_poster.py --city Tokyo --country Japan --theme midnight_blue
  python create_map_poster.py --city Paris --country France --theme noir --distance 15000
  python create_map_poster.py --list-themes
        """,
    )

    parser.add_argument("--city", "-c", type=str, help="City name")
    parser.add_argument("--country", "-C", type=str, help="Country name")
    parser.add_argument(
        "--country-label",
        dest="country_label",
        type=str,
        help="Override country text displayed on poster",
    )
    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        default="feature_based",
        help="Theme name (default: feature_based)",
    )
    parser.add_argument(
        "--all-themes",
        "--All-themes",
        dest="all_themes",
        action="store_true",
        help="Generate posters for all themes",
    )
    parser.add_argument(
        "--distance",
        "-d",
        type=int,
        default=29000,
        help="Map radius in meters (default: 29000)",
    )
    parser.add_argument(
        "--width",
        "-W",
        type=float,
        default=12,
        help="Image width in inches (default: 12)",
    )
    parser.add_argument(
        "--height",
        "-H",
        type=float,
        default=16,
        help="Image height in inches (default: 16)",
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="List all available themes"
    )
    parser.add_argument(
        "--format",
        "-f",
        default="png",
        choices=["png", "jpg", "jpeg", "svg", "pdf"],
        help="Output format for the poster (default: png)",
    )
    parser.add_argument(
        "--font",
        default="Roboto",
        help="Font family for the poster (default: Roboto)",
    )
    parser.add_argument(
        "--texture",
        default="none",
        help="Paper texture to apply (default: none)",
    )
    parser.add_argument(
        "--artistic-effect",
        default="none",
        choices=["none", "watercolor", "pencil_sketch", "oil_painting", "vintage"],
        help="Artistic effect to apply (default: none)",
    )
    parser.add_argument(
        "--color-enhancement",
        default="none",
        choices=[
            "none",
            "intelligent_palette",
            "geographic_colors",
            "seasonal_summer",
            "seasonal_autumn",
            "seasonal_winter",
            "seasonal_spring",
        ],
        help="Color enhancement to apply (default: none)",
    )
    # --map-style removed: only real OpenStreetMap data supported
    parser.add_argument(
        "--map-shape",
        default="rectangle",
        choices=["rectangle", "circle", "triangle"],
        help="Map shape: rectangle, circle, or triangle",
    )
    parser.add_argument(
        "--state",
        "-s",
        type=str,
        help="State or province (optional)",
    )

    args = parser.parse_args()

    # If no arguments provided, show examples
    if len(sys.argv) == 1:
        print_examples()
        sys.exit(0)

    # List themes if requested
    if args.list_themes:
        list_themes()
        sys.exit(0)

    # Validate required arguments
    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        sys.exit(1)

    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        os.sys.exit(1)

    if args.all_themes:
        themes_to_generate = available_themes
    else:
        if args.theme not in available_themes:
            print(f"Error: Theme '{args.theme}' not found.")
            print(f"Available themes: {', '.join(available_themes)}")
            os.sys.exit(1)
        themes_to_generate = [args.theme]

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    # Debug: Print all received arguments
    print("\n=== DEBUG: Received Arguments ===")
    print(f"City: {args.city}")
    print(f"Country: {args.country}")
    print(f"Theme: {args.theme}")
    print(f"Distance: {args.distance}")
    print(f"Width: {args.width}")
    print(f"Height: {args.height}")
    print(f"Format: {args.format}")
    print(f"Font: {args.font}")
    print(f"Texture: {args.texture}")
    print(f"Artistic Effect: {args.artistic_effect}")
    print(f"Color Enhancement: {args.color_enhancement}")
    print("================================\n")

    # Get coordinates and generate poster
    try:
        coords = get_coordinates(args.city, args.country)
        # Unpack coordinates and display city
        if len(coords) == 3:
            lat, lon, display_city = coords
        else:
            lat, lon = coords[:2]  # Take first two values in case it's a tuple
            display_city = args.city.split(",")[0].strip()
        for theme_name in themes_to_generate:
            THEME = load_theme(theme_name)
            output_file = generate_output_filename(args.city, theme_name, args.format)
            create_poster(
                display_city,  # Use display city for the label
                args.country,
                (lat, lon),  # Pass only coordinates
                args.distance,
                output_file,
                args.format,
                args.width,
                args.height,
                country_label=args.country_label,
                font_family=args.font,
                texture=args.texture,
                artistic_effect=args.artistic_effect,
                color_enhancement=args.color_enhancement,
                map_shape=getattr(args, "map_shape", "rectangle"),
            )

        print("\n" + "=" * 50)
        print("[*] Poster generation complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
