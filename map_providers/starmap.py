"""
Star map provider for generating 2D constellation charts.
Uses astronomical calculations to render night sky from any location/date.
"""

import numpy as np
from datetime import datetime
from typing import Optional, Tuple, List

# Simplified bright star catalog (name, RA, Dec, magnitude)
# RA in hours (0-24), Dec in degrees (-90 to +90)
BRIGHT_STARS = [
    # Name, RA (h), Dec (deg), magnitude
    ("Sirius", 6.75, -16.7, -1.46),
    ("Canopus", 6.4, -52.7, -0.74),
    ("Arcturus", 14.26, 19.1, -0.05),
    ("Rigil Kentaurus", 14.66, -60.8, -0.01),
    ("Vega", 18.62, 38.8, 0.03),
    ("Capella", 5.28, 46.0, 0.08),
    ("Rigel", 5.24, -8.2, 0.13),
    ("Procyon", 7.65, 5.2, 0.38),
    ("Betelgeuse", 5.92, 7.4, 0.50),
    ("Achernar", 1.63, -57.2, 0.50),
    ("Hadar", 14.06, -60.4, 0.61),
    ("Altair", 19.85, 8.9, 0.77),
    ("Acrux", 12.44, -63.1, 0.77),
    ("Aldebaran", 4.6, 16.5, 0.85),
    ("Antares", 16.49, -26.4, 0.96),
    ("Spica", 13.42, -11.2, 0.98),
    ("Pollux", 7.76, 27.9, 1.14),
    ("Fomalhaut", 22.96, -29.6, 1.16),
    ("Deneb", 20.70, 45.3, 1.25),
    ("Mimosa", 12.85, -59.7, 1.25),
    ("Regulus", 10.14, 11.9, 1.35),
    ("Adhara", 6.98, -28.9, 1.50),
    ("Castor", 7.58, 31.9, 1.58),
    ("Gacrux", 12.44, -57.1, 1.64),
    ("Bellatrix", 5.42, 6.3, 1.64),
    ("Elnath", 5.44, 28.6, 1.65),
    ("Miaplacidus", 9.22, -69.7, 1.67),
    ("Alnilam", 5.60, -1.2, 1.69),
    ("Alnair", 22.14, -46.9, 1.74),
    ("Alioth", 12.90, 55.9, 1.76),
    ("Kaus Australis", 18.40, -34.4, 1.79),
    ("Dubhe", 11.06, 61.8, 1.81),
    ("Mirfak", 3.41, 49.9, 1.82),
    ("Wezen", 7.65, -26.4, 1.83),
    ("Sargas", 17.62, -43.0, 1.84),
    ("Kaus Media", 18.37, -29.3, 1.85),
    ("Avior", 8.38, -59.5, 1.86),
    ("Menkalinan", 5.99, 44.9, 1.90),
    ("Atria", 16.81, -69.0, 1.91),
    ("Alhena", 6.75, 16.4, 1.93),
    ("Peacock", 20.43, -56.7, 1.94),
]

# Simplified constellation stick figures (indices into BRIGHT_STARS)
CONSTELLATIONS = {
    "Orion": [(26, 25), (25, 27), (27, 8)],  # Bellatrix-Betelgeuse-Alnilam
    "Ursa Major": [(29, 31), (31, 32)],  # Alioth-Dubhe-Mirfak (simplified)
    "Scorpius": [(14, 34)],  # Antares-Sargas
    "Crux": [(11, 23)],  # Mimosa-Gacrux
    "Centaurus": [(4, 10)],  # Rigil-Hadar
}


def calculate_star_positions(lat: float, lon: float, date: Optional[datetime] = None) -> List[Tuple[str, float, float, float]]:
    """
    Calculate visible star positions from a given location.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Date/time for calculation (default: now)
        
    Returns:
        List of (name, x, y, magnitude) for visible stars
    """
    if date is None:
        date = datetime.now()
    
    # Julian date calculation (simplified)
    year, month, day = date.year, date.month, date.day
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    
    # Local sidereal time (simplified)
    hours = date.hour + date.minute / 60 + date.second / 3600
    LST = (JD - 2451545.0) * 0.00273791 + hours + lon / 15
    LST = LST % 24
    
    visible_stars = []
    
    for name, ra, dec, mag in BRIGHT_STARS:
        # Hour angle
        HA = (LST - ra) % 24
        HA_rad = np.radians(HA * 15)
        dec_rad = np.radians(dec)
        lat_rad = np.radians(lat)
        
        # Altitude calculation
        sin_alt = np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(HA_rad)
        alt = np.degrees(np.arcsin(sin_alt))
        
        # Azimuth calculation
        y = np.sin(HA_rad)
        x = np.cos(HA_rad) * np.sin(lat_rad) - np.tan(dec_rad) * np.cos(lat_rad)
        az = np.degrees(np.arctan2(y, x)) % 360
        
        # Only include stars above horizon
        if alt > 10:  # At least 10 degrees above horizon
            # Convert to stereographic projection (simplified)
            # x = azimuth (0-360 mapped to -1 to 1)
            # y = altitude (0-90 mapped to 0 to 1)
            x = ((az / 360) * 2 - 1) * np.cos(np.radians(alt))
            y = (alt / 90) * np.sin(np.radians(az))
            visible_stars.append((name, x, y, mag))
    
    return visible_stars


def get_star_color_scheme() -> dict:
    """
    Get color scheme optimized for star maps.
    
    Returns:
        dict with color values for star map features
    """
    return {
        "bg": "#0a0a1a",           # Deep navy/black sky
        "star": "#FFFFFF",          # White stars
        "star_bright": "#FFF8DC",   # Cornsilk for bright stars
        "constellation": "#4169E1", # Royal blue lines
        "grid": "#1a1a2e",          # Subtle grid
        "text": "#E0E0E0",          # Light gray text
        "label": "#87CEEB",         # Sky blue labels
    }


def get_constellation_lines() -> List[Tuple[int, int]]:
    """
    Get constellation line indices.
    
    Returns:
        List of (star1_index, star2_index) tuples
    """
    lines = []
    for constellation, star_pairs in CONSTELLATIONS.items():
        for pair in star_pairs:
            lines.append(pair)
    return lines
