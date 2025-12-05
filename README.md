# Fractal Visualizer

A beautiful, interactive fractal visualization system built with Python and Pygame. Explore the infinite complexity of mathematical patterns with real-time rendering and intuitive controls.

## Features

- **Beautiful Fractals**: Mandelbrot Set, Julia Set, and more
- **Interactive**: Real-time pan, zoom, and parameter adjustment
- **Multiple Color Schemes**: Classic, Psychedelic, Fire, Ocean, Rainbow, Grayscale
- **High Performance**: Optimized rendering with smooth interactions
- **Modular Architecture**: Easy to add new fractals and visualizations

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

## Controls

### Mouse

- **Left Click + Drag**: Pan the view
- **Scroll Wheel Up**: Zoom in (towards mouse cursor)
- **Scroll Wheel Down**: Zoom out (from mouse cursor)
- **Right Click**: Reset view to default

### Keyboard

#### General Controls
- **H**: Toggle help overlay
- **Q** or **ESC**: Quit application
- **R**: Reset view to default

#### Visualization Controls
- **1-9**: Switch between different fractals
- **C**: Cycle through color schemes
- **+** or **=**: Increase iteration count (more detail)
- **-**: Decrease iteration count (faster rendering)

#### Parameter Adjustment (Fractal-specific)
- **Arrow Keys**: Adjust visualization parameters
  - For Julia Set: Modify the complex constant c

#### Screenshot
- **S**: Save current view as PNG image

## Included Fractals

### Mandelbrot Set
The most iconic fractal, discovered by Benoit Mandelbrot. The Mandelbrot set is defined by the iteration z(n+1) = z(n)² + c, where points that don't escape to infinity are part of the set.

- **Default View**: Centered at (-0.5, 0)
- **Infinite Zoom**: Explore self-similar patterns at any scale
- **Classic Beauty**: The boundary contains infinite complexity

### Julia Set
Related to the Mandelbrot set, but with a fixed constant c. Different values of c produce vastly different and beautiful patterns.

- **Default**: Classic spiral pattern
- **Interactive**: Use arrow keys to adjust the complex parameter
- **Variety**: Each small change creates a new unique pattern

## Color Schemes

1. **Classic**: Traditional blue exterior with gradient
2. **Psychedelic**: Vibrant, multi-colored scheme with sine wave patterns
3. **Fire**: Warm gradient from black through red, orange, yellow
4. **Ocean**: Cool blue-cyan-aqua gradient
5. **Rainbow**: Full spectrum HSV color wheel
6. **Grayscale**: Simple black to white gradient

## Project Structure

```
fractals/
├── main.py                 # Entry point and main event loop
├── engine/
│   ├── renderer.py         # Core rendering engine
│   └── color_schemes.py    # Color palette definitions
├── visualizations/
│   ├── base.py            # Base visualization class
│   ├── mandelbrot.py      # Mandelbrot Set implementation
│   └── julia.py           # Julia Set implementation
├── ui/
│   ├── controls.py        # Input handling
│   └── selector.py        # Visualization switching
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── CLAUDE.md              # Development documentation
```

## Adding New Fractals

The system is designed to be easily extensible. To add a new fractal:

1. Create a new file in `visualizations/` (e.g., `burning_ship.py`)
2. Inherit from `BaseVisualization` class
3. Implement required methods:
   - `get_name()`: Return display name
   - `get_default_params()`: Return default parameters
   - `compute(x, y)`: Compute iteration count for a point
4. Register in `visualizations/__init__.py`

Example:

```python
from .base import BaseVisualization

class MyFractal(BaseVisualization):
    def get_name(self) -> str:
        return "My Fractal"

    def get_default_params(self) -> dict:
        return {
            'center_x': 0.0,
            'center_y': 0.0,
            'zoom': 1.0,
            'max_iter': 256,
        }

    def compute(self, x: float, y: float) -> int:
        # Your fractal computation here
        pass
```

## Performance Tips

- **Lower iteration count** for faster rendering while exploring
- **Increase iteration count** when you find an interesting area to see more detail
- **Smaller window size** renders faster
- **NumPy optimization**: The code is ready for NumPy array operations (future enhancement)

## Known Limitations

- Rendering is CPU-bound and single-threaded (GPU acceleration possible future enhancement)
- Very deep zooms may lose precision (Python float64 limits)
- Large window sizes will render slower

## Future Enhancements

Potential additions:
- More fractals (Burning Ship, Sierpinski Triangle, Dragon Curve, etc.)
- GPU acceleration with NumPy/Numba optimization
- Arbitrary precision for deeper zooms
- Animation recording
- Custom color scheme editor
- Preset save/load system
- Multi-threaded rendering

## License

This project is open source and available for educational purposes.

## Credits

- Built with [Pygame](https://www.pygame.org/)
- Inspired by the mathematical beauty of fractals
- Thanks to Benoit Mandelbrot and Gaston Julia for their groundbreaking work

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"
Install dependencies: `pip install -r requirements.txt`

### Slow rendering
- Reduce window size in `main.py`
- Lower iteration count with the `-` key
- Close other applications

### Window not responding
The application is rendering. Large iteration counts can take time. Wait for rendering to complete.

---

**Enjoy exploring the infinite beauty of fractals!**
