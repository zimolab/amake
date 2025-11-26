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
"""

import builtins
import json
import sys
from pathlib import Path
from typing import Optional

from amake.consts import (
    GLOBAL_VARNAME_APPSETTINGS,
    APP_NAME,
    APP_VERSION,
    APP_DATADIR,
    APP_LOCALEDIR,
    APP_SETTINGS_FILE,
    GLOBAL_VARNAME_DEBUG_FUNC,
    GLOBAL_VARNAME_ERROR_FUNC,
    GLOBAL_VARNAME_TR_FUNC,
    GLOBAL_VARNAME_NTR_FUNC,
)

_DEBUG_MODE = True

ALL_COMMANDS = ("edit", "init", "init-config", "process", "generate")


def _debug(msg):
    if not _DEBUG_MODE:
        return
    print(f"[DEBUG] {msg}")


def _error(msg):
    if not _DEBUG_MODE:
        return
    print(f"[ERROR] {msg}")


# Add debug functions to builtins, so they can be accessed from anywhere
setattr(builtins, GLOBAL_VARNAME_DEBUG_FUNC, _debug)
setattr(builtins, GLOBAL_VARNAME_ERROR_FUNC, _error)


def _setup_app_locale():
    import os
    from amake.i18n import AmakeI18N, DEFAULT_LOCALE_CODE
    from amake import assets

    _debug(f"Initializing app locale...")
    app_locale_dir = Path(APP_LOCALEDIR)

    if _DEBUG_MODE:
        _debug("Remove all locale files in debug mode")
        if app_locale_dir.is_dir():
            import shutil

            shutil.rmtree(app_locale_dir.as_posix(), ignore_errors=True)

    if not app_locale_dir.is_dir():
        _debug(f"Creating app locale directory: {app_locale_dir.as_posix()}")
        app_locale_dir.mkdir(parents=True)

    if not os.listdir(app_locale_dir.as_posix()):
        _debug(f"No locale files found in {app_locale_dir.as_posix()}")
        _debug(f"Copying default locale files to {app_locale_dir.as_posix()}")

        assets.export_builtin_locales(app_locale_dir.as_posix(), overwrite=True)

    lang = DEFAULT_LOCALE_CODE
    try:
        with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
            appsettings_obj = json.load(f)
            lang = str(appsettings_obj.get("locale", DEFAULT_LOCALE_CODE)).strip()
    except Exception as e:
        _error(
            f"Failed to load app settings from file, use default locale: {APP_SETTINGS_FILE}: {e}"
        )

    _debug(f"Setting app locale to:  {lang}")

    i18n = AmakeI18N(localedir=app_locale_dir.as_posix(), locale_code=lang)

    def gettext(string_id: str) -> str:
        if i18n is None:
            return string_id
        return i18n.gettext(string_id)

    def ngettext(singular: str, plural: str, n: int) -> str:
        if i18n is None:
            return singular if n == 1 else plural
        return i18n.ngettext(singular, plural, n)

    # 把当前i18n的翻译函数注入到全局空间
    # 之后，可以使用common.trfunc()/common.ntrfunc()来获取到下面两个翻译函数
    setattr(builtins, GLOBAL_VARNAME_TR_FUNC, gettext)
    setattr(builtins, GLOBAL_VARNAME_NTR_FUNC, ngettext)


_setup_app_locale()


def _load_appsettings():
    from amake.appsettings import AmakeAppSettings

    _debug(f"Loading app config from: {APP_SETTINGS_FILE}")
    appsettings_path = Path(APP_SETTINGS_FILE)
    if not appsettings_path.is_file():
        _debug(f"App settings file not found")
        appsettings = AmakeAppSettings.default()
        _debug(f"Creating new app settings file: {appsettings_path.as_posix()}")
        appsettings_path.parent.mkdir(parents=True, exist_ok=True)
        appsettings.save(appsettings_path.as_posix())
        return appsettings
    try:
        appsettings = AmakeAppSettings.load(appsettings_path.as_posix())
        return appsettings
    except Exception as e:
        _error(
            f"Failed to load app settings from file: {appsettings_path.as_posix()}: {e}"
        )
        appsettings = AmakeAppSettings.default()
        appsettings.save(appsettings_path.as_posix())
        return appsettings


# Load app config
_appsettings = _load_appsettings()
# add appsettings to builtins, so it can be accessed from anywhere
setattr(builtins, GLOBAL_VARNAME_APPSETTINGS, _appsettings)


def _pyguiadapter_init():
    import pyguiadapterlite

    global _appsettings
    _debug(f"Initializing PyGUIAdapterLite...")

    pyguiadapterlite.set_logging_enabled(False)
    pyguiadapterlite.set_locale_code(_appsettings.locale)
    pyguiadapterlite.set_default_parameter_label_justify("left")


_pyguiadapter_init()


def _check_dirs():
    _debug(f"Checking app data directories...")
    app_data_dir = Path(APP_DATADIR)
    if not app_data_dir.is_dir():
        _debug(f"Creating app data directory: {app_data_dir.as_posix()}")
        app_data_dir.mkdir(parents=True)

    app_locale_dir = Path(APP_LOCALEDIR)
    if not app_locale_dir.is_dir():
        _debug(f"Creating app locale directory: {app_locale_dir.as_posix()}")
        app_locale_dir.mkdir(parents=True)


_check_dirs()


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


def _run_amake_main(args) -> int:

    current_dir = get_one_of(args, "--current-dir", "<dir>", default=None)
    schema_file = get_one_of(args, "--schema", "<schemafile>", default=None)
    config_file = get_one_of(args, "--config", "<configfile>", default=None)

    from amake.tools import amake_main

    return amake_main(schema_file, config_file, current_dir)


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


def main():
    from amake.thirdparty.docopt import docopt

    doc = __doc__.strip()
    args = docopt(doc, version=f"{APP_NAME} {APP_VERSION}")
    if not args:
        return 1

    if all_false(args, *ALL_COMMANDS):
        return _run_amake_main(args)

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

    return -1


if __name__ == "__main__":
    sys.exit(main())
