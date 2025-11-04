from pathlib import Path
from typing import Optional, Union

from .common import (
    get_schema_file,
    _error,
    get_config_file,
    curdir,
    DEFAULT_AMAKE_CONFIGS_FILENAMES,
)
from ..appconfig import AmakeAppConfig
from ..utils import show_error_message


def amake_main(
    app_config: AmakeAppConfig,
    schema_file: Optional[str] = None,
    config_file: Optional[str] = None,
    current_dir: Union[str, Path, None] = None,
) -> int:
    if not app_config:
        raise ValueError("app_config is not set")

    from ..schema import AmakeSchema, AmakeConfigurations

    schema_file_tmp = schema_file
    schema_file = get_schema_file(schema_file)
    if not schema_file:
        _error(f"Schema file not found: {schema_file_tmp}")
        print(f"Schema file not found: {schema_file_tmp}")
        show_error_message(
            f"Schema file '{schema_file_tmp}' not found! You can create a new schema file by running 'amake init' command."
        )
        return -1

    try:
        schema = AmakeSchema.load(schema_file)
    except Exception as e:
        _error(f"Failed to load schema file: {schema_file} : {e}")
        print(f"Failed to load schema file: {schema_file} : {e}")
        show_error_message(f"Failed to load schema file: {schema_file} : {e}")
        return -1

    config_file_tmp = get_config_file(config_file)
    try:
        if not config_file_tmp:
            _error(f"Config file not found: {config_file}")
            print("Config file not found in current directory")
            print("Creating new config file...")
            current_dir = curdir(current_dir)
            if config_file:
                config_file = current_dir / config_file
            else:
                config_file = current_dir / DEFAULT_AMAKE_CONFIGS_FILENAMES[0]
            config_file_tmp = config_file
            config = AmakeConfigurations.make_from_schema(schema)
            config.save(config_file_tmp, ensure_ascii=False, indent=2, encoding="utf-8")
        else:
            config = AmakeConfigurations.load(config_file_tmp)
    except Exception as e:
        _error(f"Failed to load config file: {config_file_tmp} : {e}")
        print(f"Failed to load config file: {config_file_tmp} : {e}")
        show_error_message(f"Failed to load config file '{config_file_tmp}' : {e}")
        return -1

    from ..core import Amake

    try:
        app = Amake(app_config, schema, config)
        app.run()
        print("Saving app config...")
        app_config.save(ensure_ascii=False, indent=2, encoding="utf-8")
    except Exception as e:
        _error(f"Failed to run amake: {e}")
        print(f"Error: {e}")
        return -1
    return 0
