import json
from tkinter import Widget, E, W, Toplevel, Tk, Frame, messagebox
from tkinter.ttk import Label, Entry, Combobox, Button
from typing import Dict, Any, Union

from pyguiadapterlite.components.scrollarea import NColumnScrollableArea, ColumnConfig

from ._widgets import TextEdit
from .common import (
    TEXT_EDIT_FONT,
    get_properties_of,
    KEY_VAR_NAME,
    KEY_VAR_TYPE,
    KEY_VAR_PROCESSOR,
    KEY_VAR_GROUP,
    KEY_VAR_DESCRIPTION,
    KEY_VAR_LABEL,
    KEY_VAR_HIDE_LABEL,
    KEY_VAR_LABEL_JUSTIFY,
)
from .. import common
from ..common import get_default_processor
from ..variable import AVAILABLE_TYPES, analyze_variable

_VAR_TYPES = [tpy for tpy in AVAILABLE_TYPES]
_PROPS_MAP = {tpy: get_properties_of(tpy) for tpy in AVAILABLE_TYPES}
_DEFAULT_VAR_TYPE = _VAR_TYPES[0]


class _VariableEdit(NColumnScrollableArea):

    def __init__(
        self,
        parent: Union[Widget, Tk, Toplevel],
        variable_def: Dict[str, Any],
        **kwargs,
    ):
        super().__init__(
            parent,
            n_columns=2,
            column_configs=(
                ColumnConfig(anchor=E + W, weight=0, padding_x=5, padding_y=3),
                ColumnConfig(anchor=E + W, weight=1, padding_x=5, padding_y=3),
            ),
            **kwargs,
        )
        self._parent = parent
        self._variable_def = variable_def.copy()

        tr_ = common.trfunc()
        self._variable_name_label = Label(self._inner_frame, text=tr_("Variable Name"))
        self._variable_name_edit = Entry(self._inner_frame)
        self.add_row((self._variable_name_label, self._variable_name_edit))

        variable_label = Label(self._inner_frame, text=tr_("Label"))
        self._variable_edit = Entry(self._inner_frame)
        self.add_row((variable_label, self._variable_edit))

        type_label = Label(self._inner_frame, text=tr_("Type"))
        self._variable_type_edit = Combobox(
            self._inner_frame, values=_VAR_TYPES, state="readonly"
        )
        self._variable_type_edit.bind(
            "<<ComboboxSelected>>", self._on_variable_type_changed
        )
        self.add_row((type_label, self._variable_type_edit))

        processors_label = Label(self._inner_frame, text=tr_("Processors"))
        self._variable_processors_edit = Entry(self._inner_frame)
        self.add_row((processors_label, self._variable_processors_edit))

        group_label = Label(self._inner_frame, text=tr_("Group"))
        self._variable_group_edit = Entry(self._inner_frame)
        self.add_row((group_label, self._variable_group_edit))

        description_label = Label(self._inner_frame, text=tr_("Description"))
        self._variable_description_edit = TextEdit(
            self._inner_frame, height=5, font=TEXT_EDIT_FONT
        )
        self.add_row((description_label, self._variable_description_edit))

        extra_properties_label = Label(self._inner_frame, text=tr_("Extra Properties"))
        self._extra_properties_edit = TextEdit(
            self._inner_frame, height=15, font=TEXT_EDIT_FONT
        )
        self.add_row((extra_properties_label, self._extra_properties_edit))

        self._variable_type_edit.current(0)
        self._on_variable_type_changed(None)

        self._update_ui()

    # noinspection PyUnusedLocal
    def _on_variable_type_changed(self, event):
        current_type = self._variable_type_edit.get()
        self._set_variable_processors(get_default_processor(current_type))
        self._set_extra_props(_PROPS_MAP.get(current_type))

    def _set_variable_name(self, name: str):
        self._variable_name_edit.delete(0, "end")
        self._variable_name_edit.insert(0, name)

    def _get_variable_name(self) -> str:
        return self._variable_name_edit.get()

    def _set_variable_label(self, label: str):
        self._variable_edit.delete(0, "end")
        self._variable_edit.insert(0, label)

    def _get_variable_label(self) -> str:
        return self._variable_edit.get()

    def _set_variable_type(self, var_type: str):
        self._variable_type_edit.set(var_type)

    def _get_variable_type(self) -> str:
        return self._variable_type_edit.get()

    def _set_variable_processors(self, processors: str):
        self._variable_processors_edit.delete(0, "end")
        self._variable_processors_edit.insert(0, processors)

    def _get_variable_processors(self) -> str:
        return self._variable_processors_edit.get()

    def _set_variable_group(self, group: str):
        self._variable_group_edit.delete(0, "end")
        self._variable_group_edit.insert(0, group)

    def _get_variable_group(self) -> str:
        return self._variable_group_edit.get()

    def _set_variable_description(self, description: str):
        self._variable_description_edit.set_text(description)

    def _get_variable_description(self) -> str:
        return self._variable_description_edit.get_text()

    def _set_extra_props(self, props: Dict[str, Any]):
        props = self._convert_to_extra_props(props)
        self._extra_properties_edit.set_text(
            json.dumps(props, indent=2, ensure_ascii=False)
        )

    def _get_extra_props(self) -> Dict[str, Any]:
        return json.loads(self._extra_properties_edit.get_text())

    def get_variable_def(self) -> Dict[str, Any]:
        self._update_variable_def()
        return self._variable_def

    def _update_variable_def(self):
        self._variable_def = {
            KEY_VAR_NAME: self._get_variable_name(),
            KEY_VAR_LABEL: self._get_variable_label(),
            KEY_VAR_TYPE: self._get_variable_type(),
            KEY_VAR_PROCESSOR: self._get_variable_processors(),
            KEY_VAR_GROUP: self._get_variable_group(),
            KEY_VAR_DESCRIPTION: self._get_variable_description(),
            **self._get_extra_props(),
        }

    @staticmethod
    def _convert_to_extra_props(var_def: Dict[str, Any]) -> Dict[str, Any]:
        non_extra_props = (
            KEY_VAR_HIDE_LABEL,
            KEY_VAR_LABEL_JUSTIFY,
            KEY_VAR_NAME,
            KEY_VAR_LABEL,
            KEY_VAR_TYPE,
            KEY_VAR_PROCESSOR,
            KEY_VAR_GROUP,
            KEY_VAR_DESCRIPTION,
        )
        return {k: v for k, v in var_def.items() if k not in non_extra_props}

    def _update_ui(self):
        self._set_variable_name(self._variable_def.get(KEY_VAR_NAME))
        self._set_variable_type(self._variable_def.get(KEY_VAR_TYPE))
        self._set_variable_processors(self._variable_def.get(KEY_VAR_PROCESSOR, ""))
        self._set_variable_label(self._variable_def.get(KEY_VAR_LABEL, ""))
        self._set_variable_description(self._variable_def.get(KEY_VAR_DESCRIPTION, ""))
        self._set_variable_group(self._variable_def.get(KEY_VAR_GROUP, ""))
        self._set_extra_props(self._variable_def)


