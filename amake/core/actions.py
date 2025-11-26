import shlex
import subprocess
import sys
import traceback
import webbrowser
from functools import partial
from typing import List, Optional

from pyguiadapterlite import (
    FnExecuteWindow,
    Action,
    Menu,
    Separator as MenuSeparator,
    SettingsWindow,
)
from pyguiadapterlite.components.textview import SimpleTextViewer

from ._aboutdlg import AboutDialog, AboutSchemaDialog
from .cmd import AmakeCommand
from .widgets import AmakeWidgets
from .. import assets
from .._messages import messages
from ..appsettings import AmakeAppSettings
from ..makeoptions import MAKE_OPT_MAKE_BIN_KEY, MakeOptions
from ..processor import ProcessorExecutor
from ..schema import AmakeSchema, AmakeConfigurations
from ..utils import move_to_center_of

ACTION_ID_EDIT_APPSETTINGS = "edit_app_configs"
ACTION_ID_RESET_APP_CONFIGS = "reset_app_configs"

AMAKE_LICENSE_FILE = "LICENSE"


def _run_cmd_simple(
    cmd: List[str],
    window: FnExecuteWindow,
    print_cmdline=True,
    print_output=True,
    print_return_code=True,
    show_error=True,
):
    msgs = messages()
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
    HIDDEN_APPSETTINGS_FIELDS = (AmakeAppSettings.always_on_top,)

    def __init__(
        self,
        *,
        appsettings: AmakeAppSettings,
        schema: AmakeSchema,
        configurations: AmakeConfigurations,
        widgets: AmakeWidgets,
        processor_executor: ProcessorExecutor,
    ):

        self._msgs = messages()

        self._appsettings = appsettings

        self._visible_fields = {
            field_name: field_def
            for field_name, field_def in AmakeAppSettings.fields().items()
            if field_def not in self.__class__.HIDDEN_APPSETTINGS_FIELDS
        }

        self._schema = schema
        self._configurations = configurations
        self._widgets = widgets
        self._processor_executor = processor_executor

        self._menus = []

    def create(self) -> List[Menu]:
        if self._menus:
            return self._menus
        file_actions = [
            Action(self._msgs.MSG_ACTION_SAVE_CONFIGS, self.on_save_configurations),
            Action(self._msgs.MSG_ACTION_LOAD_CONFIGS, self.on_load_configurations),
            MenuSeparator(),
            Action(self._msgs.MSG_ACTION_QUIT, self.quit),
        ]
        menu_file = Menu(title=self._msgs.MSG_MENU_FILE, actions=file_actions)

        tools_actions = [
            Action(self._msgs.MSG_ACTION_TEST_MAKE_CMD, self.test_make_command),
            Action(self._msgs.MSG_ACTION_PRINT_MAKE_HELP, self.print_make_help),
            MenuSeparator(),
            Action(self._msgs.MSG_ACTION_GENERATE_CMD, self.generate_command_line),
            Action(
                self._msgs.MSG_ACTION_GENERATE_BUILD_SCRIPT, self.export_build_script
            ),
            MenuSeparator(),
            Action(
                self._msgs.MSG_EDIT_APPSETTINGS,
                on_triggered=self.show_appsettings_window,
                data=ACTION_ID_EDIT_APPSETTINGS,
            ),
            # Action(
            #     msgs.MSG_RESET_APP_CONFIGS,
            #     on_triggered=self._reset_app_configs,
            #     data=ACTION_ID_RESET_APP_CONFIGS,
            # ),
        ]
        menu_tools = Menu(title=self._msgs.MSG_MENU_TOOLS, actions=tools_actions)

        menu_view = Menu(
            title=self._msgs.MSG_MENU_VIEW,
            actions=[
                Action(
                    self._msgs.MSG_ACTION_ALWAYS_ON_TOP,
                    self.set_always_on_top,
                    checkable=True,
                    initial_checked=self._appsettings.always_on_top,
                )
            ],
        )

        menu_help = Menu(
            title=self._msgs.MSG_MENU_HELP,
            actions=[
                Action(self._msgs.MSG_ACTION_ABOUT, self.show_about_dialog),
                Action(self._msgs.MSG_ACTION_LICENSE, self.show_license_dialog),
                MenuSeparator(),
                Action(
                    self._msgs.MSG_ACTION_ABOUT_SCHEMA,
                    on_triggered=self.show_about_schema_dialog,
                ),
            ],
        )

        if self._schema.website:
            menu_help.actions.append(
                Action(
                    self._msgs.MSG_ACTION_SCHEMA_WEBSITE,
                    on_triggered=self.goto_schema_website,
                )
            )

        self._menus.extend([menu_file, menu_tools, menu_view, menu_help])
        return self._menus

    def on_save_configurations(self, window: FnExecuteWindow, action: Action):
        window.close_param_validation_win()
        ret = self.update_and_save_configurations(window)
        if ret:
            window.show_information(
                message=self._msgs.MSG_CONFIGS_SAVE_SUCCESS,
                title=self._msgs.MSG_SUCCESS_DIALOG_TITLE,
            )
        else:
            window.show_error(
                message=self._msgs.MSG_CONFIGS_SAVE_FAILURE,
                title=self._msgs.MSG_FAILURE_DIALOG_TITLE,
            )

    def print_make_help(self, window: FnExecuteWindow, action: Action):
        if window.is_function_executing():
            window.show_warning(
                message=self._msgs.MSG_WAIT_EXECUTION_DONE,
                title=self._msgs.MSG_WARNING_DIALOG_TITLE,
            )
            return
        window.close_param_validation_win()
        window.show_output_tab()
        make_bin = window.get_parameter_values().get(MAKE_OPT_MAKE_BIN_KEY, "make")
        cmd = [make_bin, "--help"]
        _run_cmd_simple(
            cmd, window, print_cmdline=True, show_error=True, print_output=True
        )

    def test_make_command(self, window: FnExecuteWindow, action: Action):
        if window.is_function_executing():
            window.show_warning(
                message=self._msgs.MSG_WAIT_EXECUTION_DONE,
                title=self._msgs.MSG_WARNING_DIALOG_TITLE,
            )
            return
        window.close_param_validation_win()
        window.show_output_tab()
        make_bin = window.get_parameter_values().get(MAKE_OPT_MAKE_BIN_KEY, "make")
        cmd = [make_bin, "--version"]
        _run_cmd_simple(
            cmd, window, print_cmdline=True, show_error=True, print_output=True
        )

    @staticmethod
    def quit(window: FnExecuteWindow, action: Action):
        window.close()

    def set_always_on_top(self, window: FnExecuteWindow, action: Action):
        self._appsettings.always_on_top = action.is_checked()
        window.set_always_on_top(self._appsettings.always_on_top)

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

    def update_ui_from_configurations(
        self, window: FnExecuteWindow, configrations: AmakeConfigurations
    ):
        window.set_parameter_values(
            {
                **configrations.options,
                **configrations.variables,
            }
        )
        self._widgets.set_current_target(configrations.target)
        self.update_configurations(window)

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
            window.print(
                self._msgs.MSG_MAKE_CMD.ljust(12), ":", cmd.to_command_string()
            )
            window.print()

            window.print(self._msgs.MSG_MAKE_TARGET.ljust(12), ":", cmd.make_target)
            window.print()

            window.print(self._msgs.MSG_MAKE_OPTIONS.ljust(12), ":")
            for opt in cmd.make_options:
                if not opt:
                    continue
                window.print(f"  {opt}")
            window.print()

            window.print(self._msgs.MSG_VARIABLES.ljust(12), ":")
            for name, value in cmd.user_variables.items():
                window.print(f"  {name} = {value}")
            window.print()

            window.print(
                self._msgs.MSG_OVERRIDE_VARIABLES.ljust(12),
                ":",
                str(cmd.override_variables),
            )
            window.print()

            window.print(self._msgs.MSG_CMD_LINE.ljust(12), ":")
            window.print(cmd.to_command_string())
            window.print()

            window.print("=" * 80)
        except Exception as e:

            window.print(self._msgs.MSG_FAILED_TO_GENERATE_CMD, ":", str(e))
            window.print()
            window.print("=" * 80)
            window.show_error(message=str(e))

    def export_build_script(self, window: FnExecuteWindow, action: Action):
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
                title=self._msgs.MSG_GENERATE_SCRIPT_DIALOG_TITLE,
                initialfile="build.sh",
                filetypes=[
                    (self._msgs.MSG_SHELL_SCRIPT_FILE_TYPE, "*.sh"),
                    (self._msgs.MSG_ALL_FILE_TYPE, "*.*"),
                ],
            )
            if not filepath:
                return
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(script)
            msg = self._msgs.MSG_BUILD_SCRIPT_GENERATED + filepath
            window.print(msg)
            window.show_information(msg)
        except Exception as e:
            msg = self._msgs.MSG_FAILED_TO_GENERATE_SCRIPT + str(e)
            window.print(msg)
            window.show_error(msg)
            traceback.print_exc()

    def on_load_configurations(self, window: FnExecuteWindow, action: Action):
        try:
            filepath = window.select_open_file(
                title=self._msgs.MSG_LOAD_CONFIGS_DIALOG_TITLE,
                filetypes=[
                    (self._msgs.MSG_CONFIGS_FILE_FILTER, "*.config.json"),
                    (self._msgs.MSG_JSON_FILE_FILTER, "*.json"),
                    (self._msgs.MSG_ALL_FILE_TYPE, "*.*"),
                ],
            )
            if not filepath:
                return
            new_configs = AmakeConfigurations.load(filepath)
            self.update_ui_from_configurations(window, new_configs)
        except Exception as e:
            window.show_error(
                message=self._msgs.MSG_CONFIGS_LOAD_FAILURE,
                title=self._msgs.MSG_FAILURE_DIALOG_TITLE,
                detail=str(e),
            )

    def show_about_dialog(self, window: FnExecuteWindow, action: Action):
        window.show_custom_dialog(AboutDialog, title=self._msgs.MSG_ABOUT_DIALOG_TITLE)

    def show_about_schema_dialog(self, window: FnExecuteWindow, action: Action):
        window.show_custom_dialog(
            AboutSchemaDialog,
            title=self._msgs.MSG_ABOUT_SCHEMA_TITLE,
            schema=self._schema,
        )

    def show_license_dialog(self, window: FnExecuteWindow, action: Action):
        try:
            text = assets.read_asset_text(AMAKE_LICENSE_FILE)
        except Exception as e:
            print(e, file=sys.stderr)
            window.show_error(
                message=self._msgs.MSG_NO_LICENSE_FILE,
                title=self._msgs.MSG_ERROR_DIALOG_TITLE,
            )
            return

        viewer = SimpleTextViewer(
            title=self._msgs.MSG_LICENSE_DIALOG_TITLE, width=825, height=600
        )
        move_to_center_of(viewer, window.parent)
        viewer.set_text(text)
        viewer.show_modal()

    def goto_schema_website(self, window: FnExecuteWindow, action: Action):
        url = (self._schema.website or "").strip()
        if not url:
            window.show_warning("Not Provided!")
            return
        ans = window.ask_yes_no(
            message=self._msgs.MSG_OPEN_SCHEMA_WEBSITE_WARNING + url,
        )
        if not ans:
            return
        webbrowser.open(url)

    def _after_settings_window_confirmed(
        self, window: FnExecuteWindow, appsettings: AmakeAppSettings
    ):
        try:
            appsettings.save()
        except BaseException as e:
            window.show_error(self._msgs.MSG_SAVE_SETTINGS_ERROR, detail=str(e))
        else:
            window.show_information(self._msgs.MSG_SETTINGS_SAVED)

    def show_appsettings_window(self, window: FnExecuteWindow, action: Action):
        window.show_sub_window(
            SettingsWindow,
            config=None,
            modal=True,
            settings=self._appsettings,
            setting_fields=self._visible_fields,
            after_save_callback=partial(self._after_settings_window_confirmed, window),
        )

    # def _reset_app_configs(self, window: FnExecuteWindow, action: Action):
    #     from ..tools import appconfig_reset
    #
    #     msgs = messages()
    #     if not window.ask_yes_no(
    #         message=msgs.MSG_ASK_RESET_APP_CONFIGS, title=msgs.MSG_CONFIRM_DIALOG_TITLE
    #     ):
    #         return
    #     appconfig_reset(self._appsettings, no_confirm=True)
    #     self._action_handler(window, action)
