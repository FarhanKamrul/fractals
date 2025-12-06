"""
Mandelbrot Set fractal implementation.

The Mandelbrot set is the set of complex numbers c for which the function
f(z) = z² + c does not diverge when iterated from z = 0.
"""

import numpy as np
try:
    from numba import jit, cuda
    NUMBA_AVAILABLE = True
    CUDA_AVAILABLE = cuda.is_available()
except ImportError:
    NUMBA_AVAILABLE = False
    CUDA_AVAILABLE = False
    # Dummy decorator if numba not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from .base import BaseVisualization


@jit(nopython=True, cache=True)
def mandelbrot_compute_jit(cx, cy, max_iter, escape_radius_sq):
    """
    JIT-compiled Mandelbrot computation for speed.

    Args:
        cx: Real component of c
        cy: Imaginary component of c
        max_iter: Maximum iterations
        escape_radius_sq: Squared escape radius

    Returns:
        Number of iterations before escape
    """
    zx, zy = 0.0, 0.0

    for iteration in range(max_iter):
        zx_sq = zx * zx
        zy_sq = zy * zy

        if zx_sq + zy_sq > escape_radius_sq:
            return iteration

        zy = 2.0 * zx * zy + cy
        zx = zx_sq - zy_sq + cx

    return max_iter


@jit(nopython=True, parallel=True, cache=True)
def mandelbrot_compute_array(x_array, y_array, max_iter, escape_radius_sq):
    """
    JIT-compiled vectorized Mandelbrot computation.

    Args:
        x_array: Flattened array of x coordinates
        y_array: Flattened array of y coordinates
        max_iter: Maximum iterations
        escape_radius_sq: Squared escape radius

    Returns:
        Array of iteration counts
    """
    n = len(x_array)
    result = np.zeros(n, dtype=np.int32)

    for i in range(n):
        result[i] = mandelbrot_compute_jit(
            x_array[i], y_array[i], max_iter, escape_radius_sq
        )

    return result


if CUDA_AVAILABLE:
    @cuda.jit
    def mandelbrot_kernel_cuda(x_array, y_array, result, max_iter, escape_radius_sq):
        """
        CUDA kernel for GPU-accelerated Mandelbrot computation.

        Each GPU thread computes one pixel.

        Args:
            x_array: Array of x coordinates
            y_array: Array of y coordinates
            result: Output array for iteration counts
            max_iter: Maximum iterations
            escape_radius_sq: Squared escape radius
        """
        idx = cuda.grid(1)

        if idx < x_array.size:
            cx = x_array[idx]
            cy = y_array[idx]

            zx = 0.0
            zy = 0.0

            iteration = 0
            while iteration < max_iter:
                zx_sq = zx * zx
                zy_sq = zy * zy

                if zx_sq + zy_sq > escape_radius_sq:
                    break

                zy = 2.0 * zx * zy + cy
                zx = zx_sq - zy_sq + cx
                iteration += 1

            result[idx] = iteration

    def mandelbrot_compute_gpu(x_array, y_array, max_iter, escape_radius_sq):
        """
        GPU-accelerated Mandelbrot computation using CUDA.

        Args:
            x_array: Flattened array of x coordinates
            y_array: Flattened array of y coordinates
            max_iter: Maximum iterations
            escape_radius_sq: Squared escape radius

        Returns:
            Array of iteration counts
        """
        # Ensure arrays are contiguous
        x_array = np.ascontiguousarray(x_array, dtype=np.float64)
        y_array = np.ascontiguousarray(y_array, dtype=np.float64)

        n = len(x_array)
        result = np.zeros(n, dtype=np.int32)

        # Copy data to GPU
        d_x = cuda.to_device(x_array)
        d_y = cuda.to_device(y_array)
        d_result = cuda.to_device(result)

        # Configure kernel launch
        threads_per_block = 256
        blocks = (n + threads_per_block - 1) // threads_per_block

        # Launch kernel
        mandelbrot_kernel_cuda[blocks, threads_per_block](
            d_x, d_y, d_result, max_iter, escape_radius_sq
        )

        # Copy result back to CPU
        d_result.copy_to_host(result)

        return result
else:
    def mandelbrot_compute_gpu(x_array, y_array, max_iter, escape_radius_sq):
        """Fallback when CUDA not available."""
        return mandelbrot_compute_array(x_array, y_array, max_iter, escape_radius_sq)


class Mandelbrot(BaseVisualization):
    """
    The classic Mandelbrot Set fractal.

    The most iconic fractal, discovered by Benoit Mandelbrot.
    Points are colored based on how quickly they escape to infinity.
    """

    def __init__(self):
        """Initialize Mandelbrot set with default parameters."""
        super().__init__()

    def get_name(self) -> str:
        """Get the display name."""
        return "Mandelbrot Set"

    def get_default_params(self) -> dict:
        """Get default parameters for Mandelbrot set."""
        return {
            'center_x': -0.5,
            'center_y': 0.0,
            'zoom': 1.0,  # 2x zoom increase from 0.5
            'max_iter': 512,  # 2x iteration increase
            'escape_radius': 2.0,
        }

    def compute(self, x: float, y: float) -> int:
        """
        Compute iterations for a point in the Mandelbrot set.

        Args:
            x: Real component of complex number c
            y: Imaginary component of complex number c

        Returns:
            Number of iterations before escape (or max_iter)
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use JIT-compiled function for speed
        return int(mandelbrot_compute_jit(x, y, self.max_iter, escape_radius_sq))

    def compute_array(self, x_array, y_array):
        """
        Compute iterations for arrays of points (vectorized, JIT-compiled).

        Args:
            x_array: Array of x coordinates
            y_array: Array of y coordinates

        Returns:
            Array of iteration counts
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use JIT-compiled vectorized function
        return mandelbrot_compute_array(x_array, y_array, self.max_iter, escape_radius_sq)

    def compute_gpu(self, x_array, y_array):
        """
        GPU-accelerated computation for arrays of points using CUDA.

        Args:
            x_array: Array of x coordinates
            y_array: Array of y coordinates

        Returns:
            Array of iteration counts
        """
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use GPU-accelerated function (falls back to CPU if CUDA unavailable)
        return mandelbrot_compute_gpu(x_array, y_array, self.max_iter, escape_radius_sq)
