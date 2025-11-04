import dataclasses
from typing import Dict, Union, Any

from pyguiadapterlite import ParameterWidgetFactory, BaseParameterWidgetConfig

from .common import VariableTypes, get_default_processor


class VariableTypeNotDefined(Exception):
    pass


class UnsupportedVariableType(Exception):
    pass


class UnknownDefaultValueType(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class Variable(object):
    parameter_config: BaseParameterWidgetConfig
    processor: str
    typename: str


KEY_VAR_TYPE = "__type__"
KEY_VAR_PROC = "__processor__"

AVAILABLE_TYPES = list(ParameterWidgetFactory._registry.keys())


def analyze_variable(
    definition: Union[VariableTypes, Dict[str, Any]], **replacements
) -> Variable:
    if isinstance(definition, dict):
        definition = definition.copy()
        typ = definition.pop(KEY_VAR_TYPE, "")

        if not typ:
            raise VariableTypeNotDefined(
                f"variable type not defined using '{KEY_VAR_TYPE}' field"
            )

        processor = definition.pop(KEY_VAR_PROC, "")
        if not processor:
            processor = get_default_processor(typ)

        config_class = ParameterWidgetFactory.find_by_typename(typ).ConfigClass
        if not config_class:
            raise UnsupportedVariableType(f"unsupported variable type: {typ}")
        config = config_class.new(**definition)
        param_config = config
        var_type = typ
    elif isinstance(definition, (int, float, str, bool)):
        default_value = definition
        default_value_type = type(default_value).__name__
        processor = get_default_processor(default_value_type)

        w = ParameterWidgetFactory.find_by_typename(default_value_type)
        if not w:
            raise UnsupportedVariableType(
                f"unsupported variable type: {default_value_type}"
            )
        config_class = w.ConfigClass
        if not config_class:
            raise UnsupportedVariableType(
                f"unsupported variable type: {default_value_type}"
            )
        param_config = config_class.new(default_value=default_value)
        var_type = default_value_type
    else:
        raise UnknownDefaultValueType(f"unknown default value type: {type(definition)}")

    if replacements:
        param_config = dataclasses.replace(param_config, **replacements)

    return Variable(param_config, processor, var_type)
