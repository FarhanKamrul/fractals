# CLAUDE.md - Fractal Visualization System

## Project Overview

A beautiful, interactive fractal visualization system built with Python. The system displays mathematical equation-based patterns with a focus on fractals, designed to be modular and extensible for adding multiple visualizations.

## Technology Stack

- **Python 3.8+**
- **pygame** - Graphics rendering and user interaction
- **numpy** - Fast mathematical computations
- **numba** (optional) - JIT compilation for performance optimization

**Rationale**: This stack provides simplicity, ease of extension, and excellent real-time rendering performance.

## Project Structure

```
fractals/
├── main.py                    # Entry point, main event loop
├── engine/
│   ├── __init__.py
│   ├── renderer.py           # Core rendering engine
│   └── color_schemes.py      # Color palettes and gradients
├── visualizations/
│   ├── __init__.py
│   ├── base.py              # Base visualization abstract class
│   ├── mandelbrot.py        # Mandelbrot Set implementation
│   ├── julia.py             # Julia Set implementation
│   └── (future: burning_ship.py, sierpinski.py, dragon_curve.py)
├── ui/
│   ├── __init__.py
│   ├── controls.py          # Interactive controls handler
│   └── selector.py          # Visualization selector UI
├── requirements.txt          # Python dependencies
├── README.md                # User documentation
└── CLAUDE.md                # This file - AI assistant guide
```

## Architecture Design

### Core Components

#### 1. Base Visualization Class (`visualizations/base.py`)
- Abstract base class that all visualizations inherit from
- Defines interface: `compute()`, `get_color()`, `handle_input()`
- Manages viewport (zoom, pan, center point)
- Parameter management system

#### 2. Rendering Engine (`engine/renderer.py`)
- Handles pygame window and surface management
- Pixel-by-pixel computation loop
- Coordinate transformation (screen ↔ mathematical plane)
- Performance optimization (dirty region tracking)

#### 3. Color Schemes (`engine/color_schemes.py`)
- Multiple palettes: psychedelic, grayscale, fire, ocean, rainbow
- Smooth gradient interpolation
- Iteration → color mapping

#### 4. UI System (`ui/`)
- **controls.py**: Mouse/keyboard input handling
  - Mouse: Click & drag to pan, scroll to zoom
  - Keyboard: Switch fractals, adjust parameters, toggle help
- **selector.py**: Visualization switcher with live preview

### Data Flow

```
User Input → Controls → Visualization Parameters Update
                              ↓
                     Renderer.compute()
                              ↓
                     For each pixel:
                       - Map screen coords to math plane
                       - Call visualization.compute(x, y)
                       - Get iteration count
                       - Map to color via color_schemes
                              ↓
                     Display to screen
```

## Implementation Plan

### Phase 1: Foundation ✓
- [x] Create project structure
- [x] Set up CLAUDE.md tracking
- [ ] Create requirements.txt
- [ ] Implement base visualization class
- [ ] Implement color schemes module

### Phase 2: Core Engine
- [ ] Implement rendering engine
- [ ] Add coordinate transformation system
- [ ] Implement basic event loop in main.py

### Phase 3: First Fractals
- [ ] Implement Mandelbrot Set
  - Classic black set with colorful exterior
  - Zoom range: 10^-15 or better
- [ ] Implement Julia Set
  - Multiple parameter presets
  - Real-time parameter adjustment

### Phase 4: Interactivity
- [ ] Mouse controls (pan, zoom)
- [ ] Keyboard controls (fractal switching, parameters)
- [ ] On-screen help display
- [ ] FPS counter and iteration display

### Phase 5: Polish
- [ ] README with screenshots
- [ ] Multiple color schemes
- [ ] Save screenshots
- [ ] Testing and optimization

## Key Features

### Interactive Controls

**Mouse:**
- Left click + drag: Pan view
- Scroll wheel: Zoom in/out
- Right click: Reset view

**Keyboard:**
- `1-9`: Switch between fractals
- `C`: Cycle color schemes
- `+/-`: Adjust iteration count
- `Arrow keys`: Fine-tune parameters (fractal-specific)
- `R`: Reset to default view
- `S`: Save screenshot
- `H`: Toggle help overlay
- `ESC/Q`: Quit

### Starting Fractals

1. **Mandelbrot Set**
   - The most iconic fractal
   - Formula: z(n+1) = z(n)² + c
   - Infinite zoom capability

2. **Julia Set**
   - Beautiful variations of Mandelbrot
   - Formula: z(n+1) = z(n)² + c (where c is constant)
   - Multiple parameter presets

### Future Visualizations
- Burning Ship fractal
- Sierpinski Triangle
- Dragon Curve
- Lorenz Attractor
- Custom mathematical patterns

## Development Workflow

### Adding a New Visualization

1. Create new file in `visualizations/` (e.g., `burning_ship.py`)
2. Inherit from `BaseVisualization`
3. Implement required methods:
   ```python
   def compute(self, x, y) -> int  # Returns iteration count
   def get_name(self) -> str
   def get_default_params(self) -> dict
   ```
4. Register in `visualizations/__init__.py`
5. Add keyboard shortcut in `ui/controls.py`

### Code Style
- Follow PEP 8
- Type hints for function signatures
- Docstrings for classes and complex functions
- Keep visualization logic separate from rendering

### Performance Considerations
- Use numpy arrays for batch pixel computation
- Consider numba @jit decorators for hot loops
- Implement dirty region tracking to avoid full redraws
- Target 30+ FPS for smooth interaction

## Testing

### Manual Testing Checklist
- [ ] All fractals render correctly
- [ ] Zoom maintains center point
- [ ] Pan works smoothly
- [ ] Color schemes apply correctly
- [ ] Keyboard shortcuts work
- [ ] No crashes on edge cases (extreme zoom, window resize)
- [ ] Performance acceptable (30+ FPS at 1080p)

### Future: Automated Tests
- Unit tests for mathematical computations
- Visual regression tests for fractal rendering
- Performance benchmarks

## Current Status

**Branch**: `claude/claude-md-mitd6ci5pldckssw-019dai4LnW9Gct7W6vt5xmeb`

**Progress**: Initial setup phase

**Next Steps**:
1. Create project structure
2. Implement base classes
3. Build rendering engine
4. Implement first fractal (Mandelbrot)

## Dependencies

### Required
- pygame: Graphics and UI
- numpy: Mathematical operations

### Optional
- numba: Performance optimization
- Pillow: Screenshot saving (alternative to pygame)

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Design Principles

1. **Simplicity**: One command to run, intuitive controls
2. **Modularity**: Each visualization is self-contained
3. **Extensibility**: Easy to add new fractals and features
4. **Performance**: Real-time interaction at high resolution
5. **Beauty**: Rich colors, smooth gradients, high detail

## Notes for AI Assistants

- Always update this file when making architectural changes
- Keep the project structure clean and modular
- Prioritize code readability and maintainability
- Test interactivity after each major change
- Document any performance optimizations
- Keep mathematical accuracy high (use appropriate data types)

---

Last Updated: 2025-12-05
