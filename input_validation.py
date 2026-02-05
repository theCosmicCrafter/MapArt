"""
Input validation and sanitization module for Map Poster Generator.
Provides secure input handling and validation functions.
"""

import re
import os
from typing import Tuple, Optional


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


# Allowed characters for city/country names (unicode letters, spaces, hyphens, apostrophes)
SAFE_NAME_PATTERN = re.compile(r"^[\w\s\-\'\.\,\(\)]+$", re.UNICODE)

# Maximum input lengths
MAX_CITY_LENGTH = 100
MAX_COUNTRY_LENGTH = 100
MAX_STATE_LENGTH = 50

# Dangerous path characters and patterns
DANGEROUS_PATH_CHARS = ["..", "//", "\\", "\x00", "\n", "\r"]
DANGEROUS_FILE_EXTENSIONS = [".exe", ".bat", ".cmd", ".sh", ".ps1", ".vbs", ".js"]

# Allowed output formats
ALLOWED_FORMATS = {"png", "jpg", "jpeg", "svg", "pdf"}

# Allowed map shapes
ALLOWED_SHAPES = {"rectangle", "circle", "triangle"}

# Allowed artistic effects
ALLOWED_EFFECTS = {"none", "watercolor", "pencil_sketch", "oil_painting", "vintage"}

# Allowed color enhancements
ALLOWED_ENHANCEMENTS = {
    "none",
    "intelligent_palette",
    "geographic_colors",
    "seasonal_summer",
    "seasonal_autumn",
    "seasonal_winter",
    "seasonal_spring",
}


def sanitize_city_country(
    name: str, max_length: int = 100, allow_empty: bool = False
) -> str:
    """
    Sanitize city or country name input.

    Args:
        name: Raw input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If input contains dangerous characters
    """
    if not isinstance(name, str):
        raise ValidationError("Input must be a string")

    if not name and not allow_empty:
        raise ValidationError("Input cannot be empty")

    # Trim whitespace
    name = name.strip()

    # Check length
    if len(name) > max_length:
        raise ValidationError(
            f"Input exceeds maximum length of {max_length} characters"
        )

    if len(name) == 0:
        raise ValidationError("Input cannot be empty")

    # Check for dangerous characters
    for char in DANGEROUS_PATH_CHARS:
        if char in name:
            raise ValidationError(f"Input contains invalid characters")

    # Allow unicode letters, numbers, spaces, and common punctuation
    # Block control characters and special symbols
    if not SAFE_NAME_PATTERN.match(name):
        # More lenient: just block control characters
        for char in name:
            if ord(char) < 32:  # Control characters
                raise ValidationError("Input contains invalid control characters")

    return name


def validate_output_format(format_str: str) -> str:
    """
    Validate and normalize output format.

    Args:
        format_str: Input format string

    Returns:
        Normalized format string

    Raises:
        ValidationError: If format is not allowed
    """
    if not format_str:
        return "png"

    fmt = format_str.lower().strip().lstrip(".")

    if fmt not in ALLOWED_FORMATS:
        raise ValidationError(
            f"Invalid format '{format_str}'. Allowed: {', '.join(ALLOWED_FORMATS)}"
        )

    return fmt


def validate_map_shape(shape: str) -> str:
    """Validate map shape parameter."""
    if not shape:
        return "rectangle"

    shape = shape.lower().strip()

    if shape not in ALLOWED_SHAPES:
        raise ValidationError(
            f"Invalid shape '{shape}'. Allowed: {', '.join(ALLOWED_SHAPES)}"
        )

    return shape


def validate_artistic_effect(effect: str) -> str:
    """Validate artistic effect parameter."""
    if not effect or effect.lower() == "none":
        return "none"

    effect = effect.lower().strip()

    if effect not in ALLOWED_EFFECTS:
        raise ValidationError(
            f"Invalid effect '{effect}'. Allowed: {', '.join(ALLOWED_EFFECTS)}"
        )

    return effect


def validate_color_enhancement(enhancement: str) -> str:
    """Validate color enhancement parameter."""
    if not enhancement or enhancement.lower() == "none":
        return "none"

    enhancement = enhancement.lower().strip()

    if enhancement not in ALLOWED_ENHANCEMENTS:
        raise ValidationError(
            f"Invalid enhancement '{enhancement}'. Allowed: {', '.join(ALLOWED_ENHANCEMENTS)}"
        )

    return enhancement


