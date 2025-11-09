#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""amake: a makefile assistant tool to help you write more flexible and maintainable makefiles.

Usage:
    amake [-C <dir> | --current-dir=<dir>] [-s <schemafile> | --schema=<schemafile>] [-c <configfile> | --config=<configfile>]
    amake init [-C <dir> | --current-dir=<dir>] [-t <template> | --template=<template>] [--no-edit] [<schemafile>]
    amake init-config [-C <dir> | --current-dir=<dir>] [<schemafile>] [<configfile>]
    amake edit [-C <dir> | --current-dir=<dir>] [-T | --text-editor] [<schemafile>]
    amake process [-C <dir> | --current-dir=<dir>] [--vars=<vars,...>] [<schemafile>] [<configfile>]
    amake generate [-C <dir> | --current-dir=<dir>] [-o <outputfile> | --output=<outputfile>] [-Y | --yes] [<schemafile>] [<configfile>]
    amake appconfig (--set=<config-paris> | --reset | --list | --edit) [-y | --yes]

Commands:
    init        Initialize a new amake project in the current directory. An amake project means a directory
                with an amake schema file. if not specified, the amake schema file will be named "amake.schema.json".

    init-config Initialize a new amake config file in the current directory. An amake config file means a file with
                a JSON object, which contains the values of variables defined in the amake schema. If not specified,
                the amake config file will be named "amake.config.json". If <schemafile> is not specified, use default
                amake schema file "amake.schema.json" in the current directory. If <configfile> is not specified, use
                "amake.config.json" in the current directory.

    edit        Edit the amake schema file in a GUI editor or a text editor(with -T or --text-editor option).

    process     Apply the processors on variables in the config file. The processor of a variable is defined
                in the amake schema using the "__processor__" field. If <schemafile> is not specified, use
                "amake.schema.json" in the current directory. If <configfile> is not specified, use "amake.config.json"
                in the current directory. This command is usually used for debugging purpose, it shows the processor call
                chain, the result of each processor and the final result of the variables. The final result is0 the actual
                value will be used passed to the makefile. How the processor works: Assuming we have defined  a variable
                 "INCLUDES" in the amake schema, and the initial value of it is a python list ["dir1", "dir2", "dir3"].
                Apparently, a python list is not a valid variable type in the makefile, so we need to convert it to a string
                when it is passed to the makefile. We may also want to add a "-I" prefix to each element of the list.
                To achieve this, we can define a processor chain on the "INCLUDES" variable in the amake schema as follows:
                    {
                        ...
                        variables: {
                            "INCLUDES": {
                                "__type__": "dirs_t",
                                "__processor__": "prefix_each '-I' | join ' ' | strip"

                            }
                        }
                        ...
                    }
                As you can see, we define three processors on the "INCLUDES" variable, and chained them with the pipe
                symbol "|". The first processor "prefix_each" is used to adds a prefix to each element of the list, "-I"
                is an argument of this processor which specifies the prefix(if a processor needs more than one argument,
                the arguments should be separated by a whitespace not a comma), so the output of this processor will be
                a list of ["-Idir1", "-Idir2", "-Idir3"]. The second processor "join" is used to join the elements of a
                list with the specified separator, in this case, it takes the output value of the previous "prefix_each"
                processor as the input, and joins the elements with a whitespace separator, so the output of this
                processor will be a string "-Idir1 -Idir2 -Idir3". The third processor "strip"  takes the output of the
                previous "join" processor as its input, and removes the leading and trailing spaces(if any). Since the
                "strip" processor is the last processor in the chain, its output will be the final value of the "INCLUDES"
                variable and be passed to the makefile.

    generate    Generate a build script based on the amake schema and the variable values in the config file.

    appconfig   A command to manage the amake app configuration.



Options:
    -s <schemafile>, --schema=<schemafile>   Specify the amake schema file to use. If not specified, use "amake.schema.json"
                                             in the current directory.

    -c <configfile>, --config=<configfile>   Specify the amake config file to use. If not specified, use "amake.config.json".

    -C <dir>, --current-dir=<dir>            Specify the current directory, if not specified, use the current working
                                             directory.

    -t <template> | --template=<template>    Specify the schema template to use. If not specified, use the default
                                             template. The default template is a blank schema, which means no variables
                                             predefined in the schema. Another template is "classic", which has some
                                             predefined variables as demonstration, with those variables definitions
                                             user can learn some basic concepts of how to define variables.

    -T, --text-editor                        Whether to use a system text editor instead of the GUI editor to edit
                                             the schema file.

    --no-edit                                When specified, it will not open the schema editor to edit the schema file
                                             after initialization.

    --vars=<vars,...>                        Specify the variables to run processors on. If not specified, all variables
                                             will be processed.

    -o <outputfile> | --output=<outputfile>  Specify the output file for the generated build script. If not specified,
                                             use "build.sh" in the current directory.

    -Y, --yes                                When specified, it will not ask for confirmation before some important
                                             operations, such as generating the build script or resetting the app config .etc.

    --set=<config-paris>                     This option is used with the "appconfig" command. It is used to set the value
                                             of a specific config item. Syntax: --set="config1=value1,config2=value2,...".
                                             For example, user can change the locale of the app by the following command:
                                                amake appconfig --set=locale=en_US

    --reset                                  This option is used with the "appconfig" command. It is used to reset the
                                             app config. Sometimes, the app config file maybe corrupted, this option will
                                             remove the app config file and create a new one with default values.

    --list                                   This option is used with the "appconfig" command. It is used to list all
                                             config items and their current values.

    --edit                                   This option is used with the "appconfig" command. It is used to edit the
                                             app config file in a text editor.

