import dataclasses
from typing import Any, Dict, Tuple

from pyguiadapterlite import ParameterWidgetFactory

TEXT_EDIT_FONT_SIZE = 12
TEXT_EDIT_FONT_FAMILY = "Consolas"

TEXT_EDIT_FONT = (TEXT_EDIT_FONT_FAMILY, TEXT_EDIT_FONT_SIZE)


KEY_VAR_NAME = "__name__"
KEY_VAR_TYPE = "__type__"
KEY_VAR_PROCESSOR = "__processor__"
KEY_VAR_LABEL = "label"
KEY_VAR_DESCRIPTION = "description"
KEY_VAR_GROUP = "group"
KEY_VAR_HIDE_LABEL = "hide_label"
KEY_VAR_LABEL_JUSTIFY = "label_justify"


def get_properties_of(
    typename: str, ignored_props: Tuple[str, ...] = ()
) -> Dict[str, Any]:
    w = ParameterWidgetFactory.find_by_typename(typename)
    if not w:
        return {}
    ignored_props = ignored_props or ()
    conf = dataclasses.asdict(w.ConfigClass())
    props = {k: v for k, v in conf.items() if k not in ignored_props}
    return props
