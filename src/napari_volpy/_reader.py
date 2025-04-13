from pathlib import Path
import numpy as np
import tifffile
import h5py


def napari_get_reader(path):
    """Determine the appropriate reader for the file."""
    if isinstance(path, str) and path.endswith(
        (".tif", ".tiff", ".h5", ".hdf5", ".mmap")
    ):
        return volpy_reader
    return None


def volpy_reader(path):
    """Read VolPy-compatible files."""
    path = Path(path)
    try:
        if path.suffix in (".tif", ".tiff"):
            data = tifffile.imread(path)
        elif path.suffix in (".h5", ".hdf5"):
            with h5py.File(path, "r") as f:
                data = f.get("mov", f.get("data"))[:]  # Common CaImAn keys
        elif path.suffix == ".mmap":
            from caiman.base.movies import load  # 延迟导入

            data = load(path)
        else:
            return None

        # Standardize shape to (T, Y, X)
        if data.ndim == 2:
            data = data[np.newaxis, ...]
        elif data.ndim == 3 and data.shape[-1] < min(data.shape[:2]):
            data = data.transpose(2, 0, 1)

        return [(data, {"name": path.stem}, "image")]
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None
