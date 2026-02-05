"""
Layered Map Integration Module

Integrates the map_layer_compositor with the existing create_map_poster.py rendering pipeline.
Provides concrete render functions for each map type using the existing fetching/plotting logic.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import matplotlib.pyplot as plt
import osmnx as ox
from matplotlib.axes import Axes
from shapely.geometry import Point

if TYPE_CHECKING:
    from map_layer_compositor import LayerCompositor, MapLayer

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import logging_config
from create_map_poster import (
    fetch_features,
    fetch_graph,
    get_crop_limits,
    get_edge_colors_by_type,
    get_edge_widths_by_type,
)

# Import map providers
try:
    from map_providers.cycling import fetch_cycling_routes
    from map_providers.railway import fetch_railways
except ImportError:
    fetch_cycling_routes = None
    fetch_railways = None

logger = logging_config.logger


def create_city_layer_renderer(
    point: Point,
    distance: float,
    theme: dict,
    fig_size: tuple[float, float],
):
    """
    Create a render function for city/street network layer.
    
    Args:
        point: Center point coordinates
        distance: Viewport distance in meters
        theme: Color theme dictionary
        fig_size: Figure size (width, height) in inches
        
    Returns:
        Render function for LayerCompositor
    """
    def render(ax: Axes, layer_data: dict):
        """Render city layer to axes."""
        # Fetch data if not cached
        if 'graph' not in layer_data:
            layer_data['graph'] = fetch_graph(point, distance)
            layer_data['water'] = fetch_features(
                point, distance,
                tags={"natural": "water", "waterway": "riverbank"},
                name="water"
            )
            layer_data['parks'] = fetch_features(
                point, distance,
                tags={"leisure": "park", "landuse": "grass"},
                name="parks"
            )
        
        G = layer_data.get('graph')
        water = layer_data.get('water')
        parks = layer_data.get('parks')
        
        if G is None:
            ax.text(0.5, 0.5, 'No street data available',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Project graph
        G_proj = ox.project_graph(G)
        
        # Plot water
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                try:
                    water_polys = ox.projection.project_gdf(water_polys)
                except Exception:
                    water_polys = water_polys.to_crs(G_proj.graph["crs"])
                water_polys.plot(
                    ax=ax, facecolor=theme.get("water", "#A8D5F0"),
                    edgecolor="none", zorder=1
                )
        
        # Plot parks
        if parks is not None and not parks.empty:
            parks_polys = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not parks_polys.empty:
                try:
                    parks_polys = ox.projection.project_gdf(parks_polys)
                except Exception:
                    parks_polys = parks_polys.to_crs(G_proj.graph["crs"])
                parks_polys.plot(
                    ax=ax, facecolor=theme.get("parks", "#C8E6C9"),
                    edgecolor="none", zorder=2
                )
        
        # Plot roads
        edge_colors = get_edge_colors_by_type(G_proj)
        edge_widths = get_edge_widths_by_type(G_proj)
        
        ox.plot_graph(
            G_proj,
            ax=ax,
            bgcolor=theme.get("bg", "#FFFFFF"),
            node_size=0,
            edge_color=edge_colors,
            edge_linewidth=edge_widths,
            show=False,
            close=False,
        )
    
    return render


def create_railway_layer_renderer(
    point: Point,
    distance: float,
    theme: dict,
    include_roads: bool = True,
):
    """
    Create a render function for railway layer.
    
    Args:
        point: Center point coordinates
        distance: Viewport distance in meters
        theme: Color theme dictionary
        include_roads: Whether to include light road background
        
    Returns:
        Render function for LayerCompositor
    """
    def render(ax: Axes, layer_data: dict):
        """Render railway layer to axes."""
        if fetch_railways is None:
            ax.text(0.5, 0.5, 'Railway provider not available',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Fetch data if not cached
        if 'railways' not in layer_data:
            layer_data['railways'] = fetch_railways(point, distance)
            if include_roads:
                layer_data['graph'] = fetch_graph(point, distance)
            layer_data['water'] = fetch_features(
                point, distance,
                tags={"natural": "water", "waterway": "riverbank"},
                name="water"
            )
        
        railways = layer_data.get('railways')
        G = layer_data.get('graph')
        water = layer_data.get('water')
        
        # Plot water for context
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                water_polys.plot(
                    ax=ax, facecolor=theme.get("water", "#A8D5F0"),
                    edgecolor="none", zorder=1
                )
        
        # Light road background
        if include_roads and G is not None:
            G_proj = ox.project_graph(G)
            ox.plot_graph(
                G_proj,
                ax=ax,
                bgcolor=theme.get("bg", "#FFFFFF"),
                node_size=0,
                edge_color="#DDDDDD",
                edge_linewidth=0.3,
                show=False,
                close=False,
            )
        
        # Plot railways prominently
        if railways is not None and not railways.empty:
            railway_lines = railways[railways.geometry.type.isin(["LineString", "MultiLineString"])]
            if not railway_lines.empty:
                railway_color = theme.get("railway", "#8B4513")
                railway_lines.plot(
                    ax=ax,
                    color=railway_color,
                    linewidth=2.5,
                    zorder=5,
                )
                
                # Add railway stations if available
                if 'railway' in railways.columns:
                    stations = railways[railways['railway'] == 'station']
                    if not stations.empty:
                        stations.plot(
                            ax=ax,
                            color=railway_color,
                            markersize=50,
                            zorder=6,
                        )
    
    return render


def create_cycling_layer_renderer(
    point: Point,
    distance: float,
    theme: dict,
    include_roads: bool = True,
):
    """
    Create a render function for cycling routes layer.
    
    Args:
        point: Center point coordinates
        distance: Viewport distance in meters
        theme: Color theme dictionary
        include_roads: Whether to include light road background
        
    Returns:
        Render function for LayerCompositor
    """
    def render(ax: Axes, layer_data: dict):
        """Render cycling layer to axes."""
        if fetch_cycling_routes is None:
            ax.text(0.5, 0.5, 'Cycling provider not available',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Fetch data if not cached
        if 'cycle_routes' not in layer_data:
            cycle_routes, cycleways = fetch_cycling_routes(point, distance)
            layer_data['cycle_routes'] = cycle_routes
            layer_data['cycleways'] = cycleways
            if include_roads:
                layer_data['graph'] = fetch_graph(point, distance)
            layer_data['water'] = fetch_features(
                point, distance,
                tags={"natural": "water", "waterway": "riverbank"},
                name="water"
            )
        
        cycle_routes = layer_data.get('cycle_routes')
        cycleways = layer_data.get('cycleways')
        G = layer_data.get('graph')
        water = layer_data.get('water')
        
        # Plot water for context
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                water_polys.plot(
                    ax=ax, facecolor=theme.get("water", "#A8D5F0"),
                    edgecolor="none", zorder=1
                )
        
        # Light road background
        if include_roads and G is not None:
            G_proj = ox.project_graph(G)
            ox.plot_graph(
                G_proj,
                ax=ax,
                bgcolor=theme.get("bg", "#FFFFFF"),
                node_size=0,
                edge_color="#E0E0E0",
                edge_linewidth=0.3,
                show=False,
                close=False,
            )
        
        # Plot cycleways (dedicated bike paths)
        if cycleways is not None and not cycleways.empty:
            cycleway_lines = cycleways[cycleways.geometry.type.isin(["LineString", "MultiLineString"])]
            if not cycleway_lines.empty:
                cycleway_lines.plot(
                    ax=ax,
                    color=theme.get("cycleway", "#4CAF50"),
                    linewidth=2.0,
                    zorder=4,
                )
        
        # Plot cycle routes (marked bike routes on roads)
        if cycle_routes is not None and not cycle_routes.empty:
            route_lines = cycle_routes[cycle_routes.geometry.type.isin(["LineString", "MultiLineString"])]
            if not route_lines.empty:
                route_lines.plot(
                    ax=ax,
                    color=theme.get("cycle_route", "#FF9800"),
                    linewidth=2.5,
                    linestyle='--',
                    zorder=5,
                )
    
    return render


def create_transit_layer_renderer(
    point: Point,
    distance: float,
    theme: dict,
    include_roads: bool = True,
):
    """
    Create a render function for public transit layer.
    
    Args:
        point: Center point coordinates
        distance: Viewport distance in meters
        theme: Color theme dictionary
        include_roads: Whether to include light road background
        
    Returns:
        Render function for LayerCompositor
    """
    def render(ax: Axes, layer_data: dict):
        """Render transit layer to axes."""
        # Fetch data if not cached
        if 'transit' not in layer_data:
            # Use existing fetch_transit if available
            from create_map_poster import fetch_transit
            layer_data['transit'] = fetch_transit(point, distance)
            if include_roads:
                layer_data['graph'] = fetch_graph(point, distance)
            layer_data['water'] = fetch_features(
                point, distance,
                tags={"natural": "water", "waterway": "riverbank"},
                name="water"
            )
        
        transit = layer_data.get('transit')
        G = layer_data.get('graph')
        water = layer_data.get('water')
        
        # Plot water for context
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                water_polys.plot(
                    ax=ax, facecolor=theme.get("water", "#A8D5F0"),
                    edgecolor="none", zorder=1
                )
        
        # Light road background
        if include_roads and G is not None:
            G_proj = ox.project_graph(G)
            ox.plot_graph(
                G_proj,
                ax=ax,
                bgcolor=theme.get("bg", "#FFFFFF"),
                node_size=0,
                edge_color="#E8E8E8",
                edge_linewidth=0.3,
                show=False,
                close=False,
            )
        
        # Plot transit lines
        if transit is not None and not transit.empty:
            transit_lines = transit[transit.geometry.type.isin(["LineString", "MultiLineString"])]
            if not transit_lines.empty:
                # Color by transit type if available
                if 'route_type' in transit_lines.columns:
                    # Define colors for different transit types
                    type_colors = {
                        'subway': theme.get("transit_subway", "#E91E63"),
                        'tram': theme.get("transit_tram", "#2196F3"),
                        'bus': theme.get("transit_bus", "#FF5722"),
                        'train': theme.get("transit_train", "#9C27B0"),
                    }
                    for route_type, color in type_colors.items():
                        lines = transit_lines[transit_lines['route_type'] == route_type]
                        if not lines.empty:
                            lines.plot(
                                ax=ax,
                                color=color,
                                linewidth=3.0,
                                zorder=5,
                            )
                else:
                    # Single color for all transit
                    transit_lines.plot(
                        ax=ax,
                        color=theme.get("transit", "#E91E63"),
                        linewidth=3.0,
                        zorder=5,
                    )
            
            # Plot transit stops
            stops = transit[transit.geometry.type == 'Point']
            if not stops.empty:
                stops.plot(
                    ax=ax,
                    color=theme.get("transit_stop", "#FFFFFF"),
                    edgecolor=theme.get("transit", "#E91E63"),
                    markersize=30,
                    zorder=6,
                )
    
    return render


def create_maritime_layer_renderer(
    point: Point,
    distance: float,
    theme: dict,
    include_coastline: bool = True,
):
    """
    Create a render function for maritime/coastal layer.
    
    Args:
        point: Center point coordinates
        distance: Viewport distance in meters
        theme: Color theme dictionary
        include_coastline: Whether to emphasize coastline
        
    Returns:
        Render function for LayerCompositor
    """
    def render(ax: Axes, layer_data: dict):
        """Render maritime layer to axes."""
        # Fetch data if not cached
        if 'water' not in layer_data:
            layer_data['water'] = fetch_features(
                point, distance,
                tags={"natural": "water", "waterway": "riverbank", "place": "sea"},
                name="water"
            )
            if include_coastline:
                layer_data['coastline'] = fetch_features(
                    point, distance,
                    tags={"natural": "coastline"},
                    name="coastline"
                )
            layer_data['graph'] = fetch_graph(point, distance)
        
        water = layer_data.get('water')
        coastline = layer_data.get('coastline')
        G = layer_data.get('graph')
        
        # Plot water areas
        if water is not None and not water.empty:
            water_polys = water[water.geometry.type.isin(["Polygon", "MultiPolygon"])]
            if not water_polys.empty:
                water_polys.plot(
                    ax=ax,
                    facecolor=theme.get("water", "#4A90E2"),
                    edgecolor=theme.get("water_edge", "#2E5C8A"),
                    linewidth=1.0,
                    zorder=1,
                )
        
        # Plot coastline prominently
        if coastline is not None and not coastline.empty:
            coastline_lines = coastline[coastline.geometry.type.isin(["LineString", "MultiLineString"])]
            if not coastline_lines.empty:
                coastline_lines.plot(
                    ax=ax,
                    color=theme.get("coastline", "#1A5276"),
                    linewidth=3.0,
                    zorder=4,
                )
        
        # Plot city streets (for coastal cities)
        if G is not None:
            G_proj = ox.project_graph(G)
            # Use lighter colors for land features
            ox.plot_graph(
                G_proj,
                ax=ax,
                bgcolor=theme.get("bg", "#F5F5F5"),
                node_size=0,
                edge_color=theme.get("street_light", "#D0D0D0"),
                edge_linewidth=0.4,
                show=False,
                close=False,
            )
    
    return render


def build_layered_composition(
    city: str,
    country: str,
    point: Point,
    distance: float,
    width: int,
    height: int,
    layers_config: list[dict],
    theme: dict,
    output_file: Optional[str] = None,
) -> 'LayerCompositor':
    """
    Build a layered map composition with multiple overlay types.
    
    Args:
        city: City name
        country: Country name
        point: Center point coordinates
        distance: Viewport distance in meters
        width: Output width in inches
        height: Output height in inches
        layers_config: List of layer configuration dicts
        theme: Color theme dictionary
        output_file: Optional output file path
        
    Returns:
        Configured LayerCompositor instance
    """
    from map_layer_compositor import LayerCompositor, BlendMode
    
    # Calculate DPI based on typical poster resolution
    dpi = 150
    pixel_width = int(width * dpi)
    pixel_height = int(height * dpi)
    
    compositor = LayerCompositor(
        width=pixel_width,
        height=pixel_height,
        dpi=dpi
    )
    
    # Map layer types to their render function creators
    render_creators = {
        'city': lambda: create_city_layer_renderer(point, distance, theme, (width, height)),
        'railway': lambda: create_railway_layer_renderer(point, distance, theme),
        'cycling': lambda: create_cycling_layer_renderer(point, distance, theme),
        'transit': lambda: create_transit_layer_renderer(point, distance, theme),
        'maritime': lambda: create_maritime_layer_renderer(point, distance, theme),
    }
    
    # Add each layer
    for config in layers_config:
        layer_type = config['layer_type']
        
        if layer_type not in render_creators:
            logger.warning(f"Unknown layer type: {layer_type}")
            continue
        
        # Create render function
        render_func = render_creators[layer_type]()
        
        # Parse blend mode
        blend_mode = config.get('blend_mode', BlendMode.NORMAL)
        if isinstance(blend_mode, str):
            blend_mode = BlendMode(blend_mode)
        
        # Add layer to compositor
        layer = compositor.add_layer(
            name=config['name'],
            layer_type=layer_type,
            opacity=config.get('opacity', 1.0),
            blend_mode=blend_mode,
            z_index=config.get('z_index'),
            theme_overrides=config.get('theme_overrides', {}),
        )
        
        # Attach render function
        layer.render_func = render_func
    
    # Export if output file specified
    if output_file:
        compositor.export(output_file, quality=95)
        logger.info(f"Layered map exported to: {output_file}")
    
    return compositor


# Predefined layer combinations for common use cases
LAYER_PRESETS = {
    'city_railway_overlay': [
        {'name': 'city_base', 'layer_type': 'city', 'opacity': 1.0, 'blend_mode': 'normal', 'z_index': 0},
        {'name': 'railway_overlay', 'layer_type': 'railway', 'opacity': 0.9, 'blend_mode': 'multiply', 'z_index': 1},
    ],
    'cycling_highlight': [
        {'name': 'city_faded', 'layer_type': 'city', 'opacity': 0.5, 'blend_mode': 'normal', 'z_index': 0},
        {'name': 'cycling_highlight', 'layer_type': 'cycling', 'opacity': 1.0, 'blend_mode': 'screen', 'z_index': 1},
    ],
    'transit_focus': [
        {'name': 'city_subtle', 'layer_type': 'city', 'opacity': 0.3, 'blend_mode': 'multiply', 'z_index': 0},
        {'name': 'transit_lines', 'layer_type': 'transit', 'opacity': 1.0, 'blend_mode': 'normal', 'z_index': 1},
    ],
    'coastal_city': [
        {'name': 'city_land', 'layer_type': 'city', 'opacity': 0.7, 'blend_mode': 'normal', 'z_index': 0},
        {'name': 'maritime_water', 'layer_type': 'maritime', 'opacity': 0.8, 'blend_mode': 'overlay', 'z_index': 1},
    ],
    'triple_transit': [
        {'name': 'city_base', 'layer_type': 'city', 'opacity': 0.4, 'blend_mode': 'normal', 'z_index': 0},
        {'name': 'railway_layer', 'layer_type': 'railway', 'opacity': 0.7, 'blend_mode': 'multiply', 'z_index': 1},
        {'name': 'transit_layer', 'layer_type': 'transit', 'opacity': 0.9, 'blend_mode': 'screen', 'z_index': 2},
    ],
}


def create_preset_layered_map(
    preset_name: str,
    city: str,
    country: str,
    point: Point,
    distance: float,
    width: int = 12,
    height: int = 16,
    theme: Optional[dict] = None,
    output_file: Optional[str] = None,
):
    """
    Create a layered map using a predefined preset.
    
    Args:
        preset_name: Name of preset from LAYER_PRESETS
        city: City name
        country: Country name
        point: Center point coordinates
        distance: Viewport distance in meters
        width: Output width in inches
        height: Output height in inches
        theme: Optional color theme (uses default if None)
        output_file: Optional output file path
        
    Returns:
        LayerCompositor instance
    """
    if preset_name not in LAYER_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(LAYER_PRESETS.keys())}")
    
    if theme is None:
        # Use default theme
        theme = {
            'bg': '#FFFFFF',
            'water': '#A8D5F0',
            'parks': '#C8E6C9',
            'railway': '#8B4513',
            'cycleway': '#4CAF50',
            'cycle_route': '#FF9800',
            'transit': '#E91E63',
            'transit_subway': '#E91E63',
            'transit_tram': '#2196F3',
            'transit_bus': '#FF5722',
            'transit_train': '#9C27B0',
            'transit_stop': '#FFFFFF',
            'coastline': '#1A5276',
            'street_light': '#D0D0D0',
        }
    
    layers_config = LAYER_PRESETS[preset_name]
    
    return build_layered_composition(
        city=city,
        country=country,
        point=point,
        distance=distance,
        width=width,
        height=height,
        layers_config=layers_config,
        theme=theme,
        output_file=output_file,
    )