class VariableEditWindow(Toplevel):

    def __init__(
        self,
        parent: Widget,
        variable_def: Dict[str, Any],
        title: str = "Variable Definition Editor",
        size: tuple = (800, 600),
        position: tuple = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self.title(title)
        if position:
            self.geometry(f"{size[0]}x{size[1]}+{position[0]}+{position[1]}")
        else:
            self.geometry(f"{size[0]}x{size[1]}")

        self._edit = _VariableEdit(self, variable_def)
        self._edit.pack(side="top", fill="both", expand=True)

        bottom_frame = Frame(self)
        bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        self._ok_button = Button(bottom_frame, text="OK", command=self._on_ok)
        self._cancel_button = Button(
            bottom_frame, text="Cancel", command=self._on_cancel
        )

        self._cancel_button.pack(side="right", padx=5, pady=5)
        self._ok_button.pack(side="right", padx=5, pady=5)

        self._variable_def = variable_def
        self._is_cancelled = False

    @property
    def variable_def(self) -> Dict[str, Any]:
        return self._variable_def

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def _on_ok(self):
        tr_ = common.trfunc()
        try:
            variable_def = self._edit.get_variable_def()
            tmp = variable_def.copy()
            tmp.pop(KEY_VAR_NAME, None)
            analyze_variable(tmp)
        except Exception as e:
            messagebox.showerror(
                tr_("Error"),
                tr_(f"invalid extra properties found: {e}").format(str(e)),
                parent=self,
            )
            return
        self._variable_def = variable_def
        self._is_cancelled = False
        self.destroy()

    def _on_cancel(self):
        self._is_cancelled = True
        self.destroy()
