try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


# 延迟导入，避免直接触发 zarr 的加载
def napari_get_reader(path):
    from ._reader import napari_get_reader as reader

    return reader(path)


# 如果有 _sample_data.py，可以保留此功能；否则可以删除
def make_sample_data():
    from ._sample_data import make_sample_data as sample_data

    return sample_data()


# 导出符号，供 Napari 使用
__all__ = (
    "napari_get_reader",
    "make_sample_data",
)
