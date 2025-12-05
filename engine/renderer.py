"""
Core rendering engine for fractal visualization.

Handles pygame window management, pixel computation, and display.
"""

import pygame
import numpy as np
from typing import Tuple
from .color_schemes import ColorScheme


class Renderer:
    """
    Main rendering engine that draws fractals to the screen.
    """

    def __init__(self, width: int = 1200, height: int = 800, title: str = "Fractal Visualizer"):
        """
        Initialize the renderer.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()
        self.fps = 60

        # Font for UI text
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Rendering surface
        self.surface = pygame.Surface((width, height))

    def render(self, visualization, color_scheme: ColorScheme, show_info: bool = True):
        """
        Render a visualization to the screen.

        Args:
            visualization: BaseVisualization instance to render
            color_scheme: ColorScheme instance for coloring
            show_info: Whether to display info overlay
        """
        # Compute fractal for each pixel
        for y in range(self.height):
            for x in range(self.width):
                # Convert screen coordinates to world coordinates
                world_x, world_y = visualization.screen_to_world(
                    x, y, self.width, self.height
                )

                # Compute iteration count
                iteration = visualization.compute(world_x, world_y)

                # Get color from scheme
                color = color_scheme.get_color(iteration, visualization.max_iter)

                # Draw pixel
                self.surface.set_at((x, y), color)

        # Blit surface to screen
        self.screen.blit(self.surface, (0, 0))

        # Draw info overlay if enabled
        if show_info:
            self.draw_info(visualization, color_scheme)

        pygame.display.flip()

    def render_optimized(self, visualization, color_scheme: ColorScheme,
                        show_info: bool = True, chunk_size: int = 8):
        """
        Optimized rendering with chunked updates for responsiveness.

        Args:
            visualization: BaseVisualization instance to render
            color_scheme: ColorScheme instance for coloring
            show_info: Whether to display info overlay
            chunk_size: Number of rows to render per frame
        """
        # Render in chunks to maintain responsiveness
        for start_y in range(0, self.height, chunk_size):
            end_y = min(start_y + chunk_size, self.height)

            for y in range(start_y, end_y):
                for x in range(self.width):
                    # Convert screen coordinates to world coordinates
                    world_x, world_y = visualization.screen_to_world(
                        x, y, self.width, self.height
                    )

                    # Compute iteration count
                    iteration = visualization.compute(world_x, world_y)

                    # Get color from scheme
                    color = color_scheme.get_color(iteration, visualization.max_iter)

                    # Draw pixel
                    self.surface.set_at((x, y), color)

            # Update display with partial progress
            self.screen.blit(self.surface, (0, 0))
            if show_info:
                self.draw_info(visualization, color_scheme, rendering=True,
                             progress=end_y / self.height)
            pygame.display.flip()

        # Final update without progress bar
        if show_info:
            self.draw_info(visualization, color_scheme)
            pygame.display.flip()

    def draw_info(self, visualization, color_scheme: ColorScheme,
                 rendering: bool = False, progress: float = 1.0):
        """
        Draw information overlay on screen.

        Args:
            visualization: Current visualization
            color_scheme: Current color scheme
            rendering: Whether currently rendering
            progress: Rendering progress (0.0 to 1.0)
        """
        # Semi-transparent background
        overlay = pygame.Surface((self.width, 80))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Visualization info
        info_text = visualization.get_info()
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

        # Color scheme
        scheme_text = f"Color: {color_scheme.name}"
        scheme_surface = self.small_font.render(scheme_text, True, (200, 200, 200))
        self.screen.blit(scheme_surface, (10, 35))

        # FPS counter
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.small_font.render(fps_text, True, (200, 200, 200))
        self.screen.blit(fps_surface, (10, 55))

        # Rendering progress bar
        if rendering and progress < 1.0:
            bar_width = 300
            bar_height = 20
            bar_x = self.width - bar_width - 10
            bar_y = 10

            # Background
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height))

            # Progress
            pygame.draw.rect(self.screen, (0, 200, 0),
                           (bar_x, bar_y, int(bar_width * progress), bar_height))

            # Border
            pygame.draw.rect(self.screen, (255, 255, 255),
                           (bar_x, bar_y, bar_width, bar_height), 2)

            # Percentage text
            pct_text = f"Rendering: {int(progress * 100)}%"
            pct_surface = self.small_font.render(pct_text, True, (255, 255, 255))
            self.screen.blit(pct_surface, (bar_x + 5, bar_y + 2))

    def draw_help(self):
        """Draw help overlay showing controls."""
        # Semi-transparent background
        overlay = pygame.Surface((500, 400))
        overlay.set_alpha(230)
        overlay.fill((20, 20, 20))
        self.screen.blit(overlay, (self.width // 2 - 250, self.height // 2 - 200))

        # Help text
        help_lines = [
            "CONTROLS",
            "",
            "Mouse:",
            "  Left Click + Drag - Pan view",
            "  Scroll Wheel - Zoom in/out",
            "",
            "Keyboard:",
            "  1-9 - Switch visualizations",
            "  C - Cycle color schemes",
            "  + / - - Increase/decrease iterations",
            "  R - Reset view",
            "  S - Save screenshot",
            "  H - Toggle this help",
            "  ESC/Q - Quit",
        ]

        y_offset = self.height // 2 - 180
        for i, line in enumerate(help_lines):
            if i == 0:
                # Title
                text_surface = self.font.render(line, True, (255, 255, 100))
            elif line == "":
                continue
            else:
                text_surface = self.small_font.render(line, True, (255, 255, 255))

            self.screen.blit(text_surface, (self.width // 2 - 230, y_offset))
            y_offset += 25 if line else 10

        pygame.display.flip()

    def save_screenshot(self, filename: str = "fractal_screenshot.png"):
        """
        Save the current frame as an image.

        Args:
            filename: Output filename
        """
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved as {filename}")

    def tick(self) -> int:
        """
        Advance the clock and return delta time.

        Returns:
            Delta time in milliseconds
        """
        return self.clock.tick(self.fps)

    def quit(self):
        """Clean up and quit pygame."""
        pygame.quit()
