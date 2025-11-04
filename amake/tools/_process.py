from pathlib import Path
from typing import Optional, Union, List

from .common import get_schema_file, get_config_file, _error
from ..schema import AmakeConfigurations


def run_processors(
    schema_file: Optional[str] = None,
    config_file: Optional[str] = None,
    current_dir: Union[str, Path, None] = None,
    variables: Optional[List[str]] = None,
):
    schema_file = get_schema_file(current_dir, schema_file)
    if not schema_file:
        print("Schema file not found.")
        return -1
    config_file = get_config_file(current_dir, config_file)
    if not config_file:
        print("Config file not found.")
        return -1

    from amake.schema import AmakeSchema

    try:

        schema = AmakeSchema.load(schema_file)
    except Exception as e:
        _error(f"Error loading schema file: {e}")
        print(f"Failed to load schema file: {e}")
        return -1

    try:
        config = AmakeConfigurations.load(config_file)
    except Exception as e:
        _error(f"Error loading config file: {e}")
        print(f"Failed to load config file: {e}")
        return -1

    print("=" * 80)
    print("Schema File".ljust(15), ":", schema_file.as_posix())
    print("Config File".ljust(15), ":", config_file.as_posix())
    if variables:
        print("Variables".ljust(15), ":", ", ".join(variables))
    else:
        variables = list(schema.variables.keys())
        print("Variables".ljust(15), ":", "all")

    from amake.core import Amake

    executor = Amake.create_processor_executor()

    flag_not_found = object()

    print()

    failed_variables = []
    for var_name in variables:
        print(f"Variable Name".ljust(15), ":", var_name)
        if not schema.has_variable(var_name):
            print("Warning".ljust(15), ":", "Skipped (not defined in schema)")
            print()
            continue

        var_value = config.variables.get(var_name, flag_not_found)
        if var_value is flag_not_found:
            var_value = schema.default_value_of(var_name)

        processors = schema.processor_of(var_name)
        print(f"Initial Value".ljust(15), ":", var_value, f" (type: {type(var_value)})")
        print(f"Processors".ljust(15), ":", f"{processors or 'No Processors Defined'}")
        if not processors:
            continue

        print("Run Processors".ljust(15), ":")
        try:
            print("*" * 80)
            final_value = schema.run_processor_on(
                executor, var_name, var_value, debug=True
            )
            print("*" * 80)
            print(
                f"Final Value".ljust(15),
                ":",
                final_value,
                f" (type: {type(final_value)})",
            )
        except Exception as e:
            _error(f"Error processing variable {var_name}: {e}")
            print("Error:".ljust(15), ":", f"{e}")
            failed_variables.append(var_name)
            print("*" * 80)
            continue
        finally:
            print()
    if failed_variables:
        print("Failed Variables".ljust(15), ":", ", ".join(failed_variables))
    print("=" * 80)
    return 0
