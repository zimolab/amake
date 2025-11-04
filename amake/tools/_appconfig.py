import builtins
import os
from pathlib import Path
from typing import Dict

from amake.appconfig import AmakeAppConfig
from amake.utils import open_file_in_editor


def appconfig_list(app_config: AmakeAppConfig) -> int:
    print("Current Configuration of Amake:")
    print()
    print(app_config.list())
    print()
    return 0


def appconfig_edit(app_config: AmakeAppConfig) -> int:
    filepath = app_config.filepath
    if not filepath:
        print("No configuration file found.")
        return -1
    open_file_in_editor(filepath)
    return 0


def appconfig_reset(app_config: AmakeAppConfig, no_confirm: bool = False) -> int:
    filepath = app_config.filepath

    if not filepath:
        default_filepath = getattr(builtins, "_amake_appconfig_filepath", None)
        if not default_filepath:
            print("Unable to determine the path of the app configuration file!")
            return -1
        filepath = default_filepath

    if not os.path.isfile(filepath):
        print(f"The app configuration file '{filepath}' does not exist!")
        print("Creating a new app configuration file with default values...")
        try:
            app_config = AmakeAppConfig.default()
            app_config.save(filepath, encoding="utf-8", indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to create a new app configuration file: {e}")
            return -1
        else:
            print(f"New app configuration file created at '{filepath}'.")
            return 0
    if not no_confirm:
        answer = input(
            f"Remove the existing app configuration file '{filepath}'? (y[es]/n[o]) "
        )
        if answer.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0

    filepath = Path(filepath)
    try:
        filepath.unlink()
    except Exception as e:
        print(f"Failed to remove the app configuration file: {e}")
        return -1
    print(f"The app configuration file '{filepath}' has been removed.")
    print("Creating a new app configuration file with default values...")
    try:
        app_config = AmakeAppConfig.default()
        app_config.save(filepath, encoding="utf-8", indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to create a new app configuration file: {e}")
        return -1
    else:
        print(f"New app configuration file created at '{filepath}'.")
        return 0


def appconfig_set(app_config: AmakeAppConfig, paris: Dict[str, str]) -> int:
    try:
        app_config.set(paris)
        app_config.save(encoding="utf-8", indent=2, ensure_ascii=False)
        print("New app configs have been saved!")
        return 0
    except Exception as e:
        print(f"Failed to set or save the app configs: {e}")
        return -1
