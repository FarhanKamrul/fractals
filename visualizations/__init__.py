"""
Visualizations module.

Contains all fractal and mathematical pattern implementations.
"""

from .base import BaseVisualization
from .mandelbrot import Mandelbrot
from .julia import Julia
from .burning_ship import BurningShip

# Registry of all available visualizations
VISUALIZATIONS = [
    Mandelbrot,
    Julia,
    BurningShip,
]

__all__ = ['BaseVisualization', 'Mandelbrot', 'Julia', 'BurningShip', 'VISUALIZATIONS']
