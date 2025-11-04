from typing import Dict, Any, List, Iterable

from pyguiadapterlite import BaseParameterWidgetConfig

from . import common
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
        tr_ = common.trfunc()

        self.GROUP_NAME = tr_("Make Options")

        _MSG_YES = tr_("Yes")
        _MSG_NO = tr_("No")

        self._options = {
            MAKE_OPT_MAKE_BIN_KEY: {
                "__type__": "file_t",
                "__processor__": "strip | posixpath",
                "label": tr_("make command"),
                "default_value": "make",
                "description": tr_("make command or path to make executable."),
            },
            MAKE_OPT_OVERRIDE_KEY: {
                "__type__": "bool",
                "__processor__": "to_bool",
                "default_value": True,
                "label": tr_("override makefile variables"),
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "description": tr_(
                    "override makefile variables with the same name using -e option."
                ),
            },
            MAKE_OPT_DEBUG_KEY: {
                "__type__": "loose_choice_t",
                "__processor__": "strip | prefix_ifneq '' '--debug='",
                "label": tr_("debug level(--debug)"),
                "choices": ["", "a", "b", "v", "i", "j", "m"],
                "default_value": "",
                "readonly": True,
                "description": tr_("debug level of make."),
            },
            MAKE_OPT_DIR_KEY: {
                "__type__": "directory_t",
                "__processor__": "strip | posixpath | prefix_ifneq '' '--directory='",
                "label": "makefile directory(--directory)",
                "default_value": "",
                "description": tr_("the directory where makefile is located."),
            },
            MAKE_OPT_MAKEFILE_KEY: {
                "__type__": "file_t",
                "__processor__": "strip | posixpath | prefix_ifneq '' '--makefile='",
                "label": tr_("makefile(--makefile)"),
                "default_value": "",
                "filters": [(tr_("Makefile"), "Makefile"), ("All Files", "*.*")],
                "description": tr_("the makefile to be used."),
            },
            MAKE_OPT_INCLUDE_DIR_KEY: {
                "__type__": "dir_list_t",
                "__processor__": "no_empty | posixpath_each | pretend_each '-I'",
                "default_value": [],
                "label": tr_("include directories(--include-dir)"),
                "content_title": tr_("Include Directory List"),
                "hide_label": False,
                "description": tr_("directories to search for makefiles."),
            },
            MAKE_OPT_JOBS_KEY: {
                "__type__": "int_r",
                "__processor__": "to_str | strip | prefix_ifneq '' '--jobs='",
                "label": tr_("jobs count(--jobs)"),
                "default_value": 1,
                "min_value": 1,
                "max_value": 9999,
                "description": tr_("number of jobs to run simultaneously."),
            },
            MAKE_OPT_ALWAYS_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--always-make' ''",
                "label": tr_("always make(--always-make)"),
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": tr_(
                    "always remake everything, even if the target is up to date."
                ),
            },
            MAKE_OPT_IGNORE_ERRORS_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--ignore-errors' ''",
                "label": tr_("ignore errors(--ignore-errors)"),
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": tr_("ignore errors and keep going."),
            },
            MAKE_OPT_DRY_RUN_KEY: {
                "__type__": "bool",
                "__processor__": "ifelse '--dry-run' ''",
                "label": tr_("dry run(--dry-run)"),
                "true_text": _MSG_YES,
                "false_text": _MSG_NO,
                "default_value": False,
                "description": tr_("don't actually run any commands."),
            },
            MAKE_OPT_EXTRA_KEY: {
                "__type__": "text_t",
                "__processor__": "strip",
                "label": tr_("extra options "),
                "default_value": "",
                "height": 3,
                "description": tr_("extra options to be passed to make command."),
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
