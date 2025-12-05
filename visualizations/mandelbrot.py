"""
Mandelbrot Set fractal implementation.

The Mandelbrot set is the set of complex numbers c for which the function
f(z) = z² + c does not diverge when iterated from z = 0.
"""

from .base import BaseVisualization


class Mandelbrot(BaseVisualization):
    """
    The classic Mandelbrot Set fractal.

    The most iconic fractal, discovered by Benoit Mandelbrot.
    Points are colored based on how quickly they escape to infinity.
    """

    def __init__(self):
        """Initialize Mandelbrot set with default parameters."""
        super().__init__()

    def get_name(self) -> str:
        """Get the display name."""
        return "Mandelbrot Set"

    def get_default_params(self) -> dict:
        """Get default parameters for Mandelbrot set."""
        return {
            'center_x': -0.5,
            'center_y': 0.0,
            'zoom': 0.5,
            'max_iter': 256,
            'escape_radius': 2.0,
        }

    def compute(self, x: float, y: float) -> int:
        """
        Compute iterations for a point in the Mandelbrot set.

        Args:
            x: Real component of complex number c
            y: Imaginary component of complex number c

        Returns:
            Number of iterations before escape (or max_iter)
        """
        # c is the complex number we're testing
        cx, cy = x, y

        # z starts at 0
        zx, zy = 0.0, 0.0

        # Get escape radius
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Iterate z = z² + c
        iteration = 0
        while iteration < self.max_iter:
            # Compute z²
            zx_sq = zx * zx
            zy_sq = zy * zy

            # Check if escaped
            if zx_sq + zy_sq > escape_radius_sq:
                break

            # z = z² + c
            # (zx + zy*i)² = zx² - zy² + 2*zx*zy*i
            zy = 2 * zx * zy + cy
            zx = zx_sq - zy_sq + cx

            iteration += 1

        return iteration
