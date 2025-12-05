"""
Julia Set fractal implementation.

The Julia set is similar to the Mandelbrot set but uses a fixed complex
parameter c, while z varies. Different values of c produce vastly different
and beautiful patterns.
"""

from .base import BaseVisualization


class Julia(BaseVisualization):
    """
    Julia Set fractal.

    Related to the Mandelbrot set, but produces different beautiful patterns
    for each choice of the complex parameter c.
    """

    def __init__(self, c_real: float = -0.7, c_imag: float = 0.27015):
        """
        Initialize Julia set with default parameters.

        Args:
            c_real: Real component of the Julia set constant
            c_imag: Imaginary component of the Julia set constant
        """
        super().__init__()
        self.set_param('c_real', c_real)
        self.set_param('c_imag', c_imag)

    def get_name(self) -> str:
        """Get the display name."""
        c_real = self.get_param('c_real')
        c_imag = self.get_param('c_imag')
        return f"Julia Set (c = {c_real:.3f} + {c_imag:.3f}i)"

    def get_default_params(self) -> dict:
        """Get default parameters for Julia set."""
        return {
            'center_x': 0.0,
            'center_y': 0.0,
            'zoom': 0.5,
            'max_iter': 256,
            'escape_radius': 2.0,
            'c_real': -0.7,
            'c_imag': 0.27015,
        }

    def compute(self, x: float, y: float) -> int:
        """
        Compute iterations for a point in the Julia set.

        Args:
            x: Real component of z
            y: Imaginary component of z

        Returns:
            Number of iterations before escape (or max_iter)
        """
        # c is fixed for Julia sets
        cx = self.get_param('c_real')
        cy = self.get_param('c_imag')

        # z starts at the point we're testing
        zx, zy = x, y

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

    def set_c(self, c_real: float, c_imag: float):
        """
        Set the Julia set constant c.

        Args:
            c_real: Real component of c
            c_imag: Imaginary component of c
        """
        self.set_param('c_real', c_real)
        self.set_param('c_imag', c_imag)


# Some beautiful Julia set presets
JULIA_PRESETS = [
    (-0.7, 0.27015),   # Classic spiral
    (-0.8, 0.156),     # Douady's rabbit
    (0.285, 0.01),     # Dragon
    (-0.4, 0.6),       # Branching
    (0.28, 0.008),     # Swirls
    (-0.835, -0.2321), # Lightning
    (-0.70176, -0.3842), # Dendrite
]
