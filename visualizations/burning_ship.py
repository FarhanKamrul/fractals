"""
Burning Ship Fractal

A beautiful variation of the Mandelbrot set that uses absolute values,
creating a unique ship-like appearance.
"""

import numpy as np
from numba import jit, cuda
from .base import BaseVisualization


@jit(nopython=True)
def burning_ship_compute_jit(cx, cy, max_iter, escape_radius_sq):
    """
    JIT-compiled Burning Ship computation for a single point.

    The Burning Ship formula:
    z(n+1) = (|Re(z(n))| + i|Im(z(n))|)^2 + c

    Args:
        cx: Real component of c
        cy: Imaginary component of c
        max_iter: Maximum iterations
        escape_radius_sq: Escape radius squared

    Returns:
        Number of iterations before escape
    """
    zx = 0.0
    zy = 0.0

    for iteration in range(max_iter):
        # Take absolute values (this is what makes the Burning Ship unique!)
        zx_abs = abs(zx)
        zy_abs = abs(zy)

        # Check for escape
        if zx_abs * zx_abs + zy_abs * zy_abs > escape_radius_sq:
            return iteration

        # Burning Ship formula: z = (|zx| + i|zy|)^2 + c
        zx_new = zx_abs * zx_abs - zy_abs * zy_abs + cx
        zy = 2.0 * zx_abs * zy_abs + cy
        zx = zx_new

    return max_iter


@jit(nopython=True, parallel=True)
def burning_ship_compute_array(x_array, y_array, max_iter, escape_radius_sq):
    """
    JIT-compiled Burning Ship computation for array of points.

    Args:
        x_array: Flattened array of real components
        y_array: Flattened array of imaginary components
        max_iter: Maximum iterations
        escape_radius_sq: Escape radius squared

    Returns:
        Array of iteration counts
    """
    result = np.empty_like(x_array, dtype=np.int32)
    for i in range(x_array.size):
        result[i] = burning_ship_compute_jit(
            x_array[i], y_array[i], max_iter, escape_radius_sq
        )
    return result


# GPU CUDA implementation
try:
    @cuda.jit
    def burning_ship_kernel_cuda(x_array, y_array, result, max_iter, escape_radius_sq):
        """
        CUDA kernel for Burning Ship computation.

        Each thread computes one pixel.

        Args:
            x_array: Array of real components
            y_array: Array of imaginary components
            result: Output array for iteration counts
            max_iter: Maximum iterations
            escape_radius_sq: Escape radius squared
        """
        idx = cuda.grid(1)

        if idx < x_array.size:
            cx = x_array[idx]
            cy = y_array[idx]
            zx = 0.0
            zy = 0.0
            iteration = 0

            while iteration < max_iter:
                # Take absolute values
                zx_abs = abs(zx)
                zy_abs = abs(zy)

                # Check for escape
                if zx_abs * zx_abs + zy_abs * zy_abs > escape_radius_sq:
                    break

                # Burning Ship formula
                zx_new = zx_abs * zx_abs - zy_abs * zy_abs + cx
                zy = 2.0 * zx_abs * zy_abs + cy
                zx = zx_new
                iteration += 1

            result[idx] = iteration

    def burning_ship_compute_gpu(x_array, y_array, max_iter, escape_radius_sq):
        """
        GPU-accelerated Burning Ship computation.

        Args:
            x_array: Flattened array of real components
            y_array: Flattened array of imaginary components
            max_iter: Maximum iterations
            escape_radius_sq: Escape radius squared

        Returns:
            Array of iteration counts
        """
        # Transfer data to GPU
        d_x = cuda.to_device(x_array)
        d_y = cuda.to_device(y_array)
        d_result = cuda.device_array(x_array.size, dtype=np.int32)

        # Configure grid
        threads_per_block = 256
        blocks = (x_array.size + threads_per_block - 1) // threads_per_block

        # Launch kernel
        burning_ship_kernel_cuda[blocks, threads_per_block](
            d_x, d_y, d_result, max_iter, escape_radius_sq
        )

        # Copy result back to CPU
        return d_result.copy_to_host()

except (ImportError, AttributeError):
    # No CUDA support - fallback to CPU
    def burning_ship_compute_gpu(x_array, y_array, max_iter, escape_radius_sq):
        return burning_ship_compute_array(x_array, y_array, max_iter, escape_radius_sq)


class BurningShip(BaseVisualization):
    """
    Burning Ship Fractal.

    Uses the formula: z(n+1) = (|Re(z)| + i|Im(z)|)^2 + c

    The absolute values create a unique asymmetric fractal that resembles
    a burning ship when viewed from the right angle.
    """

    def __init__(self):
        """Initialize Burning Ship fractal."""
        super().__init__()
        # Try to detect GPU support
        self.use_gpu = False
        try:
            if cuda.is_available():
                self.use_gpu = True
        except (ImportError, AttributeError):
            pass

    def get_name(self) -> str:
        """Get the display name."""
        return "Burning Ship"

    def get_default_params(self) -> dict:
        """Get default parameters for Burning Ship."""
        return {
            'center_x': -0.5,
            'center_y': -0.6,  # Offset to show the "ship"
            'zoom': 0.8,
            'max_iter': 512,  # 2x iteration increase
            'escape_radius': 2.0,
        }

    def compute(self, x: float, y: float) -> int:
        """
        Compute iterations for a point in the Burning Ship set.

        Args:
            x: Real component of complex number c
            y: Imaginary component of complex number c

        Returns:
            Number of iterations before escape (or max_iter)
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        return int(burning_ship_compute_jit(x, y, self.max_iter, escape_radius_sq))

    def compute_array(self, x_array: np.ndarray, y_array: np.ndarray) -> np.ndarray:
        """
        Compute iterations for arrays of points (vectorized, CPU).

        Args:
            x_array: 2D array of real components
            y_array: 2D array of imaginary components

        Returns:
            2D array of iteration counts
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Flatten for JIT computation
        x_flat = x_array.flatten()
        y_flat = y_array.flatten()

        return burning_ship_compute_array(x_flat, y_flat, self.max_iter, escape_radius_sq)

    def compute_gpu(self, x_array: np.ndarray, y_array: np.ndarray) -> np.ndarray:
        """
        Compute iterations for arrays of points (GPU-accelerated).

        Args:
            x_array: 2D array of real components
            y_array: 2D array of imaginary components

        Returns:
            2D array of iteration counts
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Flatten for GPU computation
        x_flat = x_array.flatten()
        y_flat = y_array.flatten()

        return burning_ship_compute_gpu(x_flat, y_flat, self.max_iter, escape_radius_sq)