"""

import builtins
import os
import shutil
import sys
from typing import Optional


from amake.thirdparty import platformdirs
from pathlib import Path


__APP_NAME__ = "amake"
__APP_VERSION__ = "0.1.0"
__APP_DESCRIPTION__ = "A makefile assistant tool to help you write more flexible and maintainable makefiles."
__APP_LICENSE__ = "MIT License"
__APP_COPYRIGHT__ = "Copyright (c) 2021 zimolab"
__APP_DATADIR__ = platformdirs.user_data_dir(__APP_NAME__.lower())
__APP_LOCALEDIR__ = os.path.join(__APP_DATADIR__, "locales")
__APP_CONFIG_FILEPATH__ = os.path.join(__APP_DATADIR__, "amake_config.json")
__APP_REPO__ = "https://github.com/zimolab/amake"
__APP_AUTHOR__ = "ziomlab"


_DEBUG_MODE = True

setattr(builtins, "_amake_app_name", __APP_NAME__)
setattr(builtins, "_amake_app_description", __APP_DESCRIPTION__)
setattr(builtins, "_amake_app_datadir", __APP_DATADIR__)
setattr(builtins, "_amake_app_version", __APP_VERSION__)
setattr(builtins, "_amake_app_repo", __APP_REPO__)
setattr(builtins, "_amake_app_author", __APP_AUTHOR__)
setattr(builtins, "_amake_appconfig_filepath", __APP_CONFIG_FILEPATH__)
setattr(builtins, "_amake_app_license", __APP_LICENSE__)
setattr(builtins, "_amake_app_copyright", __APP_COPYRIGHT__)


ALL_COMMANDS = ("edit", "init", "init-config", "process", "generate", "appconfig")


def _debug(msg):
    if not _DEBUG_MODE:
        return
    print(f"[DEBUG] {msg}")


def _error(msg):
    if not _DEBUG_MODE:
        return
    print(f"[ERROR] {msg}")


# Add debug functions to builtins, so they can be accessed from anywhere
setattr(builtins, "_amake_debug", _debug)
setattr(builtins, "_amake_error", _error)


def _load_app_config():
    from amake.appconfig import AmakeAppConfig

    _debug(f"Loading app config from: {__APP_CONFIG_FILEPATH__}")
    app_config_path = Path(__APP_CONFIG_FILEPATH__)
    if not app_config_path.is_file():
        _debug(f"App config file not found")
        app_config = AmakeAppConfig.default()
        _debug(f"Creating new app config file: {app_config_path.as_posix()}")
        app_config_path.parent.mkdir(parents=True, exist_ok=True)
        app_config.save(
            app_config_path.as_posix(), encoding="utf-8", ensure_ascii=False, indent=2
        )
        return app_config
    try:
        app_config = AmakeAppConfig.load(app_config_path.as_posix())
        return app_config
    except Exception as e:
        _error(
            f"Failed to load app config from file: {app_config_path.as_posix()}: {e}"
        )
        app_config = AmakeAppConfig.default()
        app_config.save(
            app_config_path.as_posix(), encoding="utf-8", ensure_ascii=False, indent=2
        )
        return app_config


# Load app config
_app_config = _load_app_config()
# add app_config to builtins, so it can be accessed from anywhere
setattr(builtins, "_amake_app_config", _app_config)


def _setup_env():
    global _app_config
    # Set environment variables
    _debug(f"Setting environment variables...")
    # MAKE SURE SETTING ENVIRONMENT VARIABLES BEFORE IMPORTING PYGUIADAPTERLITE AND ANY SUB PACKAGES OR MODULES OF IT
    # OTHERWISE I18N WON'T WORK PROPERLY
    os.environ["PYGUIADAPTERLITE_LOGGING_MESSAGE"] = "0"
    os.environ["PYGUIADAPTERLITE_LOCALE"] = _app_config.locale
    import pyguiadapterlite

    pyguiadapterlite.set_default_parameter_label_justify("left")


_setup_env()


def _check_dirs():
    _debug(f"Checking app data directories...")
    app_data_dir = Path(__APP_DATADIR__)
    if not app_data_dir.is_dir():
        _debug(f"Creating app data directory: {app_data_dir.as_posix()}")
        app_data_dir.mkdir(parents=True)

    app_locale_dir = Path(__APP_LOCALEDIR__)
    if not app_locale_dir.is_dir():
        _debug(f"Creating app locale directory: {app_locale_dir.as_posix()}")
        app_locale_dir.mkdir(parents=True)


_check_dirs()


def _initialize_locale():
    global _app_config
    _debug(f"Initializing app locale...")
    app_locale_dir = Path(__APP_LOCALEDIR__)
    if not app_locale_dir.is_dir():
        _debug(f"Creating app locale directory: {app_locale_dir.as_posix()}")
        app_locale_dir.mkdir(parents=True)

    if not os.listdir(app_locale_dir.as_posix()):
        _debug(f"No locale files found in {app_locale_dir.as_posix()}")
        _debug(f"Copying default locale files to {app_locale_dir.as_posix()}")
        from amake import assets

        assets.export_builtin_locales(app_locale_dir.as_posix(), overwrite=True)

    _debug(f"Setting app locale: {_app_config.locale}")
    _app_config.setup_i18n(app_locale_dir.as_posix())


_initialize_locale()


def any_true(args, *opts):
    for o in opts:
        if args.get(o, False):
            return True
    return False


def all_false(args, *opts):
    for o in opts:
        if args.get(o, False):
            return False
    return True


def get_one_of(args, *opts, default=None) -> Optional[str]:
    for o in opts:
        v = args.get(o, None)
        if v is not None:
            return v
    return default


################Commands##################


def _run_amake(args) -> int:
    global _app_config

    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    schema_file = get_one_of(args, "--schema", "<schemafile>", default=None)
    config_file = get_one_of(args, "--config", "<configfile>", default=None)

    from amake.tools import amake_main

    return amake_main(_app_config, schema_file, config_file, current_dir)


def _run_command_init(args) -> int:
    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    no_edit = any_true(args, "--no-edit")
    template = get_one_of(args, "--template", "<template>", default=None)
    schemafile = get_one_of(args, "--schema", "<schemafile>", default=None)

    from amake.tools import init_amake_schema

    return init_amake_schema(schemafile, template, current_dir, no_edit)


def _run_command_init_config(args) -> int:
    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    schemafile = get_one_of(args, "--schema", "<schemafile>", default=None)
    configfile = get_one_of(args, "--config", "<configfile>", default=None)

    from amake.tools import init_amake_config

    return init_amake_config(schemafile, configfile, current_dir)


def _run_command_edit(args) -> int:
    from amake.tools import edit_amake_schema

    schema_file = get_one_of(args, "--schema", "<schemafile>", default=None)
    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    text_editor = any_true(args, "--text-editor", "-T")
    return edit_amake_schema(schema_file, current_dir, text_editor)


def _run_command_process(args) -> int:
    schema_file = get_one_of(args, "--schema", "<schemafile>", default=None)
    config_file = get_one_of(args, "--config", "<configfile>", default=None)
    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    variables = get_one_of(args, "--vars", "<vars,...>", default=None)
    if variables:
        variables = [v.strip() for v in variables.split(",") if v.strip()]
    else:
        variables = None

    from amake.tools import run_processors

    return run_processors(schema_file, config_file, current_dir, variables)


def _run_command_generate(args) -> int:
    schema_file = get_one_of(args, "--schema", "<schemafile>", default=None)
    config_file = get_one_of(args, "--config", "<configfile>", default=None)
    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    output_file = get_one_of(args, "--output", "<outputfile>", default=None)
    no_confirm = any_true(args, "--yes", "-Y")

    from amake.tools import generate_build_script

    return generate_build_script(
        schema_file, config_file, current_dir, output_file, no_confirm
    )


def _run_command_appconfig(args) -> int:
    global _app_config
    from amake.utils import parse_key_value_pairs

    from amake.tools import (
        appconfig_list,
        appconfig_edit,
        appconfig_reset,
        appconfig_set,
    )

    if any_true(args, "--list"):
        return appconfig_list(_app_config)

    if any_true(args, "--edit"):
        return appconfig_edit(_app_config)

    if any_true(args, "--reset"):
        no_confirm = any_true(args, "--yes", "-Y")
        return appconfig_reset(_app_config, no_confirm)

    if any_true(args, "--set"):
        print("Setting app configs...")
        config_paris_str = get_one_of(args, "--set", "<config-paris>", default=None)
        if not config_paris_str.strip():
            print("Please specify config-paris!")
            return -1

        try:
            config_paris = parse_key_value_pairs(config_paris_str)
        except Exception as e:
            print(f"Failed to parse config-paris: {e}")
            return -1
        if not config_paris:
            print("No config-paris specified!")
            return -1
        return appconfig_set(_app_config, config_paris)

    return -1


def main():
    from amake.thirdparty.docopt import docopt

    doc = __doc__.strip()
    args = docopt(doc, version=f"{__APP_NAME__} {__APP_VERSION__}")
    if not args:
        return 1

    if all_false(args, *ALL_COMMANDS):
        return _run_amake(args)

    if args.get("init", True):
        return _run_command_init(args)

    if args.get("init-config", True):
        return _run_command_init_config(args)

    if args.get("edit", True):
        return _run_command_edit(args)

    if args.get("process", True):
        return _run_command_process(args)

    if args.get("generate", True):
        return _run_command_generate(args)

    if args.get("appconfig", True):
        return _run_command_appconfig(args)

    return -1


if __name__ == "__main__":
    sys.exit(main())
