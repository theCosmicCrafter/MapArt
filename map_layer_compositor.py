"""
Map Layer Compositor Module

Provides multi-layer map compositing capabilities for overlaying different
map types (city streets, railways, cycling routes, transit, maritime) with
various blending modes and opacity controls.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class BlendMode(Enum):
    """Blending modes for layer compositing."""

    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    HARD_LIGHT = "hard_light"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"
    HUE = "hue"
    SATURATION = "saturation"
    COLOR = "color"
    LUMINOSITY = "luminosity"


@dataclass
class MapLayer:
    """
    Represents a single map layer with rendering and compositing properties.

    Attributes:
        name: Unique identifier for the layer
        layer_type: Type of map data (city, railway, cycling, transit, maritime)
        opacity: Layer opacity (0.0 - 1.0)
        blend_mode: How this layer blends with layers below
        visible: Whether layer is currently visible
        z_index: Stack order (higher = on top)
        data: Cached map data (GeoDataFrames, graphs, etc.)
        render_func: Function to render this layer to an image
        theme_overrides: Optional theme color overrides for this layer
    """

    name: str
    layer_type: str  # 'city', 'railway', 'cycling', 'transit', 'maritime'
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    visible: bool = True
    z_index: int = 0
    data: Optional[dict] = field(default_factory=dict)
    render_func: Optional[Callable] = None
    theme_overrides: Optional[dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate layer configuration."""
        self.opacity = np.clip(self.opacity, 0.0, 1.0)


