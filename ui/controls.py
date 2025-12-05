"""
User input controls for fractal visualization.

Handles mouse and keyboard input for panning, zooming, and parameter adjustment.
"""

import pygame
from typing import Optional, Tuple


class Controls:
    """
    Handles all user input for the fractal visualizer.
    """

    def __init__(self):
        """Initialize controls."""
        self.dragging = False
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.show_help = False

    def handle_events(self, visualization, renderer) -> dict:
        """
        Process pygame events and return actions.

        Args:
            visualization: Current visualization instance
            renderer: Renderer instance

        Returns:
            Dictionary with action flags:
            - 'quit': Boolean
            - 'redraw': Boolean
            - 'switch_viz': Optional visualization index
            - 'cycle_color': Boolean
            - 'save': Boolean
            - 'toggle_help': Boolean
        """
        actions = {
            'quit': False,
            'redraw': False,
            'switch_viz': None,
            'cycle_color': False,
            'save': False,
            'toggle_help': False,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions['quit'] = True

            elif event.type == pygame.KEYDOWN:
                key_actions = self.handle_keydown(event, visualization)
                for key, value in key_actions.items():
                    if value:
                        actions[key] = value

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_actions = self.handle_mouse_down(event, visualization, renderer)
                for key, value in mouse_actions.items():
                    if value:
                        actions[key] = value

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

            elif event.type == pygame.MOUSEMOTION:
                mouse_actions = self.handle_mouse_motion(event, visualization, renderer)
                if mouse_actions.get('redraw'):
                    actions['redraw'] = True

        return actions

    def handle_keydown(self, event, visualization) -> dict:
        """
        Handle keyboard input.

        Args:
            event: Pygame keyboard event
            visualization: Current visualization

        Returns:
            Dictionary of action flags
        """
        actions = {
            'quit': False,
            'redraw': False,
            'switch_viz': None,
            'cycle_color': False,
            'save': False,
            'toggle_help': False,
        }

        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            actions['quit'] = True

        elif event.key == pygame.K_r:
            # Reset view
            visualization.reset_view()
            actions['redraw'] = True

        elif event.key == pygame.K_c:
            # Cycle color scheme
            actions['cycle_color'] = True

        elif event.key == pygame.K_s:
            # Save screenshot
            actions['save'] = True

        elif event.key == pygame.K_h:
            # Toggle help
            self.show_help = not self.show_help
            actions['toggle_help'] = True

        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
            # Increase iterations
            visualization.max_iter = int(visualization.max_iter * 1.5)
            visualization.set_param('max_iter', visualization.max_iter)
            actions['redraw'] = True

        elif event.key == pygame.K_MINUS:
            # Decrease iterations
            visualization.max_iter = max(32, int(visualization.max_iter / 1.5))
            visualization.set_param('max_iter', visualization.max_iter)
            actions['redraw'] = True

        # Number keys for switching visualizations
        elif event.key in range(pygame.K_1, pygame.K_9 + 1):
            viz_index = event.key - pygame.K_1
            actions['switch_viz'] = viz_index

        # Arrow keys for parameter adjustment (visualization-specific)
        elif event.key == pygame.K_LEFT:
            self.adjust_viz_param(visualization, 'left')
            actions['redraw'] = True

        elif event.key == pygame.K_RIGHT:
            self.adjust_viz_param(visualization, 'right')
            actions['redraw'] = True

        elif event.key == pygame.K_UP:
            self.adjust_viz_param(visualization, 'up')
            actions['redraw'] = True

        elif event.key == pygame.K_DOWN:
            self.adjust_viz_param(visualization, 'down')
            actions['redraw'] = True

        return actions

    def handle_mouse_down(self, event, visualization, renderer) -> dict:
        """
        Handle mouse button press.

        Args:
            event: Pygame mouse event
            visualization: Current visualization
            renderer: Renderer instance

        Returns:
            Dictionary of action flags
        """
        actions = {'redraw': False}

        if event.button == 1:  # Left click
            self.dragging = True
            self.last_mouse_pos = event.pos

        elif event.button == 3:  # Right click
            # Reset view
            visualization.reset_view()
            actions['redraw'] = True

        elif event.button == 4:  # Scroll up (zoom in)
            # Get mouse position in world coordinates
            mouse_x, mouse_y = event.pos
            world_x, world_y = visualization.screen_to_world(
                mouse_x, mouse_y, renderer.width, renderer.height
            )

            # Zoom in
            old_zoom = visualization.zoom
            visualization.zoom_in(1.5)

            # Adjust center to zoom towards mouse position
            zoom_factor = visualization.zoom / old_zoom
            visualization.center_x = world_x + (visualization.center_x - world_x) / zoom_factor
            visualization.center_y = world_y + (visualization.center_y - world_y) / zoom_factor

            actions['redraw'] = True

        elif event.button == 5:  # Scroll down (zoom out)
            # Get mouse position in world coordinates
            mouse_x, mouse_y = event.pos
            world_x, world_y = visualization.screen_to_world(
                mouse_x, mouse_y, renderer.width, renderer.height
            )

            # Zoom out
            old_zoom = visualization.zoom
            visualization.zoom_out(1.5)

            # Adjust center to zoom from mouse position
            zoom_factor = visualization.zoom / old_zoom
            visualization.center_x = world_x + (visualization.center_x - world_x) / zoom_factor
            visualization.center_y = world_y + (visualization.center_y - world_y) / zoom_factor

            actions['redraw'] = True

        return actions

    def handle_mouse_up(self, event):
        """
        Handle mouse button release.

        Args:
            event: Pygame mouse event
        """
        if event.button == 1:  # Left click
            self.dragging = False
            self.last_mouse_pos = None

    def handle_mouse_motion(self, event, visualization, renderer) -> dict:
        """
        Handle mouse movement.

        Args:
            event: Pygame mouse event
            visualization: Current visualization
            renderer: Renderer instance

        Returns:
            Dictionary of action flags
        """
        actions = {'redraw': False}

        if self.dragging and self.last_mouse_pos:
            # Calculate drag delta
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]

            # Convert to world space and pan
            aspect = renderer.width / renderer.height
            world_dx = -(dx * 2 * aspect) / (renderer.width * visualization.zoom)
            world_dy = -(dy * 2) / (renderer.height * visualization.zoom)

            visualization.center_x += world_dx
            visualization.center_y += world_dy

            self.last_mouse_pos = event.pos
            actions['redraw'] = True

        return actions

    def adjust_viz_param(self, visualization, direction: str):
        """
        Adjust visualization-specific parameters.

        Args:
            visualization: Current visualization
            direction: 'left', 'right', 'up', or 'down'
        """
        # Check if this is a Julia set
        viz_name = visualization.get_name()

        if "Julia" in viz_name:
            # Adjust Julia set constant c
            c_real = visualization.get_param('c_real', 0.0)
            c_imag = visualization.get_param('c_imag', 0.0)

            step = 0.01

            if direction == 'left':
                c_real -= step
            elif direction == 'right':
                c_real += step
            elif direction == 'up':
                c_imag += step
            elif direction == 'down':
                c_imag -= step

            visualization.set_c(c_real, c_imag)
