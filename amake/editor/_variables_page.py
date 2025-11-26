from copy import deepcopy
from tkinter import Widget, messagebox
from tkinter.ttk import Frame, Button
from typing import Optional, List, Dict, Any

from ._edit_window import VariableEditWindow
from ._widgets import TableView
from .common import (
    KEY_VAR_NAME,
    KEY_VAR_LABEL,
    KEY_VAR_TYPE,
    KEY_VAR_GROUP,
    KEY_VAR_PROCESSOR,
    get_properties_of,
)
from .._messages import messages
from ..common import get_default_processor
from ..schema import AmakeSchema
from ..utils import find_duplicates, move_to_desktop_center


class DuplicatedVariableNameError(Exception):
    def __init__(self, message: str, duplicated_names: List[str]):
        self.duplicated_names = duplicated_names
        super().__init__(message)


class _VariablesTab(Frame):

    def __init__(self, parent: Widget, schema: AmakeSchema):
        super().__init__(parent)
        self._msgs = messages()

        self._up_button: Optional[Button] = None
        self._down_button: Optional[Button] = None

        self._add_button: Optional[Button] = None
        self._edit_button: Optional[Button] = None
        self._remove_button: Optional[Button] = None
        self._clear_button: Optional[Button] = None

        self._variables_table: Optional[TableView] = None

        self._variable_definitions: List[Dict[str, Any]] = []

        for varname, var_def in schema.to_variable_definitions().items():
            var_def = var_def
            var_def[KEY_VAR_NAME] = varname
            self._variable_definitions.append(var_def)

        self._setup_ui()

    @property
    def variable_definitions(self) -> Dict[str, Dict[str, Any]]:
        variable_definitions = deepcopy(self._variables_table.items)

        varname_list = find_duplicates(
            [var_def[KEY_VAR_NAME] for var_def in variable_definitions]
        )
        if varname_list:
            raise DuplicatedVariableNameError(
                "Duplicated variable names found: " + ", ".join(varname_list),
                varname_list,
            )

        self._variable_definitions = variable_definitions
        ret = {}
        for var_def in self._variable_definitions:
            varname = var_def.pop(KEY_VAR_NAME)
            ret[varname] = var_def
        return ret

    def _setup_ui(self):
        self._create_variables_table()
        self._create_buttons()

    def _create_variables_table(self):
        self._variables_table = TableView(
            self,
            headers={
                KEY_VAR_NAME: self._msgs.MSG_VARS_TAB_VARNAME_COL_TITLE,
                KEY_VAR_TYPE: self._msgs.MSG_VARS_TAB_VARTYPE_COL_TITLE,
                KEY_VAR_LABEL: self._msgs.MSG_VARS_TAB_VARLABEL_COL_TITLE,
                KEY_VAR_GROUP: self._msgs.MSG_VARS_TAB_VARGROUP_COL_TITLE,
            },
        )
        self._variables_table.add_double_click_callback(self._on_double_click)
        self._variables_table.pack(side="top", fill="both", expand=True)
        self._variables_table.add_items(self._variable_definitions)

    def _create_buttons(self):
        button_frame = Frame(self)
        button_frame.pack(side="bottom", fill="x")
        self._up_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_UP_BTN_TEXT,
            command=self._on_move_up,
        )
        self._up_button.pack(side="left", padx=2, pady=5)

        self._down_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_DOWN_BTN_TEXT,
            command=self._on_move_down,
        )
        self._down_button.pack(side="left", padx=2, pady=5)

        self._add_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_ADD_BTN_TEXT,
            command=self._on_add,
        )

        self._remove_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_REMOVE_BTN_TEXT,
            command=self._on_remove,
        )

        self._clear_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_CLEAR_BTN_TEXT,
            command=self._on_clear,
        )

        self._edit_button = Button(
            button_frame,
            text=self._msgs.MSG_VARS_TAB_EDIT_BTN_TEXT,
            command=self._on_edit,
        )

        self._clear_button.pack(side="right", padx=2, pady=5)
        self._remove_button.pack(side="right", padx=2, pady=5)
        self._edit_button.pack(side="right", padx=2, pady=5)
        self._add_button.pack(side="right", padx=2, pady=5)

    def _on_add(self):
        self._start_add_item()

    def _on_edit(self):
        selection = self._variables_table.selected_indexes
        if not selection:
            messagebox.showwarning(
                self._msgs.MSG_WARNING_DIALOG_TITLE,
                self._msgs.MSG_VARS_TAB_NO_SELECTION_WARNING,
                parent=self,
            )
            return
        index = selection[0]
        var_def = self._variables_table.item_at(index)
        self._start_edit_item(index, var_def)

    def _on_remove(self):
        selection = self._variables_table.selected_items
        if not selection:
            messagebox.showwarning(
                self._msgs.MSG_WARNING_DIALOG_TITLE,
                self._msgs.MSG_VARS_TAB_NO_SELECTION_WARNING,
                parent=self,
            )
            return
        if messagebox.askyesno(
            self._msgs.MSG_CONFIRM_DIALOG_TITLE,
            self._msgs.MSG_VARS_TAB_REMOVE_CONFIRM,
            parent=self,
        ):
            self._variables_table.remove_selected_items()

    def _on_clear(self):
        if messagebox.askyesno(
            self._msgs.MSG_CONFIRM_DIALOG_TITLE,
            self._msgs.MSG_VARS_TAB_REMOVE_ALL_CONFIRM,
            parent=self,
        ):
            self._variables_table.clear_items()

    def _on_move_up(self):
        if not self._variables_table.selected_indexes:
            messagebox.showwarning(
                self._msgs.MSG_WARNING_DIALOG_TITLE,
                self._msgs.MSG_VARS_TAB_NO_SELECTION_WARNING,
                parent=self,
            )
            return
        self._variables_table.move_up()

    def _on_move_down(self):
        if not self._variables_table.selected_indexes:
            messagebox.showwarning(
                self._msgs.MSG_WARNING_DIALOG_TITLE,
                self._msgs.MSG_VARS_TAB_NO_SELECTION_WARNING,
                parent=self,
            )
            return
        self._variables_table.move_down()

    def _on_double_click(self, selection: List[int]):
        if not selection:
            return
        index = selection[0]
        var_def = self._variables_table.item_at(index)
        self._start_edit_item(index, var_def)

    def _start_edit_item(self, index: int, var_def: Dict[str, Any]):
        editor = VariableEditWindow(
            self,
            var_def,
            title=self._msgs.MSG_VARS_TAB_EDITOR_TITLE + " - " + var_def[KEY_VAR_NAME],
        )
        move_to_desktop_center(editor)
        editor.grab_set()
        editor.wait_window()
        if not editor.is_cancelled:
            self._variables_table.set_item(index, editor.variable_def)

    def _start_add_item(self):
        init_var_def = {
            **get_properties_of("str"),
            KEY_VAR_NAME: "VariableName",
            KEY_VAR_LABEL: "Variable Label",
            KEY_VAR_GROUP: "",
            KEY_VAR_TYPE: "str",
            KEY_VAR_PROCESSOR: get_default_processor("str"),
        }
        editor = VariableEditWindow(
            self, init_var_def, title=self._msgs.MSG_VARS_TAB_EDITOR_TITLE
        )
        move_to_desktop_center(editor)
        editor.grab_set()
        editor.wait_window()
        if not editor.is_cancelled:
            self._variables_table.add_item(editor.variable_def)
