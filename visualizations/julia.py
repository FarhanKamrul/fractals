"""
Julia Set fractal implementation.

The Julia set is similar to the Mandelbrot set but uses a fixed complex
parameter c, while z varies. Different values of c produce vastly different
and beautiful patterns.
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
def julia_compute_jit(zx, zy, cx, cy, max_iter, escape_radius_sq):
    """
    JIT-compiled Julia set computation for speed.

    Args:
        zx: Initial real component of z
        zy: Initial imaginary component of z
        cx: Real component of c (constant)
        cy: Imaginary component of c (constant)
        max_iter: Maximum iterations
        escape_radius_sq: Squared escape radius

    Returns:
        Number of iterations before escape
    """
    for iteration in range(max_iter):
        zx_sq = zx * zx
        zy_sq = zy * zy

        if zx_sq + zy_sq > escape_radius_sq:
            return iteration

        zy = 2.0 * zx * zy + cy
        zx = zx_sq - zy_sq + cx

    return max_iter


@jit(nopython=True, parallel=True, cache=True)
def julia_compute_array(x_array, y_array, cx, cy, max_iter, escape_radius_sq):
    """
    JIT-compiled vectorized Julia set computation.

    Args:
        x_array: Flattened array of x coordinates
        y_array: Flattened array of y coordinates
        cx: Real component of c (constant)
        cy: Imaginary component of c (constant)
        max_iter: Maximum iterations
        escape_radius_sq: Squared escape radius

    Returns:
        Array of iteration counts
    """
    n = len(x_array)
    result = np.zeros(n, dtype=np.int32)

    for i in range(n):
        result[i] = julia_compute_jit(
            x_array[i], y_array[i], cx, cy, max_iter, escape_radius_sq
        )

    return result


if CUDA_AVAILABLE:
    @cuda.jit
    def julia_kernel_cuda(x_array, y_array, result, cx, cy, max_iter, escape_radius_sq):
        """
        CUDA kernel for GPU-accelerated Julia set computation.

        Each GPU thread computes one pixel.

        Args:
            x_array: Array of x coordinates (z initial values)
            y_array: Array of y coordinates (z initial values)
            result: Output array for iteration counts
            cx: Real component of c (constant)
            cy: Imaginary component of c (constant)
            max_iter: Maximum iterations
            escape_radius_sq: Squared escape radius
        """
        idx = cuda.grid(1)

        if idx < x_array.size:
            zx = x_array[idx]
            zy = y_array[idx]

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

    def julia_compute_gpu(x_array, y_array, cx, cy, max_iter, escape_radius_sq):
        """
        GPU-accelerated Julia set computation using CUDA.

        Args:
            x_array: Flattened array of x coordinates
            y_array: Flattened array of y coordinates
            cx: Real component of c (constant)
            cy: Imaginary component of c (constant)
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
        julia_kernel_cuda[blocks, threads_per_block](
            d_x, d_y, d_result, cx, cy, max_iter, escape_radius_sq
        )

        # Copy result back to CPU
        d_result.copy_to_host(result)

        return result
else:
    def julia_compute_gpu(x_array, y_array, cx, cy, max_iter, escape_radius_sq):
        """Fallback when CUDA not available."""
        return julia_compute_array(x_array, y_array, cx, cy, max_iter, escape_radius_sq)


class Julia(BaseVisualization):
    """
    Julia Set fractal.

    Related to the Mandelbrot set, but produces different beautiful patterns
    for each choice of the complex parameter c.
    """

    def __init__(self, c_real: float = -0.7, c_imag: float = 0.27015):
        """
        Initialize Julia set with default parameters.

        Args:
            c_real: Real component of the Julia set constant
            c_imag: Imaginary component of the Julia set constant
        """
        super().__init__()
        self.set_param('c_real', c_real)
        self.set_param('c_imag', c_imag)

    def get_name(self) -> str:
        """Get the display name."""
        c_real = self.get_param('c_real')
        c_imag = self.get_param('c_imag')
        return f"Julia Set (c = {c_real:.3f} + {c_imag:.3f}i)"

    def get_default_params(self) -> dict:
        """Get default parameters for Julia set."""
        return {
            'center_x': 0.0,
            'center_y': 0.0,
            'zoom': 1.0,  # 2x zoom increase from 0.5
            'max_iter': 256,
            'escape_radius': 2.0,
            'c_real': -0.7,
            'c_imag': 0.27015,
        }

    def compute(self, x: float, y: float) -> int:
        """
        Compute iterations for a point in the Julia set.

        Args:
            x: Real component of z
            y: Imaginary component of z

        Returns:
            Number of iterations before escape (or max_iter)
        """
        # c is fixed for Julia sets
        cx = self.get_param('c_real')
        cy = self.get_param('c_imag')
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use JIT-compiled function for speed
        return int(julia_compute_jit(x, y, cx, cy, self.max_iter, escape_radius_sq))

    def compute_array(self, x_array, y_array):
        """
        Compute iterations for arrays of points (vectorized, JIT-compiled).

        Args:
            x_array: Array of x coordinates
            y_array: Array of y coordinates

        Returns:
            Array of iteration counts
        """
        cx = self.get_param('c_real')
        cy = self.get_param('c_imag')
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use JIT-compiled vectorized function
        return julia_compute_array(x_array, y_array, cx, cy, self.max_iter, escape_radius_sq)

    def compute_gpu(self, x_array, y_array):
        """
        GPU-accelerated computation for arrays of points using CUDA.

        Args:
            x_array: Array of x coordinates
            y_array: Array of y coordinates

        Returns:
            Array of iteration counts
        """
        cx = self.get_param('c_real')
        cy = self.get_param('c_imag')
        escape_radius = self.get_param('escape_radius', 2.0)
        escape_radius_sq = escape_radius * escape_radius

        # Use GPU-accelerated function (falls back to CPU if CUDA unavailable)
        return julia_compute_gpu(x_array, y_array, cx, cy, self.max_iter, escape_radius_sq)

    def set_c(self, c_real: float, c_imag: float):
        """
        Set the Julia set constant c.

        Args:
            c_real: Real component of c
            c_imag: Imaginary component of c
        """
        self.set_param('c_real', c_real)
        self.set_param('c_imag', c_imag)


# Some beautiful Julia set presets
JULIA_PRESETS = [
    (-0.7, 0.27015),   # Classic spiral
    (-0.8, 0.156),     # Douady's rabbit
    (0.285, 0.01),     # Dragon
    (-0.4, 0.6),       # Branching
    (0.28, 0.008),     # Swirls
    (-0.835, -0.2321), # Lightning
    (-0.70176, -0.3842), # Dendrite
]
