"""
User input controls for fractal visualization.

Handles mouse and keyboard input for panning, zooming, and parameter adjustment.
Implements smooth animations for Google Maps-style interaction.
"""

import pygame
import math
from typing import Optional, Tuple


class Controls:
    """
    Handles all user input for the fractal visualizer.
    Includes smooth zoom animation and inertial panning.
    """

    def __init__(self):
        """Initialize controls."""
        self.dragging = False
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.show_help = False

        # Smooth zoom animation state
        self.target_zoom = None  # Target zoom level for animation
        self.zoom_velocity = 0.0  # Current zoom velocity
        self.zoom_mouse_world = None  # World position to zoom towards
        self.zoom_smoothing = 0.15  # Smoothing factor (lower = smoother but slower)

        # Inertial panning state
        self.pan_velocity_x = 0.0  # World-space velocity
        self.pan_velocity_y = 0.0
        self.pan_friction = 0.92  # Velocity decay per frame (lower = more friction)
        self.pan_min_velocity = 0.00001  # Stop threshold
        self.last_drag_time = 0  # For velocity calculation
        self.velocity_samples = []  # Recent velocity samples for smoothing

    def update_animations(self, visualization, renderer, delta_time: float) -> bool:
        """
        Update smooth zoom and inertial panning animations.

        Args:
            visualization: Current visualization
            renderer: Renderer instance
            delta_time: Time since last frame in milliseconds

        Returns:
            True if any animation is active and view changed
        """
        changed = False
        dt = delta_time / 1000.0  # Convert to seconds

        # Update smooth zoom
        if self.target_zoom is not None:
            old_zoom = visualization.zoom
            zoom_diff = self.target_zoom - visualization.zoom

            # Check if we're close enough to snap
            if abs(zoom_diff) < visualization.zoom * 0.001:
                visualization.zoom = self.target_zoom
                self.target_zoom = None
            else:
                # Smooth exponential interpolation
                visualization.zoom += zoom_diff * self.zoom_smoothing * min(delta_time / 16.0, 3.0)

                # Keep zoom centered on mouse position
                if self.zoom_mouse_world is not None:
                    zoom_factor = visualization.zoom / old_zoom
                    world_x, world_y = self.zoom_mouse_world
                    visualization.center_x = world_x + (visualization.center_x - world_x) / zoom_factor
                    visualization.center_y = world_y + (visualization.center_y - world_y) / zoom_factor

            # Update max iterations for new zoom
            visualization.max_iter = visualization.calculate_adaptive_iterations()
            changed = True

        # Update inertial panning (only when not dragging)
        if not self.dragging and (abs(self.pan_velocity_x) > self.pan_min_velocity or
                                   abs(self.pan_velocity_y) > self.pan_min_velocity):
            # Apply velocity
            visualization.center_x += self.pan_velocity_x * dt * 60  # Normalize to ~60fps
            visualization.center_y += self.pan_velocity_y * dt * 60

            # Apply friction
            self.pan_velocity_x *= self.pan_friction
            self.pan_velocity_y *= self.pan_friction

            # Stop if below threshold
            if abs(self.pan_velocity_x) < self.pan_min_velocity:
                self.pan_velocity_x = 0.0
            if abs(self.pan_velocity_y) < self.pan_min_velocity:
                self.pan_velocity_y = 0.0

            changed = True

        return changed

    def is_animating(self) -> bool:
        """Check if any animation is in progress."""
        return (self.target_zoom is not None or
                abs(self.pan_velocity_x) > self.pan_min_velocity or
                abs(self.pan_velocity_y) > self.pan_min_velocity)

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
            self.last_drag_time = pygame.time.get_ticks()
            self.velocity_samples = []
            # Stop any ongoing inertial motion
            self.pan_velocity_x = 0
            self.pan_velocity_y = 0

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

            # Set target for smooth zoom animation (smaller factor for smoother feel)
            base_zoom = self.target_zoom if self.target_zoom else visualization.zoom
            self.target_zoom = base_zoom * 1.25  # Smaller increment for smoother feel
            self.zoom_mouse_world = (world_x, world_y)

            actions['redraw'] = True

        elif event.button == 5:  # Scroll down (zoom out)
            # Get mouse position in world coordinates
            mouse_x, mouse_y = event.pos
            world_x, world_y = visualization.screen_to_world(
                mouse_x, mouse_y, renderer.width, renderer.height
            )

            # Set target for smooth zoom animation
            base_zoom = self.target_zoom if self.target_zoom else visualization.zoom
            self.target_zoom = base_zoom / 1.25  # Smaller increment for smoother feel
            self.zoom_mouse_world = (world_x, world_y)

            actions['redraw'] = True

        return actions

    def handle_mouse_up(self, event):
        """
        Handle mouse button release.

        Args:
            event: Pygame mouse event
        """
        if event.button == 1:  # Left click
            # Calculate final velocity from recent samples for inertial panning
            if self.velocity_samples:
                # Average the recent velocity samples
                avg_vx = sum(v[0] for v in self.velocity_samples) / len(self.velocity_samples)
                avg_vy = sum(v[1] for v in self.velocity_samples) / len(self.velocity_samples)

                # Only apply inertia if we have significant velocity
                if abs(avg_vx) > 0.0001 or abs(avg_vy) > 0.0001:
                    self.pan_velocity_x = avg_vx
                    self.pan_velocity_y = avg_vy

            self.dragging = False
            self.last_mouse_pos = None
            self.velocity_samples = []

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

            # Track velocity for inertial panning
            current_time = pygame.time.get_ticks()
            if self.last_drag_time > 0:
                dt = (current_time - self.last_drag_time) / 1000.0  # seconds
                if dt > 0:
                    vx = world_dx / dt / 60  # Normalize to per-frame velocity
                    vy = world_dy / dt / 60
                    self.velocity_samples.append((vx, vy))
                    # Keep only recent samples (last 5)
                    if len(self.velocity_samples) > 5:
                        self.velocity_samples.pop(0)

            self.last_drag_time = current_time
            self.last_mouse_pos = event.pos
            actions['redraw'] = True

            # Stop any ongoing inertial motion when user starts dragging
            self.pan_velocity_x = 0
            self.pan_velocity_y = 0

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
