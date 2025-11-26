from tkinter import Toplevel, Tk, messagebox
from tkinter.ttk import Frame, Button
from typing import Union, Optional

from pyguiadapterlite.components.tabview import TabView
from pyguiadapterlite.core.hdpi import set_dpi_aware

from ._general_page import _GeneralPropertiesTab
from ._preview_window import PreviewWindow
from ._variables_page import _VariablesTab, DuplicatedVariableNameError
from .. import common
from .._messages import messages
from ..common import get_appsettings
from ..makeoptions import MakeOptions
from ..schema import AmakeSchema
from ..utils import move_to_desktop_center


class AmakeSchemaEditor(object):
    def __init__(
        self,
        parent: Union[Tk, Toplevel],
        schema: AmakeSchema,
        size: tuple = (800, 600),
    ):

        self._msgs = messages()
        self._appsettings = get_appsettings()

        self._parent = parent
        self._size = size or (800, 600)

        self._schema = schema or AmakeSchema()

        self._main_frame: Optional[Frame] = None
        self._bottom_frame: Optional[Frame] = None

        self._tab_view: Optional[TabView] = None

        self._preview_button: Optional[Button] = None
        self._save_button: Optional[Button] = None
        self._cancel_button: Optional[Button] = None

        self._general_tab: Optional[_GeneralPropertiesTab] = None
        self._variables_tab: Optional[_VariablesTab] = None

        self._cancelled = True

        self._setup_ui()

    def _setup_ui(self):

        tr_ = common.trfunc()
        self._parent.title(tr_("Amake Schema Editor"))
        self._parent.geometry(f"{self._size[0]}x{self._size[1]}")

        self._parent.protocol("WM_DELETE_WINDOW", self._on_close)

        self._main_frame = Frame(self._parent)
        self._main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self._tab_view = TabView(self._main_frame)
        self._tab_view.pack(side="top", expand=True, fill="both")

        self._general_tab = _GeneralPropertiesTab(self._tab_view.internal, self._schema)
        self._tab_view.add_tab("id_general", tr_("General"), self._general_tab)

        self._variables_tab = _VariablesTab(self._tab_view.internal, self._schema)
        self._tab_view.add_tab("id_variables", tr_("Variables"), self._variables_tab)

        self._bottom_frame = Frame(self._parent)
        self._bottom_frame.pack(side="bottom", fill="x")

        self._cancel_button = Button(
            self._bottom_frame, text=tr_("Cancel"), command=self._on_cancel
        )
        self._cancel_button.pack(side="right", padx=5, pady=5)

        self._save_button = Button(
            self._bottom_frame, text=tr_("Save"), command=self._on_save
        )
        self._save_button.pack(side="right", padx=5, pady=5)

        self._preview_button = Button(
            self._bottom_frame, text=tr_("Preview"), command=self._on_preview
        )
        self._preview_button.pack(side="right", padx=5, pady=5)

    @property
    def schema(self) -> AmakeSchema:
        return self._schema

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    @classmethod
    def run(cls, schema: AmakeSchema, *args, **kwargs) -> Optional[AmakeSchema]:
        appsettings = get_appsettings()
        if appsettings.hdpi_mode:
            set_dpi_aware(True)

        app = Tk()
        editor = cls(app, schema, *args, **kwargs)
        move_to_desktop_center(app)
        app.mainloop()
        if editor.is_cancelled:
            return None
        return editor.schema

    def _on_preview(self):
        tr_ = common.trfunc()
        try:
            new_schema = self._get_updated_schema()
        except DuplicatedVariableNameError as e:
            messagebox.showerror(
                tr_("Error"),
                tr_("Duplicated variable names found: {}").format(
                    ", ".join(e.duplicated_names)
                ),
            )
            return

        conflict_vars = MakeOptions().get_conflict_names(new_schema.variables.keys())
        if conflict_vars:
            messagebox.showerror(
                tr_("Error"),
                tr_(
                    "The following variable names are reserved by amake internally, please choose other names: {}"
                ).format(", ".join(conflict_vars)),
            )
            return

        PreviewWindow.preview(self._parent, new_schema)

    def _on_save(self):
        tr_ = common.trfunc()
        try:
            new_schema = self._get_updated_schema()
        except DuplicatedVariableNameError as e:
            messagebox.showerror(
                tr_("Error"),
                tr_("Duplicated variable names found, please rename them: {}").format(
                    ", ".join(e.duplicated_names)
                ),
            )
            return

        conflict_vars = MakeOptions().get_conflict_names(new_schema.variables.keys())
        if conflict_vars:
            messagebox.showerror(
                tr_("Error"),
                tr_(
                    "The following variable names are reserved by amake internally, please choose other names: {}"
                ).format(", ".join(conflict_vars)),
            )
            return

        self._schema = new_schema
        self._cancelled = False
        self._on_close()

    def _on_cancel(self):
        self._cancelled = True
        self._on_close()

    def _on_close(self):
        self._parent.destroy()

    def _get_updated_schema(self):
        return AmakeSchema.from_variable_definitions(
            self._variables_tab.variable_definitions,
            **self._general_tab.general_properties,
        )
