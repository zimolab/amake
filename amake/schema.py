import dataclasses
import time
from typing import List, Dict, Union, Any, Optional, Iterable, Tuple

from pyguiadapterlite import BaseParameterWidgetConfig

from .common import VariableTypes, Serializable
from .makeoptions import MakeOptions
from .processor import ProcessorExecutor
from .variable import analyze_variable, KEY_VAR_TYPE, KEY_VAR_PROC

CLASSIC_VARIABLES_DEF = {
    "BINARY": {
        "__type__": "str",
        "__processor__": "",
        "label": "Binary Name",
        "default_value": "myapp",
        "group": "Project",
    },
    "SRCDIR": {
        "__type__": "dir_t",
        "__processor__": "",
        "label": "Source Directory",
        "default_value": "src/",
        "group": "Project",
    },
    "BUILDDIR": {
        "__type__": "dir_t",
        "__processor__": "",
        "label": "Build Directory",
        "default_value": "build/",
        "group": "Project",
    },
    "OBJDIR": {
        "__type__": "dir_t",
        "__processor__": "",
        "label": "Object Directory",
        "default_value": "build/objs",
        "group": "Project",
    },
    "BINDIR": {
        "__type__": "dir_t",
        "__processor__": "",
        "label": "Binary Directory",
        "default_value": "build/bin",
        "group": "Project",
    },
    "INSTALLDIR": {
        "__type__": "dir_t",
        "__processor__": "",
        "label": "Install Directory",
        "default_value": "/usr/local",
        "group": "Project",
    },
    "CC": {
        "__type__": "file_t",
        "__processor__": "",
        "label": "C Compiler",
        "default_value": "gcc",
        "group": "Toolchain",
        "description": "The C compiler to use",
    },
    "CXX": {
        "__type__": "file_t",
        "__processor__": "",
        "label": "C++ Compiler",
        "default_value": "g++",
        "group": "Toolchain",
        "description": "The C++ compiler to use",
    },
    "AR": {
        "__type__": "file_t",
        "__processor__": "",
        "label": "Archiver",
        "default_value": "ar",
        "group": "Toolchain",
        "description": "The archiver to use",
    },
    "CFLAGS": {
        "__type__": "str",
        "__processor__": "strip",
        "label": "C Compiler Flags",
        "default_value": "-Wall -Wextra -Werror",
        "group": "Toolchain",
        "description": "The C compiler flags to use",
    },
    "CXXFLAGS": {
        "__type__": "str",
        "__processor__": "strip",
        "label": "C++ Compiler Flags",
        "default_value": "-Wall -Wextra -Werror",
        "group": "Toolchain",
        "description": "The C++ compiler flags to use",
    },
    "LDFLAGS": {
        "__type__": "str",
        "__processor__": "strip",
        "label": "Linker Flags",
        "default_value": "",
        "group": "Toolchain",
        "description": "The linker flags to use",
    },
    "INCDIR": {
        "__type__": "dirs_t",
        "__processor__": "strip_each|no_empty|prefix_each '-I' |join",
        "label": "Include Search Paths",
        "default_value": ["include/"],
        "normalize_path": False,
        "absolutize_path": False,
        "dir_dialog_title": "Add Include Search Path",
        "add_dir_button_text": "Add Include Path",
        "group": "Includes",
    },
    "LIBDIR": {
        "__type__": "dirs_t",
        "__processor__": "strip_each|no_empty|prefix_each '-L' |join",
        "label": "Library Search Paths",
        "default_value": [],
        "normalize_path": False,
        "absolutize_path": False,
        "dir_dialog_title": "Add Library Search Path",
        "add_dir_button_text": "Add Library Path",
        "group": "Libraries",
    },
    "LIBS": {
        "__type__": "string_list_t",
        "__processor__": "strip_each|no_empty|prefix_each '-l' |join",
        "label": "Libraries",
        "default_value": ["m", "pthread", "dl"],
        "group": "Libraries",
    },
}


