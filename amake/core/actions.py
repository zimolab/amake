import builtins
import shlex
import subprocess
import traceback
import webbrowser
from typing import List, Optional

from pyguiadapterlite import FnExecuteWindow, Action, Menu, Separator as MenuSeparator

from .cmd import AmakeCommand
from .widgets import AmakeWidgets
from .. import common
from .._messages import Messages
from ..appconfig import AmakeAppConfig
from ..makeoptions import MAKE_OPT_MAKE_BIN_KEY, MakeOptions
from ..processor import ProcessorExecutor
from ..schema import AmakeSchema, AmakeConfigurations

AMAKE_APP_NAME = getattr(builtins, "_amake_app_name", "amake")
AMAKE_APP_VERSION = getattr(builtins, "_amake_app_version", "0.0.0")


def _run_cmd_simple(
    cmd: List[str],
    window: FnExecuteWindow,
    print_cmdline=True,
    print_output=True,
    print_return_code=True,
    show_error=True,
):
    msgs = Messages()
    if print_cmdline:
        window.print()
        window.print(shlex.join(cmd))
        window.print()
    try:
        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8")

        if print_output:
            window.print(output)
        if print_return_code:
            window.print(msgs.MSG_EXIT_CODE + str(result.returncode))
        window.print("=" * 80)
    except BaseException as e:
        window.print(msgs.MSG_COMMAND_FAILED + str(e))
        window.print("=" * 80)
        if show_error:
            window.show_error(message=str(e))