class LayerCompositor:
    """
    Manages multiple map layers and composites them into a final image.

    Supports:
    - Layer ordering (z-index)
    - Opacity/alpha blending
    - Multiple blend modes (multiply, overlay, screen, etc.)
    - Real-time preview compositing
    - Export to various formats
    """

    def __init__(self, width: int = 1200, height: int = 1600, dpi: int = 150):
        """
        Initialize the compositor.

        Args:
            width: Output image width in pixels
            height: Output image height in pixels
            dpi: Resolution for matplotlib rendering
        """
        self.width = width
        self.height = height
        self.dpi = dpi
        self.layers: list[MapLayer] = []
        self.background_color = (255, 255, 255)
        self.cache: dict[str, Image.Image] = {}

    def add_layer(
        self,
        name: str,
        layer_type: str,
        opacity: float = 1.0,
        blend_mode: BlendMode = BlendMode.NORMAL,
        z_index: Optional[int] = None,
        data: Optional[dict] = None,
        render_func: Optional[Callable] = None,
        theme_overrides: Optional[dict] = None,
    ) -> MapLayer:
        """
        Add a new layer to the composition.

        Args:
            name: Unique layer name
            layer_type: Type of map data
            opacity: Layer opacity (0.0 - 1.0)
            blend_mode: Blending mode
            z_index: Stack position (auto-assigned if None)
            data: Pre-fetched map data
            render_func: Custom render function
            theme_overrides: Theme color overrides

        Returns:
            The created MapLayer instance
        """
        if z_index is None:
            z_index = len(self.layers)

        layer = MapLayer(
            name=name,
            layer_type=layer_type,
            opacity=opacity,
            blend_mode=blend_mode,
            z_index=z_index,
            data=data or {},
            render_func=render_func,
            theme_overrides=theme_overrides or {},
        )

        self.layers.append(layer)
        self._sort_layers()
        self._invalidate_cache()

        return layer

    def remove_layer(self, name: str) -> bool:
        """Remove a layer by name. Returns True if found and removed."""
        for i, layer in enumerate(self.layers):
            if layer.name == name:
                del self.layers[i]
                self._invalidate_cache()
                return True
        return False

    def get_layer(self, name: str) -> Optional[MapLayer]:
        """Get a layer by name."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

    def move_layer(self, name: str, new_z_index: int):
        """Change a layer's position in the stack."""
        layer = self.get_layer(name)
        if layer:
            layer.z_index = new_z_index
            self._sort_layers()
            self._invalidate_cache()

    def set_layer_opacity(self, name: str, opacity: float):
        """Update layer opacity."""
        layer = self.get_layer(name)
        if layer:
            layer.opacity = np.clip(opacity, 0.0, 1.0)
            self.cache.pop(name, None)  # Invalidate this layer's cache

    def set_layer_blend_mode(self, name: str, blend_mode: BlendMode):
        """Update layer blend mode."""
        layer = self.get_layer(name)
        if layer:
            layer.blend_mode = blend_mode
            self._invalidate_cache()

    def toggle_layer_visibility(self, name: str) -> bool:
        """Toggle layer visibility. Returns new visibility state."""
        layer = self.get_layer(name)
        if layer:
            layer.visible = not layer.visible
            self._invalidate_cache()
            return layer.visible
        return False

    def _sort_layers(self):
        """Sort layers by z-index."""
        self.layers.sort(key=lambda layer: layer.z_index)

    def _invalidate_cache(self):
        """Clear all cached layer renders."""
        self.cache.clear()

    def _render_layer_to_image(self, layer: MapLayer) -> Image.Image:
        """
        Render a single layer to a PIL Image.

        This uses matplotlib to render the layer and converts to PIL.
        Custom render functions can be provided per-layer.
        """
        # Check cache first
        if layer.name in self.cache:
            return self.cache[layer.name]

        # Create figure for this layer
        fig, ax = plt.subplots(
            figsize=(self.width / self.dpi, self.height / self.dpi),
            dpi=self.dpi,
            facecolor="none",
        )
        ax.set_facecolor("none")
        ax.set_position((0, 0, 1, 1))
        ax.axis("off")

        # Use custom render function if provided
        if layer.render_func:
            layer.render_func(ax, layer.data)
        else:
            # Default render based on layer type
            self._default_layer_render(ax, layer)

        # Convert to PIL Image
        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=self.dpi,
            bbox_inches="tight",
            pad_inches=0,
            transparent=True,
            facecolor="none",
        )
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")

        # Ensure correct size
        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height), Image.LANCZOS)

        plt.close(fig)

        # Apply opacity
        if layer.opacity < 1.0:
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: int(p * layer.opacity))
            img.putalpha(alpha)

        # Cache and return
        self.cache[layer.name] = img
        return img

    def _default_layer_render(self, ax: Axes, layer: MapLayer):
        """Default rendering logic for each layer type."""
        # This will be expanded based on the existing map rendering logic
        # For now, it's a placeholder that draws a label
        ax.text(
            0.5,
            0.5,
            f"Layer: {layer.name}\nType: {layer.layer_type}",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=20,
            alpha=0.5,
        )

    def _blend_images(
        self, base: Image.Image, overlay: Image.Image, mode: BlendMode
    ) -> Image.Image:
        """
        Blend two images using the specified blend mode.

        Implements various Photoshop-style blending modes using PIL and numpy.
        """
        if mode == BlendMode.NORMAL:
            # Simple alpha composite
            return Image.alpha_composite(base, overlay)

        # Convert to numpy arrays for advanced blending
        base_arr = np.array(base).astype(float) / 255.0
        overlay_arr = np.array(overlay).astype(float) / 255.0

        # Extract channels
        base_rgb = base_arr[:, :, :3]
        overlay_rgb = overlay_arr[:, :, :3]
        base_alpha = base_arr[:, :, 3:4]
        overlay_alpha = overlay_arr[:, :, 3:4]

        # Calculate resulting alpha
        out_alpha = overlay_alpha + base_alpha * (1 - overlay_alpha)

        # Apply blend mode to RGB
        if mode == BlendMode.MULTIPLY:
            blended = base_rgb * overlay_rgb
        elif mode == BlendMode.SCREEN:
            blended = 1 - (1 - base_rgb) * (1 - overlay_rgb)
        elif mode == BlendMode.OVERLAY:
            blended = np.where(
                base_rgb < 0.5,
                2 * base_rgb * overlay_rgb,
                1 - 2 * (1 - base_rgb) * (1 - overlay_rgb),
            )
        elif mode == BlendMode.SOFT_LIGHT:
            blended = np.where(
                overlay_rgb < 0.5,
                2 * base_rgb * overlay_rgb + base_rgb**2 * (1 - 2 * overlay_rgb),
                2 * base_rgb * (1 - overlay_rgb)
                + np.sqrt(base_rgb) * (2 * overlay_rgb - 1),
            )
        elif mode == BlendMode.HARD_LIGHT:
            blended = np.where(
                overlay_rgb < 0.5,
                2 * base_rgb * overlay_rgb,
                1 - 2 * (1 - base_rgb) * (1 - overlay_rgb),
            )
        elif mode == BlendMode.COLOR_DODGE:
            blended = np.where(
                overlay_rgb >= 1, 1, np.minimum(1, base_rgb / (1 - overlay_rgb + 1e-10))
            )
        elif mode == BlendMode.COLOR_BURN:
            blended = np.where(
                overlay_rgb <= 0,
                0,
                1 - np.minimum(1, (1 - base_rgb) / (overlay_rgb + 1e-10)),
            )
        elif mode == BlendMode.DARKEN:
            blended = np.minimum(base_rgb, overlay_rgb)
        elif mode == BlendMode.LIGHTEN:
            blended = np.maximum(base_rgb, overlay_rgb)
        elif mode == BlendMode.DIFFERENCE:
            blended = np.abs(base_rgb - overlay_rgb)
        elif mode == BlendMode.EXCLUSION:
            blended = base_rgb + overlay_rgb - 2 * base_rgb * overlay_rgb
        elif mode == BlendMode.HUE:
            blended = self._blend_hsl(base_rgb, overlay_rgb, "hue")
        elif mode == BlendMode.SATURATION:
            blended = self._blend_hsl(base_rgb, overlay_rgb, "saturation")
        elif mode == BlendMode.COLOR:
            blended = self._blend_hsl(base_rgb, overlay_rgb, "color")
        elif mode == BlendMode.LUMINOSITY:
            blended = self._blend_hsl(base_rgb, overlay_rgb, "luminosity")
        else:
            blended = overlay_rgb

        # Composite with alpha
        final_rgb = (
            overlay_rgb * overlay_alpha + base_rgb * base_alpha * (1 - overlay_alpha)
        ) / np.maximum(out_alpha, 1e-10)

        # Use blended result where overlay has content
        mask = overlay_alpha > 0
        final_rgb = np.where(mask, blended, base_rgb)

        # Combine RGB with alpha
        result = np.concatenate([final_rgb, out_alpha], axis=2)
        result = np.clip(result * 255, 0, 255).astype(np.uint8)

        return Image.fromarray(result, "RGBA")

    def _blend_hsl(
        self, base: np.ndarray, overlay: np.ndarray, mode: str
    ) -> np.ndarray:
        """Helper for HSL-based blend modes."""
        from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

        base_hsv = rgb_to_hsv(base)
        overlay_hsv = rgb_to_hsv(overlay)

        if mode == "hue":
            result_hsv = overlay_hsv.copy()
            result_hsv[:, :, 1:] = base_hsv[:, :, 1:]
        elif mode == "saturation":
            result_hsv = base_hsv.copy()
            result_hsv[:, :, 1] = overlay_hsv[:, :, 1]
        elif mode == "color":
            result_hsv = overlay_hsv.copy()
            result_hsv[:, :, 2] = base_hsv[:, :, 2]
        elif mode == "luminosity":
            result_hsv = base_hsv.copy()
            result_hsv[:, :, 2] = overlay_hsv[:, :, 2]
        else:
            result_hsv = base_hsv

        return hsv_to_rgb(result_hsv)

    def composite(self) -> Image.Image:
        """
        Composite all visible layers into a final image.

        Returns:
            PIL Image with all layers blended together
        """
        # Start with background
        result = Image.new(
            "RGBA", (self.width, self.height), (*self.background_color, 255)
        )

        # Blend each visible layer
        for layer in self.layers:
            if not layer.visible:
                continue

            layer_img = self._render_layer_to_image(layer)
            result = self._blend_images(result, layer_img, layer.blend_mode)

        return result

    def export(
        self,
        filepath: str,
        format: str = "PNG",
        quality: int = 95,
        include_background: bool = True,
    ):
        """
        Export the composited image to a file.

        Args:
            filepath: Output file path
            format: Image format (PNG, JPEG, etc.)
            quality: JPEG quality (0-100)
            include_background: Whether to include background color
        """
        img = self.composite()

        if not include_background:
            # Remove background by making it transparent
            # This would need a background color key or mask
            pass

        if format.upper() == "JPEG":
            # Convert to RGB for JPEG
            rgb_img = Image.new("RGB", img.size, self.background_color)
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha as mask
            rgb_img.save(filepath, format=format, quality=quality)
        else:
            img.save(filepath, format=format, quality=quality)

    def get_preview(self, max_size: tuple[int, int] = (400, 533)) -> Image.Image:
        """
        Get a smaller preview of the composition for UI display.

        Args:
            max_size: Maximum (width, height) for preview

        Returns:
            Resized PIL Image
        """
        img = self.composite()
        img.thumbnail(max_size, Image.LANCZOS)
        return img

    def to_dict(self) -> dict:
        """Serialize layer configuration to dict."""
        return {
            "width": self.width,
            "height": self.height,
            "dpi": self.dpi,
            "background_color": self.background_color,
            "layers": [
                {
                    "name": layer.name,
                    "layer_type": layer.layer_type,
                    "opacity": layer.opacity,
                }
                for layer in self.layers
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LayerCompositor":
        """Create compositor from serialized configuration."""
        comp = cls(
            width=data.get("width", 1200),
            height=data.get("height", 1600),
            dpi=data.get("dpi", 150),
        )
        comp.background_color = tuple(data.get("background_color", (255, 255, 255)))

        for layer_data in data.get("layers", []):
            comp.add_layer(
                name=layer_data["name"],
                layer_type=layer_data["layer_type"],
                opacity=layer_data["opacity"],
                blend_mode=BlendMode(layer_data["blend_mode"]),
                z_index=layer_data["z_index"],
                theme_overrides=layer_data.get("theme_overrides", {}),
            )
            # Set visibility
            layer = comp.get_layer(layer_data["name"])
            if layer:
                layer.visible = layer_data["visible"]

        return comp


class LayerPreset:
    """Pre-configured layer combinations for common use cases."""

    @staticmethod
    def city_with_railways() -> list[dict]:
        """City streets base + railway overlay."""
        return [
            {
                "name": "city_base",
                "layer_type": "city",
                "opacity": 1.0,
                "blend_mode": BlendMode.NORMAL,
                "z_index": 0,
            },
            {
                "name": "railway_overlay",
                "layer_type": "railway",
                "opacity": 0.9,
                "blend_mode": BlendMode.MULTIPLY,
                "z_index": 1,
            },
        ]

    @staticmethod
    def cycling_city_highlights() -> list[dict]:
        """City base with cycling routes highlighted."""
        return [
            {
                "name": "city_base",
                "layer_type": "city",
                "opacity": 0.6,
                "blend_mode": BlendMode.NORMAL,
                "z_index": 0,
            },
            {
                "name": "cycling_overlay",
                "layer_type": "cycling",
                "opacity": 1.0,
                "blend_mode": BlendMode.SCREEN,
                "z_index": 1,
            },
        ]

    @staticmethod
    def transit_focus() -> list[dict]:
        """Transit routes over simplified city."""
        return [
            {
                "name": "city_base",
                "layer_type": "city",
                "opacity": 0.4,
                "blend_mode": BlendMode.MULTIPLY,
                "z_index": 0,
            },
            {
                "name": "transit_overlay",
                "layer_type": "transit",
                "opacity": 1.0,
                "blend_mode": BlendMode.NORMAL,
                "z_index": 1,
            },
        ]

    @staticmethod
    def maritime_coastal() -> list[dict]:
        """Coastal city with maritime details."""
        return [
            {
                "name": "city_base",
                "layer_type": "city",
                "opacity": 0.7,
                "blend_mode": BlendMode.NORMAL,
                "z_index": 0,
            },
            {
                "name": "maritime_overlay",
                "layer_type": "maritime",
                "opacity": 0.8,
                "blend_mode": BlendMode.OVERLAY,
                "z_index": 1,
            },
        ]


# Convenience function for quick compositing
def create_layered_map(
    layers_config: list[dict],
    width: int = 1200,
    height: int = 1600,
    output_path: Optional[str] = None,
) -> Image.Image:
    """
    Quick-create a layered map from a configuration.

    Args:
        layers_config: List of layer configuration dicts
        width: Output width
        height: Output height
        output_path: Optional path to save result

    Returns:
        Composited PIL Image
    """
    compositor = LayerCompositor(width=width, height=height)

    for config in layers_config:
        blend_mode = config.get("blend_mode", BlendMode.NORMAL)
        if isinstance(blend_mode, str):
            blend_mode = BlendMode(blend_mode)

        compositor.add_layer(
            name=config["name"],
            layer_type=config["layer_type"],
            opacity=config.get("opacity", 1.0),
            blend_mode=blend_mode,
            z_index=config.get("z_index"),
            theme_overrides=config.get("theme_overrides", {}),
        )

    result = compositor.composite()

    if output_path:
        result.save(output_path, quality=95)

    return result