def validate_dimensions(width: float, height: float) -> Tuple[float, float]:
    """
    Validate poster dimensions.

    Args:
        width: Width in inches
        height: Height in inches

    Returns:
        Validated (width, height) tuple

    Raises:
        ValidationError: If dimensions are invalid
    """
    try:
        width = float(width)
        height = float(height)
    except (TypeError, ValueError):
        raise ValidationError("Dimensions must be numeric values")

    MIN_DIMENSION = 4.0
    MAX_DIMENSION = 48.0

    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ValidationError(f"Dimensions must be at least {MIN_DIMENSION} inches")

    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError(f"Dimensions cannot exceed {MAX_DIMENSION} inches")

    if width * height > 1000:  # Max 1000 square inches
        raise ValidationError("Total poster area cannot exceed 1000 square inches")

    return width, height


def validate_distance(distance: int) -> int:
    """
    Validate map distance/radius.

    Args:
        distance: Distance in meters

    Returns:
        Validated distance
    """
    try:
        distance = int(distance)
    except (TypeError, ValueError):
        raise ValidationError("Distance must be an integer")

    MIN_DISTANCE = 1000  # 1km
    MAX_DISTANCE = 500000  # 500km

    if distance < MIN_DISTANCE:
        raise ValidationError(f"Distance must be at least {MIN_DISTANCE} meters (1km)")

    if distance > MAX_DISTANCE:
        raise ValidationError(f"Distance cannot exceed {MAX_DISTANCE} meters (50km)")

    return distance


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal.

    Args:
        filename: Input filename

    Returns:
        Sanitized filename
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")

    # Remove path components
    filename = os.path.basename(filename)

    # Check for dangerous patterns
    for char in DANGEROUS_PATH_CHARS:
        if char in filename:
            raise ValidationError("Filename contains invalid characters")

    # Check extension
    _, ext = os.path.splitext(filename)
    if ext.lower() in DANGEROUS_FILE_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' is not allowed")

    return filename


def validate_theme_name(theme: str, available_themes: list) -> str:
    """
    Validate theme name against available themes.

    Args:
        theme: Input theme name
        available_themes: List of valid theme names

    Returns:
        Validated theme name
    """
    if not theme:
        return "feature_based"

    theme = theme.lower().strip()

    if theme not in [t.lower() for t in available_themes]:
        raise ValidationError(
            f"Theme '{theme}' not found. Available: {', '.join(available_themes)}"
        )

    # Return the properly cased theme name
    for t in available_themes:
        if t.lower() == theme:
            return t

    return theme


def validate_texture_name(texture: str, available_textures: list) -> str:
    """Validate texture name."""
    if not texture or texture.lower() == "none":
        return "none"

    texture = texture.lower().strip()

    if texture not in [t.lower() for t in available_textures]:
        raise ValidationError(
            f"Texture '{texture}' not found. Available: {', '.join(available_textures)}"
        )

    for t in available_textures:
        if t.lower() == texture:
            return t

    return texture


def safe_input_validator(
    city: str,
    country: str,
    state: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    distance: Optional[int] = None,
    format_str: Optional[str] = None,
    theme: Optional[str] = None,
    texture: Optional[str] = None,
    available_themes: Optional[list] = None,
    available_textures: Optional[list] = None,
) -> dict:
    """
    Comprehensive input validator for all user inputs.

    Returns a dictionary of validated values or raises ValidationError.
    """
    result = {}

    # Validate city and country
    result["city"] = sanitize_city_country(city, MAX_CITY_LENGTH)
    result["country"] = sanitize_city_country(
        country, MAX_COUNTRY_LENGTH, allow_empty=True
    )

    if state:
        result["state"] = sanitize_city_country(
            state, MAX_STATE_LENGTH, allow_empty=True
        )
    else:
        result["state"] = ""

    # Validate dimensions
    if width is not None and height is not None:
        result["width"], result["height"] = validate_dimensions(width, height)
    else:
        result["width"] = 12.0
        result["height"] = 16.0

    # Validate distance
    if distance is not None:
        result["distance"] = validate_distance(distance)
    else:
        result["distance"] = 12000

    # Validate format
    if format_str:
        result["format"] = validate_output_format(format_str)
    else:
        result["format"] = "png"

    # Validate theme
    if theme and available_themes:
        result["theme"] = validate_theme_name(theme, available_themes)
    else:
        result["theme"] = theme or "feature_based"

    # Validate texture
    if texture and available_textures:
        result["texture"] = validate_texture_name(texture, available_textures)
    else:
        result["texture"] = texture or "none"

    return result
