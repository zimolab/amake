from pathlib import Path
from typing import Optional, Union

from .common import get_schema_file, _debug, get_config_file, curdir, _error

DEFAULT_OUTPUT_FILE = "build.sh"


def generate_build_script(
    schema_file: Optional[str] = None,
    config_file: Optional[str] = None,
    current_dir: Union[str, Path, None] = None,
    output_file: Union[str, Path, None] = None,
    no_confirm: bool = False,
) -> int:
    schema_file = get_schema_file(current_dir, schema_file)
    if not schema_file:
        print("Schema file not found.")
        return -1
    _debug(f"Found schema file '{schema_file}'")

    config_file = get_config_file(current_dir, config_file)
    if not config_file:
        print("Config file not found.")
        return -1
    _debug(f"Found config file '{config_file}'")

    current_dir = curdir(current_dir)
    if not output_file:
        output_file = current_dir / DEFAULT_OUTPUT_FILE
    else:
        output_file = current_dir / Path(output_file)

    if output_file.is_file():
        if not no_confirm:
            answer = input(
                f"Output file '{output_file}' already exists. Overwrite? (y[es]/n[o]) "
            )
            if answer.lower() != "y" and answer.lower() != "yes":
                print("Aborted.")
                return -1

    from ..schema import AmakeSchema, AmakeConfigurations
    from ..core import Amake, AmakeCommand

    try:
        schema = AmakeSchema.load(schema_file)
    except Exception as e:
        _error(f"Failed to load schema file: {e}")
        print(f"Failed to load schema file: {e}")
        return -1
    try:
        config = AmakeConfigurations.load(config_file)
    except Exception as e:
        _error(f"Failed to load config file: {e}")
        print(f"Failed to load config file: {e}")
        return -1
    try:
        executor = Amake.create_processor_executor()
        command = AmakeCommand(
            configurations=config, schema=schema, processor_executor=executor
        )
        command_line = command.to_command_string()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(command_line)
    except Exception as e:
        _error(f"Failed to generate build script: {e}")
        print(f"Failed to generate build script: {e}")
        return -1
    else:
        print(
            f"Build script generated successfully, saved to: {output_file.as_posix()}"
        )

    return 0
