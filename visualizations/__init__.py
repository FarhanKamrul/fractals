"""
Visualizations module.

Contains all fractal and mathematical pattern implementations.
"""

from .base import BaseVisualization
from .mandelbrot import Mandelbrot
from .julia import Julia

# Registry of all available visualizations
VISUALIZATIONS = [
    Mandelbrot,
    Julia,
]

__all__ = ['BaseVisualization', 'Mandelbrot', 'Julia', 'VISUALIZATIONS']