# noinspection PyUnusedLocal
class AmakeActionsManager(object):
    def __init__(
        self,
        *,
        app_config: AmakeAppConfig,
        schema: AmakeSchema,
        configurations: AmakeConfigurations,
        widgets: AmakeWidgets,
        processor_executor: ProcessorExecutor,
    ):
        self._app_config = app_config
        self._schema = schema
        self._configurations = configurations
        self._widgets = widgets
        self._processor_executor = processor_executor

        self._menus = []

    def create(self) -> List[Menu]:
        tr_ = common.trfunc()
        msgs = Messages()
        if self._menus:
            return self._menus
        file_actions = [
            Action(msgs.MSG_ACTION_SAVE_CONFIGS, self.on_save_configurations),
            Action(msgs.MSG_ACTION_LOAD_CONFIGS, self.load_configurations),
            MenuSeparator(),
            Action(msgs.MSG_ACTION_QUIT, self.quit),
        ]
        menu_file = Menu(title=msgs.MSG_MENU_FILE, actions=file_actions)

        tools_actions = [
            Action(msgs.MSG_ACTION_TEST_MAKE_CMD, self.test_make_command),
            Action(msgs.MSG_ACTION_PRINT_MAKE_HELP, self.print_make_help),
            Action(msgs.MSG_ACTION_GENERATE_CMD, self.generate_command_line),
            Action(msgs.MSG_ACTION_GENERATE_BUILD_SCRIPT, self.export_build_script),
        ]
        menu_tools = Menu(title=msgs.MSG_MENU_TOOLS, actions=tools_actions)

        menu_view = Menu(
            title=msgs.MSG_MENU_VIEW,
            actions=[
                Action(
                    msgs.MSG_ACTION_ALWAYS_ON_TOP,
                    self.set_always_on_top,
                    checkable=True,
                    initial_checked=self._app_config.always_on_top,
                )
            ],
        )

        menu_help = Menu(
            title=msgs.MSG_MENU_HELP,
            actions=[
                Action(msgs.MSG_ACTION_ABOUT, self.show_about_dialog),
                Action(msgs.MSG_ACTION_LICENSE, self.show_license_dialog),
            ],
        )

        if self._schema.website:
            menu_help.actions.append(MenuSeparator())
            menu_help.actions.append(
                Action(
                    msgs.MSG_ACTION_SCHEMA_WEBSITE,
                    on_triggered=lambda w, a: self._open_url(self._schema.website),
                )
            )

        self._menus.extend([menu_file, menu_tools, menu_view, menu_help])
        return self._menus

    def on_save_configurations(self, window: FnExecuteWindow, action: Action):
        msgs = Messages()
        window.close_param_validation_win()
        ret = self.update_and_save_configurations(window)
        if ret:
            window.show_information(
                message=msgs.MSG_CONFIGS_SAVE_SUCCESS,
                title=msgs.MSG_SUCCESS_DIALOG_TITLE,
            )
        else:
            window.show_error(
                message=msgs.MSG_CONFIGS_SAVE_FAILURE,
                title=msgs.MSG_FAILURE_DIALOG_TITLE,
            )

    @staticmethod
    def print_make_help(window: FnExecuteWindow, action: Action):
        tr_ = common.trfunc()
        if window.is_function_executing():
            window.show_warning(
                message=tr_("Please wait for the current execution to finish.")
            )
            return
        window.close_param_validation_win()
        window.show_output_tab()
        window.print(tr_("Printing make help..."))
        make_bin = window.get_parameter_values().get(MAKE_OPT_MAKE_BIN_KEY, "make")
        cmd = [make_bin, "--help"]
        _run_cmd_simple(
            cmd, window, print_cmdline=True, show_error=True, print_output=True
        )

    @staticmethod
    def test_make_command(window: FnExecuteWindow, action: Action):
        tr_ = common.trfunc()
        if window.is_function_executing():
            window.show_warning(
                message=tr_("Please wait for the current execution to finish.")
            )
            return
        window.close_param_validation_win()
        window.show_output_tab()
        window.print(tr_("Test make command..."))
        make_bin = window.get_parameter_values().get(MAKE_OPT_MAKE_BIN_KEY, "make")
        cmd = [make_bin, "--version"]
        _run_cmd_simple(
            cmd, window, print_cmdline=True, show_error=True, print_output=True
        )

    @staticmethod
    def quit(window: FnExecuteWindow, action: Action):
        window.close()

    def set_always_on_top(self, window: FnExecuteWindow, action: Action):
        self._app_config.always_on_top = action.is_checked()
        window.set_always_on_top(self._app_config.always_on_top)

    def update_configurations(self, window: FnExecuteWindow) -> bool:
        parameters_values = window.get_parameter_values()
        if not window.check_invalid_parameters(parameters_values):
            return False

        options = {}
        variables = {}
        for name, value in parameters_values.items():
            if name in self._schema.parameter_configs.keys():
                variables[name] = value
            if name in MakeOptions().parameter_configs.keys():
                options[name] = value

        self._configurations.options = options
        self._configurations.variables = variables
        self._configurations.target = self._widgets.get_current_target()
        return True

    def save_configurations(self, window: Optional[FnExecuteWindow]) -> bool:
        if not self._configurations.filepath:
            filepath = window.select_save_file()
            if not filepath:
                return False
            self._configurations.save(
                filepath=filepath,
                remember_filepath=True,
                encoding="utf-8",
                indent=4,
                ensure_ascii=False,
            )
            return True
        self._configurations.save(
            encoding="utf-8",
            indent=4,
            ensure_ascii=False,
        )
        return True

    def update_and_save_configurations(self, window: FnExecuteWindow) -> bool:
        if not self.update_configurations(window):
            return False
        return self.save_configurations(window)

    def generate_command_line(self, window: FnExecuteWindow, action: Action):
        window.close_param_validation_win()
        ret = self.update_configurations(window)
        if not ret:
            return
        window.show_output_tab()
        try:
            cmd = AmakeCommand(
                schema=self._schema,
                configurations=self._configurations,
                processor_executor=self._processor_executor,
            )
            window.print(f"Make Command:\n  {cmd.make_bin}")
            window.print()

            window.print(f"Make Target: {cmd.make_target}")
            window.print()

            window.print(f"Make Options:")
            for opt in cmd.make_options:
                if not opt:
                    continue
                window.print(f"  {opt}")
            window.print()

            window.print("Variables:")
            for name, value in cmd.user_variables.items():
                window.print(f"  {name} = {value}")
            window.print()

            window.print(f"Override Variables: {cmd.override_variables}")
            window.print()

            window.print("Command line:")
            window.print(cmd.to_command_string())
            window.print()

            window.print("=" * 80)
        except Exception as e:

            window.print(f"Failed to generate command line: {e}")
            window.print()
            window.print("=" * 80)
            window.show_error(message=str(e))

    def export_build_script(self, window: FnExecuteWindow, action: Action):
        tr_ = common.trfunc()
        window.close_param_validation_win()
        ret = self.update_configurations(window)
        if not ret:
            return
        try:
            cmd = AmakeCommand(
                schema=self._schema,
                configurations=self._configurations,
                processor_executor=self._processor_executor,
            )
            script = cmd.to_command_string()
            filepath = window.select_save_file(
                title=tr_("Export Build Script"),
                initialfile="build.sh",
                filetypes=[(tr_("Shell Script"), "*.sh"), (tr_("All Files"), "*.*")],
            )
            if not filepath:
                return
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(script)
            msg = tr_("Build script exported to ") + filepath
            window.print(msg)
            window.show_information(msg)
        except Exception as e:
            msg = tr_("Failed to export build script: ") + str(e)
            window.print(msg)
            window.show_error(msg)
            traceback.print_exc()

    def load_configurations(self, window: FnExecuteWindow, action: Action):
        pass

    def show_about_dialog(self, window: FnExecuteWindow, action: Action):
        pass

    def show_license_dialog(self, window: FnExecuteWindow, action: Action):
        pass

    @staticmethod
    def _open_url(url: str):
        webbrowser.open_new(url)
