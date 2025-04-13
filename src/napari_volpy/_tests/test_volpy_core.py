import numpy as np
from napari_volpy.volpy_core import run_volpy


def test_run_volpy():
    image = np.random.rand(50, 64, 64)  # (T, Y, X)
    params = {"fr": 30, "use_mrcnn": False, "template_size": 0.02, "context_size": 0.1}

    results = run_volpy(image=image, params=params)

    assert "rois" in results
    assert "traces" in results
    assert "denoised" in results
    assert results["denoised"].shape == image.shape
    assert results["rois"].ndim == 3
    assert results["traces"].ndim == 2
