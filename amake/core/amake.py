import builtins
import subprocess
import time
import traceback
from typing import Optional, Any, Dict

from pyguiadapterlite import (
    FnExecuteWindow,
    GUIAdapter,
    uprint,
    FnExecuteWindowConfig,
    is_function_cancelled,
    Action,
)

from .actions import (
    AmakeActionsManager,
    ACTION_ID_EDIT_APP_CONFIGS,
    ACTION_ID_RESET_APP_CONFIGS,
)
from .cmd import AmakeCommand
from .eventhandler import AmakeEventHandler, EventType
from .widgets import AmakeWidgets
from .. import processors
from .._messages import messages
from ..appconfig import AmakeAppConfig
from ..makeoptions import MakeOptions
from ..processor import ProcessorExecutor
from ..schema import AmakeSchema, AmakeConfigurations


class Amake(object):

    def __init__(
        self,
        app_config: Optional[AmakeAppConfig],
        schema: AmakeSchema,
        configurations: AmakeConfigurations,
    ):
        self._schema = schema
        self._configurations = configurations
        self._app_config = app_config

        self._save_app_config_before_exit = True

        self._gui_adapter: Optional[GUIAdapter] = None

        self._processor_executor = self.create_processor_executor()

        self._widgets = AmakeWidgets()
        self._menu_manager = AmakeActionsManager(
            app_config=self._app_config,
            schema=self._schema,
            configurations=self._configurations,
            widgets=self._widgets,
            processor_executor=self._processor_executor,
            action_handler=self.handle_action_event,
        )
        self._event_handler = AmakeEventHandler()
        self._event_handler.add_event_callback(
            EventType.AFTER_WINDOW_CREATE, self.after_window_create
        )
        self._event_handler.add_event_callback(
            EventType.BEFORE_WINDOW_CLOSE, self.before_window_close
        )
        self._event_handler.add_event_callback(
            EventType.BEFORE_EXECUTE, self.before_execute
        )
        self._event_handler.add_event_callback(
            EventType.AFTER_EXECUTE, self.after_execute
        )

        self._execute_start_time = 0.0

    @property
    def save_app_config_before_exit(self) -> bool:
        return self._save_app_config_before_exit

    @staticmethod
    def _on_run(command: AmakeCommand):

        msgs = messages()

        def _debug_print(msg):
            uprint(f"\033[33m{msg}\033[0m")

        _debug_print(msgs.MSG_RUNNING_COMMAND + command.to_command_string())
        _hinted = False

        process = subprocess.Popen(
            command.to_command_list(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            shell=True,
        )
        while True:
            if process.poll() is not None:
                break
            output = process.stdout.readline()
            if output:
                uprint(output, end="")
            time.sleep(0.01)
            if is_function_cancelled():
                if not _hinted:
                    _debug_print(msgs.MSG_ASK_CANCEL_EXECUTION)
                    _debug_print(msgs.MSG_TERMINATING_PROCESS)
                    _hinted = True
                process.terminate()
        _debug_print(msgs.MSG_PROCESS_FINISHED)
        _debug_print(msgs.MSG_EXIT_CODE + str(process.returncode))

    def after_window_create(self, window: FnExecuteWindow):
        self._widgets.create(window)
        self._widgets.set_targets(self._schema.targets)

        window.clear_output_on_execute.set(self._app_config.clear_output_on_run)
        window.set_always_on_top(self._app_config.always_on_top)

        self._update_ui(window, self._configurations)

    def before_window_close(self, window: FnExecuteWindow) -> bool:
        msgs = messages()

        window.close_param_validation_win()
        ret = window.ask_yes_no_cancel(
            message=msgs.MSG_QUIT_CONFIRMATION,
            title=msgs.MSG_QUIT_DIALOG_TITLE,
        )
        if ret is None:
            return False
        if self._save_app_config_before_exit:
            self.update_and_save_app_config(window)
        if ret:
            return self._menu_manager.update_and_save_configurations(window)
        return True

    # noinspection PyUnusedLocal
    def before_execute(
        self, window: FnExecuteWindow, parameters_values: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # update_configurations()会从当前界面收集参数值，并更新self._configurations
        # 如果发现非法的参数值，该函数会返回False
        # 可以根据该函数的返回值决定是否继续执行
        ret = self._menu_manager.update_configurations(window)
        if not ret:
            # 返回None，终止执行
            return None
        try:
            cmd = AmakeCommand(
                schema=self._schema,
                configurations=self._configurations,
                processor_executor=self._processor_executor,
            )
        except Exception as e:
            traceback.print_exc()
            window.show_error(message=str(e))
            return None
        self._execute_start_time = time.time_ns()
        return {"command": cmd}

    # noinspection PyUnusedLocal
    def after_execute(
        self, window: FnExecuteWindow, result: Any, exception: Optional[Exception]
    ):
        msgs = messages()
        end_execute_time = time.time_ns()
        window.print("=" * 80)
        window.print(
            msgs.MSG_EXECUTION_TIME
            + f"{(end_execute_time - self._execute_start_time)/1e9} s"
        )
        window.print("=" * 80)

    def _update_ui(self, window: FnExecuteWindow, configurations: AmakeConfigurations):
        current_values = {**configurations.variables, **configurations.options}
        window.set_parameter_values(current_values)
        self._widgets.set_current_target(configurations.target)

    def update_app_config(self, window: FnExecuteWindow):
        self._app_config.clear_output_on_run = window.clear_output_on_execute.get()

    def update_and_save_app_config(self, window: FnExecuteWindow):
        self.update_app_config(window)
        self._app_config.save(encoding="utf-8", indent=2, ensure_ascii=False)

    def run(self):
        parameter_configs = {
            **self._schema.parameter_configs,
            **MakeOptions().parameter_configs,
        }

        msg = messages()

        title = getattr(builtins, "_amake_app_name", "amake")
        if self._configurations.filepath:
            title += f" - {self._configurations.filepath}"

        adapter = GUIAdapter()
        self._gui_adapter = adapter
        adapter.add_universal(
            self._on_run,
            cancelable=True,
            document=self._schema.description,
            before_execute_callback=self._event_handler.before_execute,
            after_execute_callback=self._event_handler.after_execute,
            window_config=FnExecuteWindowConfig(
                title=title,
                execute_button_text=msg.MSG_EXE_BTN_TEXT,
                cancel_button_text=msg.MSG_CANCEL_BTN_TEXT,
                clear_button_text=msg.MSG_CLEAR_BTN_TEXT,
                clear_checkbox_text=msg.MSG_CLEAR_CHECKBOX_TEXT,
                after_window_create_callback=self._event_handler.after_window_create,
                before_window_close_callback=self._event_handler.before_window_close,
                print_function_result=False,
                show_function_result=False,
                output_tab_title=msg.MSG_OUTPUT_TAB_TITLE,
                document_tab_title=msg.MSG_DOCUMENT_TAB_TITLE,
                default_parameter_group_name=msg.MSG_DEFAULT_PARAM_GROUP_NAME,
                menus=self._menu_manager.create(),
            ),
            parameter_configs=parameter_configs,
        )
        adapter.run()
        self._gui_adapter = None

    def handle_action_event(self, window: FnExecuteWindow, action: Action):
        msgs = messages()
        if action.data in [ACTION_ID_EDIT_APP_CONFIGS, ACTION_ID_RESET_APP_CONFIGS]:
            window.show_information(
                message=msgs.MSG_APP_CONFIGS_CHANGE_INFO,
                title=msgs.MSG_INFO_DIALOG_TITLE,
            )
            self._save_app_config_before_exit = False
            return

    @staticmethod
    def create_processor_executor() -> ProcessorExecutor:
        executor = ProcessorExecutor()
        builtin_processors = processors.get_builtins()
        for processor_name, processor_func in builtin_processors.items():
            executor.register(func=processor_func, name=processor_name)
        return executor
