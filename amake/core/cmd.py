import shlex
from typing import List, Dict

from ..makeoptions import MAKE_OPT_MAKE_BIN_KEY, MAKE_OPT_OVERRIDE_KEY, MakeOptions
from ..processor import ProcessorExecutor
from ..schema import AmakeConfigurations, AmakeSchema


class AmakeCommand(object):
    def __init__(
        self,
        configurations: AmakeConfigurations,
        schema: AmakeSchema,
        processor_executor: ProcessorExecutor,
    ):
        self._make_target = ""
        self._user_variables = {}
        self._make_options = {}
        self._make_bin = ""
        self._override_variables = False

        self._processor_executor = processor_executor
        self._schema = schema

        self.process(configurations)

    @property
    def make_target(self) -> str:
        return self._make_target or ""

    @property
    def make_options(self) -> List[str]:
        return list(self._make_options.values())

    @property
    def user_variables(self) -> Dict[str, str]:
        return self._user_variables.copy()

    @property
    def make_bin(self) -> str:
        return self._make_bin or "make"

    @property
    def override_variables(self) -> bool:
        return self._override_variables

    def process(self, configurations: AmakeConfigurations):
        self._process_make_options(configurations)
        self._process_user_variables(configurations)
        self._make_target = configurations.target

    def _process_user_variables(self, configurations: AmakeConfigurations):
        user_variables = configurations.variables.copy()
        for var_name, var_value in user_variables.items():
            processor = self._schema.processor_of(var_name)
            if not processor:
                self._user_variables[var_name] = var_value
                continue
            processed = self._processor_executor.execute(processor, var_value)
            self._user_variables[var_name] = processed

    def _process_make_options(self, configurations: AmakeConfigurations):
        make_options = configurations.options.copy()

        self._make_bin = make_options.pop(MAKE_OPT_MAKE_BIN_KEY, "make")
        self._override_variables = make_options.pop(MAKE_OPT_OVERRIDE_KEY, False)

        self._make_options = {}
        for opt_name, opt_value in make_options.items():
            processor = MakeOptions().processor_of(opt_name)
            if not processor:
                self._make_options[opt_name] = opt_value
                continue
            processed = self._processor_executor.execute(processor, opt_value)
            self._make_options[opt_name] = processed

    def to_command_list(self) -> List[str]:
        command = [self._make_bin]

        if self._make_target:
            command.append(self._make_target)

        for make_option in self._make_options.values():
            if make_option is None:
                continue

            if not make_option:
                continue

            if isinstance(make_option, (list, tuple, set)):
                command.extend(make_option)
                continue

            command.append(make_option)

        for var_name, var_value in self._user_variables.items():
            if self._override_variables:
                command.append("-e")
            command.append(f"{var_name}={var_value}")

        return command

    def to_command_string(self) -> str:
        return shlex.join(self.to_command_list())
