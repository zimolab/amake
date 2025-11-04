from typing import Optional

from . import edit_amake_schema
from .common import (
    get_schema_file,
    _error,
    _debug,
    curdir,
    DEFAULT_AMAKE_SCHEMA_FILENAMES,
    find_default_config_file,
)

DEFAULT_AMAKE_SCHEMA_TEMPLATE = "classic"


def init_amake_schema(
    schema_file: Optional[str], template: Optional[str], current_dir: str, no_edit: bool
) -> int:
    schema_file_tmp = get_schema_file(current_dir, schema_file)
    if schema_file_tmp:
        _error(f"Schema file {schema_file_tmp} already exists.")
        print(f"Schema file '{schema_file_tmp.as_posix()}' already exists!")
        return -1

    current_dir = curdir(current_dir)
    if not schema_file:
        schema_file = DEFAULT_AMAKE_SCHEMA_FILENAMES[0]
    schema_file = current_dir / schema_file
    template = (template or DEFAULT_AMAKE_SCHEMA_TEMPLATE).strip().lower()

    from amake.schema import AmakeSchema

    if template == "classic":
        _debug(f"Schema template: {template}")
        schema = AmakeSchema.classic()
    else:
        _debug(f"Schema template: default.")
        schema = AmakeSchema.default()
    _debug(f"Saving schema to '{schema_file.as_posix()}'")

    try:
        schema.save(schema_file, indent=2, ensure_ascii=False, encoding="utf-8")
    except Exception as e:
        _error(f"Failed to save schema file: {e}")
        print(f"Failed to save schema file: {e}")
        return -1

    if no_edit:
        print(
            f"Schema file initialized at '{schema_file.as_posix()}', you can edit it later."
        )
        return 0

    return edit_amake_schema(schema_file, current_dir, text_editor=False)


def init_amake_config(
    schema_file: Optional[str],
    config_file: Optional[str],
    current_dir: str,
) -> int:
    schema_file = get_schema_file(current_dir, schema_file)
    if not schema_file:
        _error(f"Schema file not found.")
        print(f"Schema file not found!")
        return -1

    current_dir = curdir(current_dir)
    if not config_file:
        config_file = find_default_config_file(current_dir, none_if_not_found=False)
    else:
        config_file = current_dir / config_file

    if config_file.is_file():
        _error(f"Config file {config_file} already exists.")
        print(f"Config file '{config_file.as_posix()}' already exists!")
        return -1
    from amake.schema import AmakeSchema, AmakeConfigurations

    try:
        schema = AmakeSchema.load(schema_file)
    except Exception as e:
        _error(f"Failed to load schema file: {e}")
        print(f"Failed to load schema file: {e}")
        return -1

    config = AmakeConfigurations.make_from_schema(schema)
    _debug(f"Saving config to '{config_file.as_posix()}'")
    try:
        config.save(config_file, indent=2, ensure_ascii=False, encoding="utf-8")
    except Exception as e:
        _error(f"Failed to save config file: {e}")
        print(f"Failed to save config file: {e}")
        return -1

    print(f"Config file initialized at '{config_file.as_posix()}'.")
    return 0