@dataclasses.dataclass
class AmakeSchema(Serializable):
    version: str = "1.0.0"
    author: str = ""
    created_at: str = ""
    description: str = ""
    website: str = ""
    targets: List[str] = dataclasses.field(default_factory=list)
    default_target: str = ""
    variables: Dict[str, Union[VariableTypes, Dict[str, Any]]] = dataclasses.field(
        default_factory=dict
    )

    def __post_init__(self):
        super().__post_init__()
        self._parameter_configs: Optional[Dict[str, BaseParameterWidgetConfig]] = {}
        self._variable_processors: Optional[Dict[str, str]] = {}
        self._variable_typenames: Optional[Dict[str, str]] = {}

        self._update()

    @property
    def parameter_configs(self) -> Dict[str, BaseParameterWidgetConfig]:
        return self._parameter_configs.copy()

    @property
    def variable_processors(self) -> Dict[str, str]:
        return self._variable_processors.copy()

    def processor_of(self, variable_name: str) -> str:
        return self._variable_processors.get(variable_name, "")

    def default_value_of(self, variable_name: str) -> Any:
        conf = self._parameter_configs.get(variable_name, None)
        if not conf:
            return None
        return conf.default_value

    def has_variable(self, variable_name: str) -> bool:
        return variable_name in self._parameter_configs

    def check_conflicts(self, variable_names: Iterable[str]) -> List[str]:
        conflicts = []
        for name in variable_names:
            if name in self._parameter_configs:
                conflicts.append(name)
        return conflicts

    def run_processor_on(
        self,
        executor: ProcessorExecutor,
        variable_name: str,
        initial_value: Any,
        debug: bool = False,
    ) -> Any:
        processor = self.processor_of(variable_name)
        if not processor:
            return initial_value
        return executor.execute(processor, initial_value, debug)

    def get_processed_values(
        self,
        executor: ProcessorExecutor,
        variables: Dict[str, Any],
        debug: bool = False,
    ) -> Dict[str, Any]:
        processed = {}
        for var_name, var_val in variables.items():
            processor = self.processor_of(var_name)
            if processor:
                var_val = executor.execute(processor, var_val, debug)
            processed[var_name] = var_val
        return processed

    @classmethod
    def default(cls) -> "AmakeSchema":
        return cls(
            version="1.0.0",
            author="amake",
            created_at=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            description="a blank amake schema",
            targets=[],
            default_target="",
            variables={},
        )

    @classmethod
    def classic(cls) -> "AmakeSchema":
        return cls(
            version="1.0.0",
            author="amake",
            created_at=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            description="a classic amake schema",
            targets=["all", "clean", "install"],
            default_target="all",
            variables=CLASSIC_VARIABLES_DEF,
        )

    @classmethod
    def from_variable_definitions(
        cls, variable_definitions: Dict[str, Dict[str, Any]], **kwargs: Any
    ) -> "AmakeSchema":
        return cls(**kwargs, variables=variable_definitions)

    def to_variable_definitions(
        self, ignored_props: Tuple[str, ...] = None
    ) -> Dict[str, Dict[str, Any]]:
        ignored_props = ignored_props or ()
        ret = {}
        for varname, param_config in self._parameter_configs.items():
            ret[varname] = {
                KEY_VAR_TYPE: self._variable_typenames[varname],
                KEY_VAR_PROC: self._variable_processors.get(varname, ""),
                **{
                    k: v
                    for k, v in dataclasses.asdict(param_config).items()
                    if k not in ignored_props
                },
            }
        return ret

    def _update(self):
        self._parameter_configs.clear()
        for varname, var_def in self.variables.items():
            variable = analyze_variable(var_def)
            self._parameter_configs[varname] = variable.parameter_config
            self._variable_processors[varname] = variable.processor
            self._variable_typenames[varname] = variable.typename


@dataclasses.dataclass
class AmakeConfigurations(Serializable):
    version: str = "1.0.0"
    target: str = ""
    options: Dict[str, Any] = dataclasses.field(default_factory=dict)
    variables: Dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def make_from_schema(cls, schema: AmakeSchema):
        options = {}
        for opt_name, opt_var in MakeOptions().variables().items():
            opt_val = opt_var.parameter_config.default_value
            options[opt_name] = opt_val

        variables = {}
        for var_name, var in schema.parameter_configs.items():
            variables[var_name] = var.default_value

        return cls(
            version=schema.version,
            target=schema.default_target,
            options=options,
            variables=variables,
        )
