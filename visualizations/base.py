"""
Base visualization class that all fractals inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple


class BaseVisualization(ABC):
    """
    Abstract base class for all visualizations.

    Each visualization must implement the compute method and provide
    metadata about itself.
    """

    def __init__(self):
        """Initialize the visualization with default parameters."""
        self.params = self.get_default_params()
        self.reset_view()

    def reset_view(self):
        """Reset the viewport to default position and zoom."""
        defaults = self.get_default_params()
        self.center_x = defaults.get('center_x', 0.0)
        self.center_y = defaults.get('center_y', 0.0)
        self.zoom = defaults.get('zoom', 1.0)
        self.max_iter = defaults.get('max_iter', 256)

    @abstractmethod
    def compute(self, x: float, y: float) -> int:
        """
        Compute the iteration count for a point in the complex plane.

        Args:
            x: Real component of the complex number
            y: Imaginary component of the complex number

        Returns:
            Number of iterations before escape (or max_iter if no escape)
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the display name of this visualization.

        Returns:
            Human-readable name
        """
        pass

    @abstractmethod
    def get_default_params(self) -> Dict:
        """
        Get default parameters for this visualization.

        Returns:
            Dictionary containing default values for:
            - center_x: Center x coordinate
            - center_y: Center y coordinate
            - zoom: Initial zoom level
            - max_iter: Maximum iterations
            - Any visualization-specific parameters
        """
        pass

    def set_param(self, key: str, value):
        """
        Set a parameter value.

        Args:
            key: Parameter name
            value: Parameter value
        """
        self.params[key] = value

        # Update common parameters
        if key == 'max_iter':
            self.max_iter = value

    def get_param(self, key: str, default=None):
        """
        Get a parameter value.

        Args:
            key: Parameter name
            default: Default value if key not found

        Returns:
            Parameter value or default
        """
        return self.params.get(key, default)

    def zoom_in(self, factor: float = 2.0):
        """
        Zoom in by a factor.

        Args:
            factor: Zoom multiplication factor (default 2.0)
        """
        self.zoom *= factor

    def zoom_out(self, factor: float = 2.0):
        """
        Zoom out by a factor.

        Args:
            factor: Zoom division factor (default 2.0)
        """
        self.zoom /= factor

    def pan(self, dx: float, dy: float):
        """
        Pan the view by screen-space amounts.

        Args:
            dx: Change in x (screen coordinates)
            dy: Change in y (screen coordinates)
        """
        self.center_x += dx / self.zoom
        self.center_y += dy / self.zoom

    def screen_to_world(self, screen_x: int, screen_y: int,
                       screen_width: int, screen_height: int) -> Tuple[float, float]:
        """
        Convert screen coordinates to world (mathematical plane) coordinates.

        Args:
            screen_x: X position on screen
            screen_y: Y position on screen
            screen_width: Width of screen
            screen_height: Height of screen

        Returns:
            Tuple of (world_x, world_y)
        """
        # Aspect ratio correction
        aspect = screen_width / screen_height

        # Normalize to [-1, 1] range
        norm_x = (screen_x / screen_width) * 2 - 1
        norm_y = (screen_y / screen_height) * 2 - 1

        # Apply zoom and center offset
        world_x = self.center_x + (norm_x * aspect) / self.zoom
        world_y = self.center_y + norm_y / self.zoom

        return world_x, world_y

    def get_info(self) -> str:
        """
        Get information string about current state.

        Returns:
            Formatted string with current parameters
        """
        return (f"{self.get_name()} | "
                f"Zoom: {self.zoom:.2e} | "
                f"Center: ({self.center_x:.6f}, {self.center_y:.6f}) | "
                f"Max Iter: {self.max_iter}")
