"""
Color Enhancement Module for Artistic Map Generation
Provides intelligent color palettes, artistic effects, and geographic color awareness
"""

import requests
import numpy as np
from PIL import Image
import cv2
import colorsys
from typing import List, Dict, Tuple


class ColorPaletteAPI:
    """Integration with Colormind API for intelligent palette generation"""

    def __init__(self):
        self.api_url = "http://colormind.io/api/"
        self.cache = {}

    def get_palette(
        self, input_colors: List[str] = None, model: str = "default"
    ) -> List[str]:
        """Generate color palette from Colormind API"""
        cache_key = f"{str(input_colors)}_{model}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            payload = {"model": model}
            if input_colors:
                payload["input"] = input_colors

            response = requests.post(self.api_url, json=payload, timeout=5)

            if response.status_code == 200:
                palette = response.json().get("result", [])
                # Convert RGB to hex
                hex_palette = []
                for color in palette:
                    if isinstance(color, list) and len(color) == 3:
                        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                        hex_palette.append(hex_color)

                self.cache[cache_key] = hex_palette
                return hex_palette

        except Exception as e:
            print(f"Warning: Could not fetch palette from API: {e}")
            return self._fallback_palette(input_colors)

        return self._fallback_palette(input_colors)

    def _fallback_palette(self, input_colors: List[str] = None) -> List[str]:
        """Fallback palette generation using color theory"""
        if not input_colors:
            return ["#4682B4", "#F5F5DC", "#228B22", "#8B7355", "#2F4F4F"]

        # Generate complementary colors
        base_color = input_colors[0]
        return self._generate_harmonious_colors(base_color)

    def _generate_harmonious_colors(self, base_hex: str) -> List[str]:
        """Generate harmonious colors using color theory"""
        rgb = tuple(int(base_hex[i : i + 2], 16) for i in (1, 3, 5))
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

        colors = [base_hex]

        # Generate complementary, triadic, and analogous colors
        harmonies = [
            (h + 0.5) % 1.0,  # Complementary
            (h + 0.33) % 1.0,  # Triadic 1
            (h + 0.67) % 1.0,  # Triadic 2
            (h + 0.083) % 1.0,  # Analogous 1
            (h - 0.083) % 1.0,  # Analogous 2
        ]

        for h_new in harmonies[:4]:  # Take 4 additional colors
            r, g, b = colorsys.hsv_to_rgb(h_new, s * 0.8, v)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(r * 255), int(g * 255), int(b * 255)
            )
            colors.append(hex_color)

        return colors


