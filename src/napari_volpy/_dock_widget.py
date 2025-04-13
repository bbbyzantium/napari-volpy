from magicgui import magicgui
import napari
import numpy as np
from napari.types import ImageData
from napari.utils import progress
import json
from pathlib import Path


@magicgui(
    call_button="Run VolPy",
    image={"label": "Input Image", "tooltip": "Select the voltage imaging data"},
    fr={"label": "Frame Rate (Hz)", "value": 30.0, "min": 1.0, "max": 1000.0},
    template_size={"label": "ROI Size (um)", "value": 0.02, "min": 0.01, "max": 0.1},
    context_size={"label": "Context Size (um)", "value": 0.1, "min": 0.05, "max": 0.5},
    use_mrcnn={
        "label": "Use Mask R-CNN",
        "value": False,
        "tooltip": "Requires model setup",
    },
    do_denoising={"label": "Enable Denoising", "value": True},
)
def volpy_widget(
    viewer: napari.Viewer,
    image: ImageData,
    fr: float,
    template_size: float,
    context_size: float,
    use_mrcnn: bool,
    do_denoising: bool,
):
    """VolPy analysis widget for voltage imaging."""
    from .volpy_core import run_volpy  # 确保导入在函数内部

    if image is None:
        viewer.status = "Please select an image layer!"
        return

    params = {
        "fr": fr,
        "template_size": template_size,
        "context_size": context_size,
        "use_mrcnn": use_mrcnn,
        "do_temporal_low_pass": do_denoising,
        "do_spatial_smooth": do_denoising,
        "threshold_method": "adaptive_threshold" if not use_mrcnn else "mrcnn",
    }

    viewer.status = "Running VolPy..."
    try:
        with progress(total=3) as pbar:
            pbar.set_description("Processing")
            results = run_volpy(image=image, params=params)
            pbar.update(1)

            viewer.add_image(results["denoised"], name="Denoised Image")
            pbar.update(1)

            viewer.add_labels(results["rois"], name="VolPy ROIs")
            plot_traces(viewer, results["traces"], name="VolPy Traces")
            pbar.update(1)

        viewer.status = "VolPy completed!"
    except Exception as e:
        viewer.status = f"Error: {str(e)}"
        raise


# 其余代码不变
def plot_traces(viewer: napari.Viewer, traces: np.ndarray, name: str):
    """Display signal traces as a Tracks layer."""
    T = traces.shape[1]
    track_data = []
    track_ids = []
    for i in range(traces.shape[0]):
        times = np.arange(T)
        values = traces[i]
        track = np.stack([times, values], axis=1)
        track_data.append(track)
        track_ids.extend([i] * T)
    track_data = np.concatenate(track_data, axis=0)
    viewer.add_tracks(
        track_data, properties={"track_id": track_ids}, name=name, scale=(1, 0.001)
    )


@magicgui(
    call_button="Export Results",
    output_path={"label": "Output HDF5 Path", "mode": "w", "filter": "*.h5"},
)
def export_results(viewer: napari.Viewer, output_path: Path):
    """Export VolPy results to HDF5."""
    import h5py

    rois = viewer.layers.get("VolPy ROIs")
    traces = viewer.layers.get("VolPy Traces")

    if rois is None or traces is None:
        viewer.status = "No results to export!"
        return

    with h5py.File(output_path, "w") as f:
        f.create_dataset("rois", data=rois.data)
        f.create_dataset("traces", data=traces.data[:, 1])
    viewer.status = f"Results saved to {output_path}"


@magicgui(
    call_button="Save Parameters",
    output_path={"label": "JSON Path", "mode": "w", "filter": "*.json"},
)
def save_params(
    viewer: napari.Viewer,
    output_path: Path,
    fr: float,
    template_size: float,
    context_size: float,
):
    """Save VolPy parameters to a JSON file."""
    params = {"fr": fr, "template_size": template_size, "context_size": context_size}
    with open(output_path, "w") as f:
        json.dump(params, f)
    viewer.status = f"Parameters saved to {output_path}"


def make_volpy_widget():
    return volpy_widget


def make_save_params_widget():
    return save_params
