# CLAUDE.md - Fractal Visualization System

## Project Overview

A beautiful, interactive fractal visualization system built with Python. The system displays mathematical equation-based patterns with a focus on fractals, designed to be modular and extensible for adding multiple visualizations.

## Technology Stack

- **Python 3.8+**
- **pygame** - Graphics rendering and user interaction
- **numpy** - Fast mathematical computations
- **numba** - JIT compilation and CUDA GPU acceleration

**Rationale**: This stack provides simplicity, ease of extension, and excellent real-time rendering performance. GPU acceleration delivers 100-1000x speedup for near-instantaneous rendering.

## Project Structure

```
fractals/
├── main.py                    # Entry point, main event loop with progressive refinement
├── engine/
│   ├── __init__.py
│   ├── renderer.py           # Core rendering engine with GPU support
│   └── color_schemes.py      # Color palettes and gradients
├── visualizations/
│   ├── __init__.py
│   ├── base.py              # Base visualization with adaptive iteration scaling
│   ├── mandelbrot.py        # Mandelbrot Set (GPU accelerated)
│   ├── julia.py             # Julia Set (GPU accelerated)
│   ├── burning_ship.py      # Burning Ship fractal (GPU accelerated)
│   └── (future: sierpinski.py, dragon_curve.py, lorenz.py)
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
- Defines interface: `compute()`, `compute_array()`, `compute_gpu()`
- Manages viewport (zoom, pan, center point)
- **Adaptive iteration scaling**: Logarithmic formula `maxIter = a + b·log(zoom)`
  - Minimum 200 iterations at overview level
  - Scales up to 10,000 iterations at deep zoom
- Parameter management system

#### 2. Rendering Engine (`engine/renderer.py`)
- GPU-accelerated rendering with CUDA support
- Smart computation method selection: GPU → CPU JIT → Pure Python
- **Progressive refinement** (Google Maps-style):
  - Instant zoom/pan by transforming cached surface
  - Automatic high-quality refinement when camera stops
  - No visible rendering boundaries during refinement
- Coordinate transformation (screen ↔ mathematical plane)
- Numpy array-based bulk pixel operations (10-100x faster than pixel-by-pixel)

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

### Phase 1: Foundation ✅
- [x] Create project structure
- [x] Set up CLAUDE.md tracking
- [x] Create requirements.txt
- [x] Implement base visualization class
- [x] Implement color schemes module

### Phase 2: Core Engine ✅
- [x] Implement rendering engine
- [x] Add coordinate transformation system
- [x] Implement basic event loop in main.py
- [x] GPU acceleration with CUDA
- [x] Numpy-based bulk pixel operations

### Phase 3: First Fractals ✅
- [x] Implement Mandelbrot Set
  - GPU-accelerated computation
  - Infinite zoom with adaptive iterations
- [x] Implement Julia Set
  - Multiple parameter presets
  - Real-time parameter adjustment with arrow keys
- [x] Implement Burning Ship fractal
  - GPU-accelerated
  - Unique asymmetric fractal shape

### Phase 4: Interactivity ✅
- [x] Mouse controls (pan with drag, zoom with scroll)
- [x] Keyboard controls (fractal switching, parameters)
- [x] On-screen help display
- [x] Info overlay with FPS and iteration count
- [x] Progressive refinement (Google Maps-style)

### Phase 5: Polish ✅
- [x] Multiple color schemes (6 schemes)
- [x] Save screenshots (S key)
- [x] Adaptive iteration scaling
- [x] Performance optimization (GPU + JIT)
- [x] Smooth zoom/pan with cached transformation

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

### Available Fractals

1. **Mandelbrot Set** (Press `1`)
   - The most iconic fractal
   - Formula: z(n+1) = z(n)² + c
   - Infinite zoom capability with adaptive iterations
   - GPU-accelerated for instant rendering

2. **Julia Set** (Press `2`)
   - Beautiful variations of Mandelbrot
   - Formula: z(n+1) = z(n)² + c (where c is constant)
   - Adjust c parameter with arrow keys
   - GPU-accelerated

3. **Burning Ship** (Press `3`)
   - Unique asymmetric fractal
   - Formula: z(n+1) = (|Re(z)| + i|Im(z)|)² + c
   - Creates ship-like appearance
   - GPU-accelerated

### Future Visualizations
- Sierpinski Triangle
- Dragon Curve
- Lorenz Attractor
- Newton Fractal
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
- **GPU acceleration**: CUDA kernels for 100-1000x speedup
- **CPU fallback**: Numba JIT compilation for 10-100x speedup
- **Numpy vectorization**: Bulk pixel operations instead of loops
- **Progressive refinement**: Low-iteration preview, high-iteration refinement
- **Adaptive iterations**: Scale with zoom depth (200-10,000 iterations)
- **Cached surface transformation**: Instant zoom/pan feedback
- **Performance**: Achieves near-instantaneous rendering with GPU

## Testing

### Manual Testing Checklist
- [x] All fractals render correctly (Mandelbrot, Julia, Burning Ship)
- [x] Zoom maintains center point
- [x] Pan works smoothly with cached transformation
- [x] Color schemes apply correctly (6 schemes)
- [x] Keyboard shortcuts work (1-3 for fractals, C for colors, etc.)
- [x] Visualization switching works bidirectionally
- [x] Progressive refinement is seamless (no visible boundaries)
- [x] GPU acceleration works when available
- [x] Performance excellent (near-instant with GPU, <1s without)

### Future: Automated Tests
- Unit tests for mathematical computations
- Visual regression tests for fractal rendering
- Performance benchmarks

## Current Status

**Branch**: `claude/claude-md-mitd6ci5pldckssw-019dai4LnW9Gct7W6vt5xmeb`

**Progress**: ✅ **All phases complete** - Fully functional GPU-accelerated fractal visualizer

**Implemented Features**:
- ✅ Three fractals: Mandelbrot, Julia, Burning Ship
- ✅ GPU acceleration with CUDA (100-1000x speedup)
- ✅ Progressive refinement (Google Maps-style smooth zoom/pan)
- ✅ Adaptive iteration scaling (200-10,000 iterations based on zoom)
- ✅ Six color schemes
- ✅ Interactive controls (mouse + keyboard)
- ✅ Screenshot saving
- ✅ Real-time parameter adjustment

**Recent Updates** (2025-12-06):
- Fixed visualization switching bug (Julia → Mandelbrot)
- Doubled iteration counts (512 base, 200-10,000 adaptive range)
- Added Burning Ship fractal with GPU support
- Eliminated visible rendering boundaries during refinement
- Fixed zoom revert bug in progressive refinement

**Future Enhancements**:
- Additional fractals (Sierpinski, Dragon Curve, Newton)
- Video recording of zoom sequences
- Custom color scheme editor
- Saved location bookmarks

## Dependencies

### Required
- **pygame** >= 2.5.0 - Graphics and UI
- **numpy** >= 1.24.0 - Mathematical operations and array processing
- **numba** >= 0.57.0 - JIT compilation and CUDA GPU acceleration

### Optional
- **CUDA Toolkit** - For GPU acceleration (100-1000x speedup)
  - Works without GPU, falling back to CPU JIT (still 10-100x faster than pure Python)

## Deployment Options

### 1. Local Installation (Recommended)
Best for GPU acceleration and full performance.

```bash
# Clone repository
git clone <repo-url>
cd fractals

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### 2. PyInstaller (Standalone Executable)
Package as single executable for distribution.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
Note: GPU support may require additional bundling of CUDA libraries.

### 3. Docker Container
Consistent environment, good for servers.

```dockerfile
FROM python:3.9
RUN apt-get update && apt-get install -y libsdl2-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```
For GPU: Use nvidia-docker with `--gpus all` flag.

### 4. Limitations
- **Web deployment**: Not recommended - pygame has limited web support and no CUDA in browser
- For web version, would need complete rewrite using WebGL/Three.js

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Controls
# - Mouse: Left drag to pan, scroll to zoom
# - Keyboard: 1-3 to switch fractals, C to change colors, H for help
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

Last Updated: 2025-12-06

## Version History

### v1.0 (2025-12-06)
- Complete GPU-accelerated fractal visualizer
- Three fractals: Mandelbrot, Julia, Burning Ship
- Progressive refinement with Google Maps-style smooth interaction
- Adaptive iteration scaling (200-10,000 iterations)
- Six color schemes
- Full interactivity: pan, zoom, parameter adjustment
- Screenshot saving
- 100-1000x GPU speedup with CUDA

### Initial Release (2025-12-05)
- Project structure and planning
- Basic architecture design
