import numpy as np


def run_volpy(image: np.ndarray = None, params: dict = None):
    """Run VolPy analysis on voltage imaging data."""
    from caiman.source_extraction.volpy.volpy import VOLPY  # 延迟导入

    if image is None:
        raise ValueError("'image' must be provided.")

    image = image.astype(np.float32)
    vpy = VOLPY(
        fr=params["fr"],
        template_size=params["template_size"],
        context_size=params["context_size"],
        do_temporal_low_pass=params["do_temporal_low_pass"],
        do_spatial_smooth=params["do_spatial_smooth"],
        threshold_method=params["threshold_method"],
    )

    vpy.fit(image)

    results = {
        "denoised": vpy.denoised_data if params["do_temporal_low_pass"] else image,
        "rois": vpy.rois,
        "traces": vpy.traces,
    }
    return results
