import os

from amake.thirdparty import platformdirs

APP_NAME = "amake"
APP_AUTHOR = "zimolab"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "A makefile assistant tool to help you write more flexible and maintainable makefiles."
APP_LICENSE = "MIT License"
APP_COPYRIGHT = "Copyright (c) 2025 zimolab"
APP_REPO = "https://github.com/zimolab/amake"

APP_DATADIR = platformdirs.user_data_dir(APP_NAME.lower())
APP_LOCALEDIR = os.path.join(APP_DATADIR, "locales")
APP_SETTINGS_FILE = os.path.join(APP_DATADIR, "amake.settings.json")

GLOBAL_VARNAME_DEBUG_FUNC = "_amake_debug_"
GLOBAL_VARNAME_ERROR_FUNC = "_amake_error_"
GLOBAL_VARNAME_TR_FUNC = "__tr__"
GLOBAL_VARNAME_NTR_FUNC = "__ntr__"
GLOBAL_VARNAME_APPSETTINGS = "_amake_appsettings_"
