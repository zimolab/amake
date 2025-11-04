from pathlib import Path
from typing import Union

_PACKAGE_NAME = "amake"
_ASSETS_DIR_NAME = "_assets"
_LOCALES_DIR_NAME = "locales"
_IMAGES_DIR_NAME = "images"


def assets_dir(path: Union[str, Path, None] = None):
    if isinstance(path, str):
        path = path.strip()
    path = path or ""
    try:
        from importlib.resources import as_file, files

        with as_file(files(_PACKAGE_NAME).joinpath(_ASSETS_DIR_NAME, path)) as path:
            return path
    except ImportError:
        import pkg_resources

        return Path(
            pkg_resources.resource_filename(_PACKAGE_NAME, _ASSETS_DIR_NAME)
        ).joinpath(path)


def locales_dir() -> Path:
    return assets_dir(_LOCALES_DIR_NAME)


def images_dir() -> Path:
    return assets_dir(_IMAGES_DIR_NAME)


def image_file(filename: str) -> Path:
    return images_dir().joinpath(filename)
