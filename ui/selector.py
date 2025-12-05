"""
Visualization selector for switching between different fractals.
"""

from typing import List, Type
from visualizations.base import BaseVisualization


class Selector:
    """
    Manages switching between different visualizations.
    """

    def __init__(self, visualizations: List[Type[BaseVisualization]]):
        """
        Initialize selector with available visualizations.

        Args:
            visualizations: List of visualization classes
        """
        self.visualization_classes = visualizations
        self.current_index = 0
        self.current_visualization = self.visualization_classes[0]()

    def get_current(self) -> BaseVisualization:
        """
        Get the current visualization instance.

        Returns:
            Current visualization
        """
        return self.current_visualization

    def switch_to(self, index: int) -> BaseVisualization:
        """
        Switch to a specific visualization by index.

        Args:
            index: Index of visualization to switch to

        Returns:
            New current visualization
        """
        if 0 <= index < len(self.visualization_classes):
            self.current_index = index
            self.current_visualization = self.visualization_classes[index]()

        return self.current_visualization

    def next(self) -> BaseVisualization:
        """
        Switch to next visualization.

        Returns:
            New current visualization
        """
        self.current_index = (self.current_index + 1) % len(self.visualization_classes)
        self.current_visualization = self.visualization_classes[self.current_index]()
        return self.current_visualization

    def previous(self) -> BaseVisualization:
        """
        Switch to previous visualization.

        Returns:
            New current visualization
        """
        self.current_index = (self.current_index - 1) % len(self.visualization_classes)
        self.current_visualization = self.visualization_classes[self.current_index]()
        return self.current_visualization

    def get_count(self) -> int:
        """
        Get number of available visualizations.

        Returns:
            Count of visualizations
        """
        return len(self.visualization_classes)

    def get_names(self) -> List[str]:
        """
        Get names of all available visualizations.

        Returns:
            List of visualization names
        """
        return [viz_class().get_name() for viz_class in self.visualization_classes]