class GeographicColorRules:
    """Geographic-specific color rules and seasonal variations"""

    def __init__(self):
        self.geographic_palettes = {
            "mountain": {
                "base": ["#8B7355", "#90EE90", "#FFFFFF"],
                "elevation": {
                    "low": "#90EE90",
                    "mid": "#8B7355",
                    "high": "#D3D3D3",
                    "peak": "#FFFFFF",
                },
                "vegetation": ["#228B22", "#32CD32", "#90EE90"],
                "rock": ["#A0826D", "#8B7355", "#696969"],
            },
            "coastal": {
                "base": ["#4682B4", "#F4A460", "#F5DEB3"],
                "water": {
                    "deep": "#006994",
                    "medium": "#4682B4",
                    "shallow": "#87CEEB",
                    "surf": "#B0E0E6",
                },
                "land": ["#F4A460", "#DEB887", "#F5DEB3"],
                "beach": ["#F5DEB3", "#EEE8AA", "#FFE4B5"],
            },
            "desert": {
                "base": ["#EDC9AF", "#F4A460", "#228B22"],
                "sand": ["#EDC9AF", "F4A460", "#FFE4B5"],
                "rock": ["#A0826D", "#8B7355", "#704214"],
                "vegetation": ["#228B22", "#90EE90", "#ADFF2F"],
            },
            "forest": {
                "base": ["#228B22", "#90EE90", "#2E8B57"],
                "trees": {"deep": "#006400", "medium": "#228B22", "light": "#90EE90"},
                "undergrowth": ["#2E8B57", "#3CB371", "#8FBC8F"],
                "meadow": ["#90EE90", "#98FB98", "#ADFF2F"],
            },
            "urban": {
                "base": ["#696969", "#A9A9A9", "#2F4F4F"],
                "buildings": ["#696969", "#808080", "#A9A9A9"],
                "roads": ["#2F4F4F", "#36454F", "#483D8B"],
                "parks": ["#228B22", "#90EE90", "#8FBC8F"],
            },
        }

        self.seasonal_adjustments = {
            "spring": {"green_shift": 20, "brightness": 10, "saturation": 15},
            "summer": {"green_shift": 0, "brightness": 5, "saturation": 10},
            "autumn": {
                "orange_shift": 30,
                "red_shift": 20,
                "brightness": -10,
                "saturation": 20,
            },
            "winter": {"blue_shift": 15, "brightness": -20, "desaturate": 30},
        }

    def get_geographic_palette(self, geo_type: str, season: str = "summer") -> Dict:
        """Get colors for specific geographic type and season"""
        base_palette = self.geographic_palettes.get(
            geo_type, self.geographic_palettes["urban"]
        )

        # Apply seasonal adjustments
        if season in self.seasonal_adjustments:
            base_palette = self._apply_seasonal_adjustment(base_palette, season)

        return base_palette

    def _apply_seasonal_adjustment(self, palette: Dict, season: str) -> Dict:
        """Apply seasonal color adjustments"""
        adjustments = self.seasonal_adjustments[season]
        adjusted = {}

        for category, colors in palette.items():
            if isinstance(colors, dict):
                adjusted[category] = {}
                for key, color in colors.items():
                    adjusted[category][key] = self._adjust_color(color, adjustments)
            elif isinstance(colors, list):
                adjusted[category] = [
                    self._adjust_color(c, adjustments) for c in colors
                ]
            else:
                adjusted[category] = self._adjust_color(colors, adjustments)

        return adjusted

    def _adjust_color(self, hex_color: str, adjustments: Dict) -> str:
        """Adjust a single color based on seasonal parameters"""
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

        # Apply adjustments
        if "green_shift" in adjustments:
            # Shift towards green
            h = (h + adjustments["green_shift"] / 360) % 1.0

        if "orange_shift" in adjustments:
            # Shift towards orange
            h = (h + adjustments["orange_shift"] / 360) % 1.0

        if "red_shift" in adjustments:
            # Shift towards red
            h = (h + adjustments["red_shift"] / 360) % 1.0

        if "blue_shift" in adjustments:
            # Shift towards blue
            h = (h + adjustments["blue_shift"] / 360) % 1.0

        if "brightness" in adjustments:
            v = max(0, min(1, v + adjustments["brightness"] / 100))

        if "saturation" in adjustments:
            s = max(0, min(1, s + adjustments["saturation"] / 100))

        if "desaturate" in adjustments:
            s = max(0, s - adjustments["desaturate"] / 100)

        # Convert back to hex
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


