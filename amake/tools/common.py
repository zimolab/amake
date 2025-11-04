import builtins
from pathlib import Path
from typing import Optional, Union


DEFAULT_AMAKE_SCHEMA_FILENAMES = ("amake.schema.json",)
DEFAULT_AMAKE_CONFIGS_FILENAMES = ("amake.config.json",)

_debug = getattr(builtins, "_amake_debug", print)
_error = getattr(builtins, "_amake_error", print)


def find_default_schema_file(
    current_dir: Optional[Path] = None, none_if_not_found=True
) -> Optional[Path]:
    current_dir = Path(current_dir or ".")
    for filename in DEFAULT_AMAKE_SCHEMA_FILENAMES:
        path = current_dir / filename
        if path.exists():
            return path
    if none_if_not_found:
        return None
    return current_dir / DEFAULT_AMAKE_SCHEMA_FILENAMES[0]


def find_default_config_file(
    current_dir: Optional[Path] = None, none_if_not_found=True
):
    current_dir = Path(current_dir or ".")
    for filename in DEFAULT_AMAKE_CONFIGS_FILENAMES:
        path = current_dir / filename
        if path.exists():
            return path
    if none_if_not_found:
        return None
    return current_dir / DEFAULT_AMAKE_CONFIGS_FILENAMES[0]


def curdir(current_dir: Union[str, Path, None] = None) -> Path:
    return Path(current_dir or Path.cwd())


def get_config_file(
    current_dir: Union[str, Path, None] = None, config_file: Optional[str] = None
) -> Optional[Path]:
    current_dir = curdir(current_dir)
    if not config_file:
        _debug(
            f"Config file not specified, finding default config file in '{current_dir.as_posix()}'..."
        )
        config_file = find_default_config_file(current_dir, none_if_not_found=True)
        if not config_file:
            _error(f"No default config file found in '{current_dir.as_posix()}'")
            return None
        _debug(f"Found default config file '{config_file.as_posix()}'")
        return config_file
    config_file = current_dir / config_file
    if not config_file.is_file():
        _error(f"Config file '{config_file.as_posix()}' does not exist")
        return None
    return config_file


def get_schema_file(
    current_dir: Union[str, Path, None] = None, schema_file: Optional[str] = None
) -> Optional[Path]:
    current_dir = curdir(current_dir)
    if not schema_file:
        _debug(
            f"Schema file not specified, finding default schema file in '{current_dir.as_posix()}'..."
        )
        schema_file = find_default_schema_file(current_dir, none_if_not_found=True)
        if not schema_file:
            _error(f"No default schema file found in '{current_dir.as_posix()}'")
            return None
        _debug(f"Found default schema file '{schema_file.as_posix()}'")
        return schema_file
    schema_file = current_dir / schema_file
    if not schema_file.is_file():
        _error(f"Schema file '{schema_file.as_posix()}' does not exist")
        return None
    return schema_file
