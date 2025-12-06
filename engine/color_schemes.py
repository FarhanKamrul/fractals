"""
Color schemes for fractal visualization.

Provides multiple color palettes and smooth gradient interpolation.
Includes vectorized color mapping for high-performance rendering.
"""

import math
from typing import Tuple
import numpy as np


class ColorScheme:
    """Base class for color schemes."""

    def __init__(self, name: str):
        """
        Initialize color scheme.

        Args:
            name: Display name of the color scheme
        """
        self.name = name
        self._lut_cache = {}  # Cache for color lookup tables

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        """
        Map iteration count to RGB color.

        Args:
            iteration: Number of iterations before escape
            max_iter: Maximum possible iterations

        Returns:
            Tuple of (R, G, B) values in range [0, 255]
        """
        raise NotImplementedError

    def get_lut(self, max_iter: int) -> np.ndarray:
        """
        Get a color lookup table for vectorized rendering.

        Args:
            max_iter: Maximum iteration count

        Returns:
            numpy array of shape (max_iter + 1, 3) with RGB values
        """
        if max_iter in self._lut_cache:
            return self._lut_cache[max_iter]

        # Build LUT
        lut = np.zeros((max_iter + 1, 3), dtype=np.uint8)
        for i in range(max_iter + 1):
            lut[i] = self.get_color(i, max_iter)

        # Cache it (limit cache size)
        if len(self._lut_cache) > 10:
            self._lut_cache.clear()
        self._lut_cache[max_iter] = lut

        return lut

    def get_colors_vectorized(self, iterations: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Vectorized color mapping using lookup table.

        Args:
            iterations: 2D array of iteration counts
            max_iter: Maximum iteration count

        Returns:
            3D array of RGB values (height, width, 3)
        """
        lut = self.get_lut(max_iter)
        # Clamp iterations to valid range
        clamped = np.clip(iterations, 0, max_iter)
        return lut[clamped]


class GrayscaleScheme(ColorScheme):
    """Simple grayscale color scheme."""

    def __init__(self):
        super().__init__("Grayscale")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 0)

        # Smooth gradient from black to white
        value = int(255 * (iteration / max_iter))
        return (value, value, value)


class PsychedelicScheme(ColorScheme):
    """Vibrant, psychedelic color scheme."""

    def __init__(self):
        super().__init__("Psychedelic")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 0)

        # Use sine waves for smooth color cycling
        t = iteration / max_iter
        r = int(127.5 * (math.sin(t * math.pi * 2 * 3) + 1))
        g = int(127.5 * (math.sin(t * math.pi * 2 * 5 + 2) + 1))
        b = int(127.5 * (math.sin(t * math.pi * 2 * 7 + 4) + 1))

        return (r, g, b)


class FireScheme(ColorScheme):
    """Warm fire/lava color scheme."""

    def __init__(self):
        super().__init__("Fire")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 0)

        # Gradient through blacks, reds, oranges, yellows, whites
        t = iteration / max_iter

        if t < 0.25:
            # Black to dark red
            ratio = t / 0.25
            r = int(128 * ratio)
            return (r, 0, 0)
        elif t < 0.5:
            # Dark red to bright red
            ratio = (t - 0.25) / 0.25
            r = int(128 + 127 * ratio)
            return (r, 0, 0)
        elif t < 0.75:
            # Bright red to orange
            ratio = (t - 0.5) / 0.25
            r = 255
            g = int(165 * ratio)
            return (r, g, 0)
        else:
            # Orange to yellow
            ratio = (t - 0.75) / 0.25
            r = 255
            g = int(165 + 90 * ratio)
            b = int(100 * ratio)
            return (r, g, b)


class OceanScheme(ColorScheme):
    """Cool ocean/water color scheme."""

    def __init__(self):
        super().__init__("Ocean")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 32)  # Deep ocean blue

        # Gradient through deep blues, cyans, aquas
        t = iteration / max_iter

        if t < 0.33:
            # Deep blue to medium blue
            ratio = t / 0.33
            r = 0
            g = int(64 * ratio)
            b = int(32 + 96 * ratio)
            return (r, g, b)
        elif t < 0.67:
            # Medium blue to cyan
            ratio = (t - 0.33) / 0.34
            r = 0
            g = int(64 + 191 * ratio)
            b = int(128 + 127 * ratio)
            return (r, g, b)
        else:
            # Cyan to bright aqua
            ratio = (t - 0.67) / 0.33
            r = int(64 * ratio)
            g = 255
            b = 255
            return (r, g, b)


class RainbowScheme(ColorScheme):
    """Full spectrum rainbow color scheme."""

    def __init__(self):
        super().__init__("Rainbow")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 0)

        # HSV to RGB conversion for smooth rainbow
        t = (iteration / max_iter) * 360  # Hue in degrees

        h = t
        s = 1.0
        v = 1.0

        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


class ClassicScheme(ColorScheme):
    """Classic Mandelbrot set colors - blue exterior."""

    def __init__(self):
        super().__init__("Classic")

    def get_color(self, iteration: int, max_iter: int) -> Tuple[int, int, int]:
        if iteration == max_iter:
            return (0, 0, 0)

        # Smooth blue gradient with some variation
        t = iteration / max_iter

        # Use logarithmic scaling for better detail
        log_t = math.log(1 + t * 10) / math.log(11)

        r = int(log_t * 66)
        g = int(log_t * 30 + 100 * math.sin(t * math.pi * 2))
        b = int(128 + log_t * 127)

        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return (r, g, b)


# Registry of all available color schemes
COLOR_SCHEMES = [
    ClassicScheme(),
    PsychedelicScheme(),
    FireScheme(),
    OceanScheme(),
    RainbowScheme(),
    GrayscaleScheme(),
]


def get_color_scheme(index: int = 0) -> ColorScheme:
    """
    Get a color scheme by index.

    Args:
        index: Index into COLOR_SCHEMES list

    Returns:
        ColorScheme instance
    """
    return COLOR_SCHEMES[index % len(COLOR_SCHEMES)]