class ArtisticEffects:
    """OpenCV-based artistic effects for map generation"""

    def __init__(self):
        self.effect_presets = {
            "pencil_sketch": {"sigma_s": 60, "sigma_r": 0.07, "shade_factor": 0.08},
            "watercolor": {"sigma_s": 150, "sigma_r": 0.5, "blur_ksize": 3},
            "oil_painting": {"size": 5, "dynRatio": 1},
            "vintage": {"sepia_intensity": 0.2, "vignette": True, "noise": 0.02},
        }

    def apply_pencil_sketch(
        self, image: Image.Image, preset: str = None
    ) -> Image.Image:
        """Apply pencil sketch effect using OpenCV"""
        if preset:
            settings = self.effect_presets.get(
                f"pencil_sketch_{preset}", self.effect_presets["pencil_sketch"]
            )
        else:
            settings = self.effect_presets["pencil_sketch"]

        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply pencil sketch
        gray_sketch, color_sketch = cv2.pencilSketch(
            cv_image,
            sigma_s=settings["sigma_s"],
            sigma_r=settings["sigma_r"],
            shade_factor=settings["shade_factor"],
        )

        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(color_sketch, cv2.COLOR_BGR2RGB))

    def apply_watercolor(self, image: Image.Image) -> Image.Image:
        """Apply watercolor effect"""
        settings = self.effect_presets["watercolor"]

        # Convert to OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Bilateral filter for watercolor effect
        watercolor = cv2.bilateralFilter(cv_image, 15, 80, 80)

        # Add some blur for softness
        watercolor = cv2.GaussianBlur(
            watercolor, (settings["blur_ksize"], settings["blur_ksize"]), 0
        )

        # Convert back
        return Image.fromarray(cv2.cvtColor(watercolor, cv2.COLOR_BGR2RGB))

    def apply_oil_painting(self, image: Image.Image) -> Image.Image:
        """Apply oil painting effect"""
        settings = self.effect_presets["oil_painting"]

        # Convert to OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply oil painting effect
        if hasattr(cv2, "xphoto"):
            oil_painting = cv2.xphoto.oilPainting(
                cv_image, settings["size"], settings["dynRatio"]
            )
        else:
            # Fallback to bilateral filter if xphoto not available
            print(
                "Warning: cv2.xphoto not found. Using bilateral filter fallback for oil painting."
            )
            oil_painting = cv2.bilateralFilter(cv_image, 9, 75, 75)

        # Convert back
        return Image.fromarray(cv2.cvtColor(oil_painting, cv2.COLOR_BGR2RGB))

    def apply_vintage(self, image: Image.Image) -> Image.Image:
        """Apply vintage effect with sepia and vignette"""
        settings = self.effect_presets["vintage"]

        # Convert to numpy
        img_array = np.array(image)

        # Apply sepia
        if settings["sepia_intensity"] > 0:
            sepia_filter = np.array(
                [[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]
            )
            sepia_img = img_array.dot(sepia_filter.T)
            sepia_img = np.clip(sepia_img, 0, 255)
            img_array = (
                img_array * (1 - settings["sepia_intensity"])
                + sepia_img * settings["sepia_intensity"]
            )

        # Apply vignette
        if settings["vignette"]:
            rows, cols = img_array.shape[:2]
            X_resultant_kernel = cv2.getGaussianKernel(cols, cols / 2)
            Y_resultant_kernel = cv2.getGaussianKernel(rows, rows / 2)
            kernel = Y_resultant_kernel * X_resultant_kernel.T
            mask = kernel / np.linalg.norm(kernel)
            vignette_img = img_array * mask[..., np.newaxis]
            img_array = img_array * 0.7 + vignette_img * 0.3

        # Add noise
        if settings["noise"] > 0:
            noise = np.random.normal(0, settings["noise"] * 255, img_array.shape)
            img_array = np.clip(img_array + noise, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def apply_effect(
        self, image: Image.Image, effect_name: str, preset: str = None
    ) -> Image.Image:
        """Apply an artistic effect by name"""
        effects = {
            "pencil_sketch": self.apply_pencil_sketch,
            "watercolor": self.apply_watercolor,
            "oil_painting": self.apply_oil_painting,
            "vintage": self.apply_vintage,
        }

        if effect_name in effects:
            return effects[effect_name](image, preset)
        else:
            print(f"Warning: Unknown effect '{effect_name}'")
            return image


class DDColorTiny:
    """Lightweight colorization model (45MB) - optional installation"""

    def __init__(self):
        self.model = None
        self.model_loaded = False

    def load_model(self):
        """Load DDColor tiny model"""
        try:
            # Try to import and load DDColor
            from ddcolor import DDColor

            self.model = DDColor.from_pretrained("piddnad/ddcolor_paper_tiny")
            self.model_loaded = True
            print("✓ DDColor-Tiny model loaded successfully")
        except ImportError:
            print("⚠ DDColor not installed. Install with: pip install ddcolor")
        except Exception as e:
            print(f"⚠ Could not load DDColor model: {e}")

    def colorize(self, image: Image.Image) -> Image.Image:
        """Colorize a grayscale image"""
        if not self.model_loaded:
            self.load_model()

        if self.model is None:
            return image

        # Convert to grayscale if needed
        if image.mode != "L":
            gray_image = image.convert("L")
        else:
            gray_image = image

        # Apply colorization
        try:
            colored = self.model.colorize(gray_image)
            return colored
        except Exception as e:
            print(f"⚠ Colorization failed: {e}")
            return image


class ColorEnhancer:
    """Main class that combines all color enhancement features"""

    def __init__(self):
        self.palette_api = ColorPaletteAPI()
        self.geo_rules = GeographicColorRules()
        self.artistic = ArtisticEffects()
        self.colorizer = DDColorTiny()

    def enhance_theme_colors(
        self, theme: Dict, location_type: str = None, season: str = "summer"
    ) -> Dict:
        """Enhance theme colors with intelligent palettes"""
        enhanced_theme = theme.copy()

        # Get geographic colors if location type specified
        if location_type:
            geo_colors = self.geo_rules.get_geographic_palette(location_type, season)
            enhanced_theme["geographic_colors"] = geo_colors

        # Generate intelligent palette from API
        base_colors = [
            theme.get("colors", {}).get("water", "#4682B4"),
            theme.get("colors", {}).get("land", ["#F5F5DC"])[0]
            if isinstance(theme.get("colors", {}).get("land"), list)
            else theme.get("colors", {}).get("land", "#F5F5DC"),
        ]

        intelligent_palette = self.palette_api.get_palette(base_colors)
        enhanced_theme["intelligent_palette"] = intelligent_palette

        return enhanced_theme

    def apply_artistic_effect(
        self, image: Image.Image, effect: str, preset: str = None
    ) -> Image.Image:
        """Apply artistic effect to generated map"""
        return self.artistic.apply_effect(image, effect, preset)

    def colorize_map(self, image: Image.Image, style: str = "artistic") -> Image.Image:
        """Apply colorization to grayscale map"""
        return self.colorizer.colorize(image)

    def apply_enhancement(self, image_path: str, enhancement_type: str, city: str = ""):
        """Apply color enhancement to image file"""
        from PIL import Image as PILImage

        # Open the image
        image = PILImage.open(image_path)

        # Apply enhancement based on type
        if enhancement_type == "vibrant":
            # Increase saturation
            enhancer = PILImage.ImageEnhance.Color(image)
            image = enhancer.enhance(1.5)
        elif enhancement_type == "vintage":
            # Apply vintage effect (includes sepia)
            image = self.artistic.apply_effect(image, "vintage")
        elif enhancement_type == "cool":
            # Cool color temperature
            img_array = np.array(image)
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 1.2, 0, 255)  # Boost blue
            image = PILImage.fromarray(img_array.astype(np.uint8))
        elif enhancement_type == "warm":
            # Warm color temperature
            img_array = np.array(image)
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.2, 0, 255)  # Boost red
            image = PILImage.fromarray(img_array.astype(np.uint8))
        elif enhancement_type == "dramatic":
            # High contrast
            enhancer = PILImage.ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
        elif enhancement_type == "watercolor":
            # Watercolor effect
            image = self.artistic.apply_effect(image, "watercolor")
        elif enhancement_type == "pencil_sketch":
            # Pencil sketch effect
            image = self.artistic.apply_effect(image, "pencil_sketch")
        elif enhancement_type == "oil_painting":
            # Oil painting effect
            image = self.artistic.apply_effect(image, "oil_painting")
        elif enhancement_type.startswith("seasonal_"):
            # Apply seasonal color shift
            season = enhancement_type.split("_")[1]
            image = self._apply_seasonal_to_image(image, season)
        elif enhancement_type == "geographic_colors":
            # Boost geographic-specific colors (greens/blues)
            image = self._apply_geographic_boost(image)
        elif enhancement_type == "intelligent_palette":
            # Apply a color harmony adjustment
            image = self._apply_palette_optimization(image)
        else:
            print(f"Unknown enhancement: {enhancement_type}")
            return

        # Save the enhanced image
        image.save(image_path, quality=95)
        print(f"[+] Applied {enhancement_type} enhancement to {image_path}")

    def _apply_seasonal_to_image(self, image: Image.Image, season: str) -> Image.Image:
        """Apply seasonal color shift directly to pixels"""
        adjustments = self.geo_rules.seasonal_adjustments.get(season, {})
        if not adjustments:
            return image

        img_array = np.array(image).astype(np.float32)

        # Simple color shifts based on season
        if season == "spring":
            # Shift towards green and brighten
            img_array[:, :, 1] *= 1.15  # Boost green
            img_array[:, :, 2] *= 1.05  # Boost blue (cool)
        elif season == "summer":
            # Vivid and bright
            img_array *= 1.1
        elif season == "autumn":
            # Shift towards orange/red
            img_array[:, :, 0] *= 1.2  # Boost red
            img_array[:, :, 1] *= 0.9  # Reduce green (makes it more orange)
        elif season == "winter":
            # Desaturate and cool/blue
            img_array[:, :, 2] *= 1.2  # Boost blue
            # Simple desaturation: pull towards grayscale
            gray = np.mean(img_array, axis=2, keepdims=True)
            img_array = img_array * 0.7 + gray * 0.3

        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)

    def _apply_geographic_boost(self, image: Image.Image) -> Image.Image:
        """Boost geographic-specific colors"""
        from PIL import ImageEnhance

        # Enhance color vibrancy
        color_enhancer = ImageEnhance.Color(image)
        image = color_enhancer.enhance(1.4)
        # Sligthly boost contrast
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(1.1)
        return image

    def _apply_palette_optimization(self, image: Image.Image) -> Image.Image:
        """Apply color harmony adjustments"""
        from PIL import ImageOps

        # Auto-contrast to ensure full range
        image = ImageOps.autocontrast(image, cutoff=1)
        return image


# Utility functions
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color"""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend_colors(color1: str, color2: str, ratio: float = 0.5) -> str:
    """Blend two colors"""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    blended = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))

    return rgb_to_hex(blended)


if __name__ == "__main__":
    # Test the color enhancement
    enhancer = ColorEnhancer()

    # Test palette generation
    print("Testing palette generation...")
    palette = enhancer.palette_api.get_palette(["#4682B4", "#F5F5DC"])
    print(f"Generated palette: {palette}")

    # Test geographic colors
    print("\nTesting geographic colors...")
    mountain_colors = enhancer.geo_rules.get_geographic_palette("mountain", "autumn")
    print(f"Mountain autumn colors: {mountain_colors}")

    print("\n✓ Color enhancement module ready!")
