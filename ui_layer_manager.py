"""
UI Layer Manager Module

Electron IPC handlers and UI components for managing map layers.
"""

from map_layer_compositor import BlendMode, LayerCompositor

LAYER_TYPE_ICONS = {
    'city': '🏙️',
    'railway': '🚂',
    'cycling': '🚴',
    'transit': '🚌',
    'maritime': '⚓',
}

BLEND_MODE_LABELS = {
    'normal': 'Normal',
    'multiply': 'Multiply (Darken)',
    'screen': 'Screen (Lighten)',
    'overlay': 'Overlay (Contrast)',
    'soft_light': 'Soft Light',
    'hard_light': 'Hard Light',
}

PRESETS = {
    'city_railway_overlay': 'City + Railways',
    'cycling_highlight': 'Cycling Routes',
    'transit_focus': 'Public Transit',
    'coastal_city': 'Coastal/Maritime',
    'triple_transit': 'All Transit Layers',
}
