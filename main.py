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
    print("Fractal Visualizer")
    print("=" * 60)
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

    # Main event loop
    running = True
    needs_redraw = False

    while running:
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
                needs_redraw = True

        # Cycle color scheme
        if actions['cycle_color']:
            color_scheme_index = (color_scheme_index + 1) % len(COLOR_SCHEMES)
            color_scheme = get_color_scheme(color_scheme_index)
            print(f"Color scheme: {color_scheme.name}")
            needs_redraw = True

        # Save screenshot
        if actions['save']:
            import time
            filename = f"fractal_{int(time.time())}.png"
            renderer.save_screenshot(filename)

        # Redraw if needed
        if actions['redraw']:
            needs_redraw = True

        if needs_redraw:
            print(f"Rendering: {visualization.get_name()} at zoom {visualization.zoom:.2e}...")
            renderer.render_optimized(visualization, color_scheme)
            needs_redraw = False

        # Tick clock
        renderer.tick()

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
