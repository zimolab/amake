from typing import Dict, Any, List, Iterable

from pyguiadapterlite import BaseParameterWidgetConfig

from ._messages import messages
from .variable import Variable, analyze_variable

MAKE_OPT_MAKE_BIN_KEY = "_make_bin"
MAKE_OPT_OVERRIDE_KEY = "_override"
MAKE_OPT_DEBUG_KEY = "_debug"
MAKE_OPT_DIR_KEY = "_directory"
MAKE_OPT_ALWAYS_KEY = "_always_make"
MAKE_OPT_MAKEFILE_KEY = "_makefile"
MAKE_OPT_INCLUDE_DIR_KEY = "_include_dir"
MAKE_OPT_IGNORE_ERRORS_KEY = "_ignore_errors"
MAKE_OPT_JOBS_KEY = "_jobs"
MAKE_OPT_DRY_RUN_KEY = "_dry_run"
MAKE_OPT_EXTRA_KEY = "_extras"


class NoSuchOptionError(Exception):
    pass


class _MakeOptions(object):

    def __init__(self):
        msgs = messages()

        self.GROUP_NAME = msgs.MSG_MKOPTS_GROUP_NAME

        _MSG_YES = msgs.MSG_MKOPTS_YES
        _MSG_NO = msgs.MSG_MKOPTS_NO

        self._options = {
            MAKE_OPT_MAKE_BIN_KEY: {
                "__type__": "file_t",
                "__processor__": "strip | posixpath",
                "label": msgs.MSG_MKOPTS_MKCMD_LABEL,
                "default_value": "make",
                "description": msgs.MSG_MKOPTS_MKCMD_DESC,
            },
            MAKE_OPT_OVERRIDE_KEY: {
                "__type__": "bool",
                "__processor__": "to_bool",
                "default_value": True,
                "label": msgs.MSG_MKOPTS_OVERRIDE_LABEL,
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "description": msgs.MSG_MKOPTS_OVERRIDE_DESC,
            },
            MAKE_OPT_DEBUG_KEY: {
                "__type__": "loose_choice_t",
                "__processor__": "strip | prefix_ifneq '' '--debug='",
                "label": msgs.MSG_MKOPT_DEBUG_LV_LABEL,
                "choices": ["", "a", "b", "v", "i", "j", "m"],
                "default_value": "",
                "readonly": True,
                "description": msgs.MSG_MKOPT_DEBUG_LV_DESC,
            },
            MAKE_OPT_DIR_KEY: {
                "__type__": "directory_t",
                "__processor__": "strip | posixpath | prefix_ifneq '' '--directory='",
                "label": msgs.MSG_MKOPTS_DIR_LABEL,
                "default_value": "",
                "description": msgs.MSG_MKOPTS_DIR_DESC,
            },
            MAKE_OPT_MAKEFILE_KEY: {
                "__type__": "file_t",
                "__processor__": "strip | posixpath | prefix_ifneq '' '--makefile='",
                "label": msgs.MSG_MKOPTS_MAKEFILE_LABEL,
                "default_value": "",
                "filters": [
                    (msgs.MSG_MAKEFILE_TYPE, "Makefile"),
                    (msgs.MSG_ALL_FILE_TYPE, "*.*"),
                ],
                "description": msgs.MSG_MKOPTS_MAKEFILE_DESC,
            },
            MAKE_OPT_INCLUDE_DIR_KEY: {
                "__type__": "dir_list_t",
                "__processor__": "no_empty | posixpath_each | pretend_each '-I'",
                "default_value": [],
                "label": msgs.MSG_MKOPTS_INCLUDE_DIR_LABEL,
                "content_title": msgs.MSG_MKOPTS_INCLUDE_DIR_TITLE,
                "hide_label": False,
                "description": msgs.MSG_MKOPTS_INCLUDE_DIR_DESC,
            },
            MAKE_OPT_JOBS_KEY: {
                "__type__": "int_r",
                "__processor__": "to_str | strip | prefix_ifneq '' '--jobs='",
                "label": msgs.MSG_MKOPTS_JOBS_LABEL,
                "default_value": 1,
                "min_value": 1,
                "max_value": 9999,
                "description": msgs.MSG_MKOPTS_JOBS_DESC,
            },
            MAKE_OPT_ALWAYS_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--always-make' ''",
                "label": msgs.MSG_MKOPTS_ALWAYS_LABEL,
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": msgs.MSG_MKOPTS_ALWAYS_DESC,
            },
            MAKE_OPT_IGNORE_ERRORS_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--ignore-errors' ''",
                "label": msgs.MSG_MKOPTS_IGNORE_ERRORS_LABEL,
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": msgs.MSG_MKOPTS_IGNORE_ERRORS_DESC,
            },
            MAKE_OPT_DRY_RUN_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--dry-run' ''",
                "label": msgs.MSG_MKOPTS_DRY_RUN_LABEL,
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": msgs.MSG_MKOPTS_DRY_RUN_DESC,
            },
            MAKE_OPT_EXTRA_KEY: {
                "__type__": "text_t",
                "__processor__": "strip",
                "label": msgs.MSG_MKOPTS_EXTRA_LABEL,
                "default_value": "",
                "height": 3,
                "description": msgs.MSG_MKOPTS_EXTRA_DESC,
            },
        }

        self._variables: Dict[str, Variable] = {}

    def variables(self) -> Dict[str, Variable]:
        if self._variables:
            return self._variables.copy()
        for opt_name, opt_def in self._options.items():
            var = analyze_variable(opt_def, group=self.GROUP_NAME)
            self._variables[opt_name] = var
        return self._variables.copy()

    def has_option(self, opt_name: str) -> bool:
        return opt_name in self.variables()

    def processor_of(self, opt_name: str) -> str:
        variables = self.variables()
        var = variables.get(opt_name, None)
        if var is None:
            raise NoSuchOptionError(f"No such make option: {opt_name}")
        return var.processor

    def get_default_value(self, opt_name: str) -> Any:
        variables = self.variables()
        var = variables.get(opt_name, None)
        if var is None:
            raise NoSuchOptionError(f"No such make option: {opt_name}")
        return var.parameter_config.default_value

    def get_conflict_names(self, name: Iterable[str]) -> List[str]:
        return [n for n in name if n in self.variables().keys()]

    @property
    def parameter_configs(self) -> Dict[str, BaseParameterWidgetConfig]:
        variables = self.variables()
        return {k: v.parameter_config for k, v in variables.items()}


_make_options = None


def MakeOptions() -> "_MakeOptions":
    global _make_options
    if _make_options is None:
        _make_options = _MakeOptions()
    return _make_options
