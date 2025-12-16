try:
    from numba import njit, prange
    NUMBA = True
except ImportError:
    NUMBA = False
    def njit(*args, **kwargs):
        def wrap(f): return f
        return wrap
    prange = range
