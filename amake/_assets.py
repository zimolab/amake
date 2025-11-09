from pathlib import Path
from typing import Union

from pyguiadapterlite.pathutils import package_path

_PACKAGE_NAME = "amake"
_ASSETS_DIR_NAME = "_assets"
_LOCALES_DIR_NAME = "locales"
_IMAGES_DIR_NAME = "images"


def _assets_path(package: str, data_dir: str, *paths) -> Path:
    return package_path(package, data_dir, *paths)


def assets_dir(path: Union[str, Path, None] = None):
    return _assets_path(_PACKAGE_NAME, _ASSETS_DIR_NAME, path)


def locales_dir() -> Path:
    return assets_dir(_LOCALES_DIR_NAME)


def images_dir() -> Path:
    return assets_dir(_IMAGES_DIR_NAME)


def image_file(filename: str) -> Path:
    return images_dir().joinpath(filename)
