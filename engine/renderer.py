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
        self.cached_surface = None  # Cache for instant zoom/pan

        # Progressive refinement state
        self.camera_state = None  # (center_x, center_y, zoom)
        self.last_render_state = None  # State when surface was last rendered
        self.camera_still_time = 0  # Time camera has been still (ms)
        self.camera_still_threshold = 150  # ms before starting refinement
        self.current_quality = 1.0  # Current rendering quality (0.3 = preview, 1.0 = full)
        self.use_progressive_refinement = True
        self.is_refining = False  # Track if currently refining

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

    def camera_moved(self, visualization) -> bool:
        """
        Check if camera has moved since last check.

        Args:
            visualization: Visualization to check camera state

        Returns:
            True if camera moved, False if still
        """
        current_state = (visualization.center_x, visualization.center_y, visualization.zoom)

        if self.camera_state != current_state:
            self.camera_state = current_state
            self.camera_still_time = 0
            return True

        return False

    def should_refine(self, delta_time: int) -> bool:
        """
        Check if we should perform refinement pass.

        Args:
            delta_time: Time elapsed since last frame (ms)

        Returns:
            True if camera has been still long enough
        """
        if not self.use_progressive_refinement or self.is_refining:
            return False

        self.camera_still_time += delta_time
        return self.camera_still_time >= self.camera_still_threshold

    def render_cached_transformed(self, visualization, color_scheme: ColorScheme, show_info: bool = True):
        """
        Instantly display cached surface transformed for new camera position.
        This provides smooth zoom/pan like Google Maps.

        Args:
            visualization: Current visualization
            color_scheme: Current color scheme
            show_info: Whether to show info overlay
        """
        if self.cached_surface is None or self.last_render_state is None:
            # No cache available, render from scratch
            self.render_optimized(visualization, color_scheme, show_info, quality_factor=0.3)
            return

        # Get camera transform
        old_cx, old_cy, old_zoom = self.last_render_state
        new_cx, new_cy, new_zoom = visualization.center_x, visualization.center_y, visualization.zoom

        # Calculate zoom factor and offset
        zoom_factor = new_zoom / old_zoom

        # Calculate pixel offset due to pan
        aspect = self.width / self.height
        dx_world = new_cx - old_cx
        dy_world = new_cy - old_cy

        # Convert world space delta to screen space
        dx_screen = -dx_world * old_zoom * self.width / (2 * aspect)
        dy_screen = -dy_world * old_zoom * self.height / 2

        # Scale and transform cached surface
        if zoom_factor != 1.0:
            # Zoom: scale around center
            new_size = (int(self.width * zoom_factor), int(self.height * zoom_factor))
            scaled = pygame.transform.smoothscale(self.cached_surface, new_size)

            # Center the scaled surface
            offset_x = (self.width - new_size[0]) // 2 + int(dx_screen * zoom_factor)
            offset_y = (self.height - new_size[1]) // 2 + int(dy_screen * zoom_factor)
        else:
            # Just pan
            scaled = self.cached_surface
            offset_x = int(dx_screen)
            offset_y = int(dy_screen)

        # Clear screen and blit transformed surface
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (offset_x, offset_y))

        # Draw info overlay
        if show_info:
            self.draw_info(visualization, color_scheme, quality=0)  # 0 = transforming cached

        pygame.display.flip()

    def render_optimized(self, visualization, color_scheme: ColorScheme,
                        show_info: bool = True, chunk_size: int = 64,
                        quality_factor: float = 1.0, refining: bool = False):
        """
        Optimized rendering with numpy arrays, chunked updates, and progressive refinement.

        Args:
            visualization: BaseVisualization instance to render
            color_scheme: ColorScheme instance for coloring
            show_info: Whether to display info overlay
            chunk_size: Number of rows to render per frame
            quality_factor: Rendering quality (0.3 = fast preview, 1.0 = full detail)
            refining: If True, renders in-place for refinement
        """
        # Mark as refining if doing refinement pass
        if refining:
            self.is_refining = True

        # Create coordinate grids
        aspect = self.width / self.height

        # Set iteration count based on quality factor
        original_max_iter = visualization.max_iter
        visualization.max_iter = visualization.calculate_adaptive_iterations(quality_factor)

        # Render in chunks to maintain responsiveness
        for start_y in range(0, self.height, chunk_size):
            end_y = min(start_y + chunk_size, self.height)
            chunk_height = end_y - start_y

            # Create meshgrid for this chunk
            x_indices = np.arange(self.width)
            y_indices = np.arange(start_y, end_y)
            x_grid, y_grid = np.meshgrid(x_indices, y_indices)

            # Convert screen coordinates to world coordinates (vectorized)
            norm_x = (x_grid / self.width) * 2 - 1
            norm_y = (y_grid / self.height) * 2 - 1

            world_x = visualization.center_x + (norm_x * aspect) / visualization.zoom
            world_y = visualization.center_y + norm_y / visualization.zoom

            # Compute fractal for all pixels in chunk (vectorized)
            iterations = self._compute_fractal_vectorized(
                world_x, world_y, visualization
            )

            # Convert iterations to colors (vectorized)
            colors = self._get_colors_vectorized(
                iterations, visualization.max_iter, color_scheme
            )

            # Blit chunk to surface using surfarray (very fast)
            chunk_surface = pygame.surfarray.make_surface(
                np.transpose(colors, (1, 0, 2))
            )
            self.surface.blit(chunk_surface, (0, start_y))

            # Update display with partial progress
            self.screen.blit(self.surface, (0, 0))
            if show_info:
                quality_percent = int(quality_factor * 100)
                self.draw_info(visualization, color_scheme, rendering=True,
                             progress=end_y / self.height, quality=quality_percent)
            pygame.display.flip()

        # Restore original max_iter
        visualization.max_iter = original_max_iter

        # Cache the rendered surface and state for smooth zoom/pan
        if quality_factor >= 0.9:  # Only cache high quality renders
            self.cached_surface = self.surface.copy()
            self.last_render_state = (visualization.center_x, visualization.center_y, visualization.zoom)

        # Final update without progress bar
        if show_info:
            quality_percent = int(quality_factor * 100)
            self.draw_info(visualization, color_scheme, quality=quality_percent)
            pygame.display.flip()

        # Clear refining flag
        self.is_refining = False

    def _compute_fractal_vectorized(self, world_x, world_y, visualization):
        """
        Compute fractal iterations for a grid of points (vectorized).

        Automatically selects best available computation method:
        1. GPU (CUDA) if available - fastest
        2. CPU with JIT compilation - fast
        3. Pure Python - slow fallback

        Args:
            world_x: 2D array of x coordinates
            world_y: 2D array of y coordinates
            visualization: Visualization instance

        Returns:
            2D array of iteration counts
        """
        shape = world_x.shape

        # Flatten arrays for processing
        x_flat = world_x.flatten()
        y_flat = world_y.flatten()

        # Try GPU computation first (fastest)
        if hasattr(visualization, 'compute_gpu'):
            iterations_flat = visualization.compute_gpu(x_flat, y_flat)
            iterations = iterations_flat.reshape(shape)
        # Fall back to CPU JIT (fast)
        elif hasattr(visualization, 'compute_array'):
            iterations_flat = visualization.compute_array(x_flat, y_flat)
            iterations = iterations_flat.reshape(shape)
        # Last resort: pure Python (slow)
        else:
            iterations = np.zeros(shape, dtype=np.int32)
            for i in range(len(x_flat)):
                iterations.flat[i] = visualization.compute(x_flat[i], y_flat[i])

        return iterations

    def _get_colors_vectorized(self, iterations, max_iter, color_scheme):
        """
        Convert iteration counts to RGB colors (vectorized).

        Args:
            iterations: 2D array of iteration counts
            max_iter: Maximum iteration count
            color_scheme: ColorScheme instance

        Returns:
            3D array of RGB values (height, width, 3)
        """
        shape = iterations.shape
        colors = np.zeros((*shape, 3), dtype=np.uint8)

        # Flatten for processing
        iter_flat = iterations.flatten()

        # Get colors for each iteration count
        for i in range(len(iter_flat)):
            color = color_scheme.get_color(iter_flat[i], max_iter)
            colors.reshape(-1, 3)[i] = color

        return colors

    def draw_info(self, visualization, color_scheme: ColorScheme,
                 rendering: bool = False, progress: float = 1.0, quality: int = 100):
        """
        Draw information overlay on screen.

        Args:
            visualization: Current visualization
            color_scheme: Current color scheme
            rendering: Whether currently rendering
            progress: Rendering progress (0.0 to 1.0)
            quality: Rendering quality percentage (30 = preview, 100 = full)
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

        # FPS counter and quality
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.small_font.render(fps_text, True, (200, 200, 200))
        self.screen.blit(fps_surface, (10, 55))

        # Quality indicator (green if 100%, yellow if preview, cyan if cached transform)
        if quality == 0:
            quality_color = (0, 255, 255)  # Cyan for cached transform
            quality_text = "Quality: Cached"
        elif quality >= 100:
            quality_color = (0, 255, 0)  # Green for full quality
            quality_text = f"Quality: {quality}%"
        else:
            quality_color = (255, 200, 0)  # Yellow for preview
            quality_text = f"Quality: {quality}%"

        quality_surface = self.small_font.render(quality_text, True, quality_color)
        self.screen.blit(quality_surface, (120, 55))

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
