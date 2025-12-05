"""
Engine module for fractal rendering.

Contains the core rendering engine and color scheme utilities.
"""

from .renderer import Renderer
from .color_schemes import ColorScheme, get_color_scheme

__all__ = ['Renderer', 'ColorScheme', 'get_color_scheme']
