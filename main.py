#!/usr/bin/env python3
"""
Fractal Visualizer - Main Entry Point

A beautiful, interactive fractal visualization system.
"""

import sys
from engine.renderer import Renderer
from engine.color_schemes import get_color_scheme, COLOR_SCHEMES
from ui.controls import Controls
from ui.selector import Selector
from visualizations import VISUALIZATIONS


def main():
    """Main application loop."""
    print("=" * 60)
    print("Fractal Visualizer - GPU Accelerated")
    print("=" * 60)
    print()

    # Detect GPU availability
    try:
        from numba import cuda
        if cuda.is_available():
            gpu_name = cuda.get_current_device().name.decode('utf-8')
            print(f"✓ GPU Detected: {gpu_name}")
            print(f"✓ CUDA cores available for near-instant rendering")
            print(f"✓ Acceleration: ~100-1000x faster than CPU")
        else:
            print("⚠ GPU not detected - using CPU JIT compilation")
            print("  (Still fast, but GPU would be 10-100x faster)")
    except ImportError:
        print("⚠ Numba not installed - using basic Python")
        print("  Install numba for 10-100x speedup")
    print()

    print("Loading...")

    # Initialize components
    renderer = Renderer(width=1200, height=800, title="Fractal Visualizer")
    controls = Controls()
    selector = Selector(VISUALIZATIONS)

    # Get initial visualization and color scheme
    visualization = selector.get_current()
    color_scheme_index = 0
    color_scheme = get_color_scheme(color_scheme_index)

    print(f"Starting with: {visualization.get_name()}")
    print(f"Color scheme: {color_scheme.name}")
    print()
    print("Controls:")
    print("  Mouse: Left click + drag to pan, scroll to zoom")
    print("  Keyboard: H for help, Q to quit")
    print()

    # Initial render
    print("Rendering initial view...")
    renderer.render_optimized(visualization, color_scheme)

    # Main event loop with progressive refinement
    running = True
    needs_redraw = False
    needs_refinement = False

    while running:
        # Get delta time
        delta_time = renderer.tick()

        # Handle input
        actions = controls.handle_events(visualization, renderer)

        # Check for quit
        if actions['quit']:
            running = False
            continue

        # Toggle help
        if actions['toggle_help']:
            if controls.show_help:
                renderer.draw_help()
            else:
                needs_redraw = True

        # Switch visualization
        if actions['switch_viz'] is not None:
            viz_index = actions['switch_viz']
            if viz_index < selector.get_count():
                visualization = selector.switch_to(viz_index)
                print(f"Switched to: {visualization.get_name()}")
                # Clear any ongoing animations
                controls.target_zoom = None
                controls.pan_velocity_x = 0
                controls.pan_velocity_y = 0
                # Clear cache since visualization changed
                renderer.cached_surface = None
                renderer.last_render_state = None
                # Update camera state to prevent false camera_moved detection
                renderer.camera_state = (visualization.center_x, visualization.center_y, visualization.zoom)
                needs_redraw = True
                needs_refinement = False

        # Cycle color scheme
        if actions['cycle_color']:
            color_scheme_index = (color_scheme_index + 1) % len(COLOR_SCHEMES)
            color_scheme = get_color_scheme(color_scheme_index)
            print(f"Color scheme: {color_scheme.name}")
            # Clear cache since colors changed
            renderer.cached_surface = None
            needs_redraw = True

        # Save screenshot
        if actions['save']:
            import time
            filename = f"fractal_{int(time.time())}.png"
            renderer.save_screenshot(filename)

        # Redraw if needed
        if actions['redraw']:
            needs_redraw = True

        # Update animations (smooth zoom and inertial pan)
        animation_active = controls.update_animations(visualization, renderer, delta_time)

        # Check if camera moved (from any source: input or animation)
        camera_moved = renderer.camera_moved(visualization)

        if camera_moved:
            # Camera moved - instantly show transformed cached surface (like Google Maps)
            renderer.render_cached_transformed(visualization, color_scheme)
            needs_refinement = True  # Schedule refinement pass
            needs_redraw = False  # Don't do full redraw, we have the transform

        elif needs_redraw:
            # Needs full redraw (e.g., changed visualization or color scheme)
            renderer.render_optimized(visualization, color_scheme, quality_factor=1.0)
            needs_redraw = False
            needs_refinement = False

        elif needs_refinement and not animation_active and renderer.should_refine(delta_time):
            # Camera still and no animations - refine to full quality in-place
            completed = renderer.render_optimized(visualization, color_scheme, quality_factor=1.0, refining=True)
            if completed:
                needs_refinement = False
            # If cancelled, needs_refinement stays True and will retry later

    # Clean up
    print()
    print("Shutting down...")
    renderer.quit()
    print("Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
