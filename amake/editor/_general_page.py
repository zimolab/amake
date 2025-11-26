from tkinter import Widget, E, W, Label
from tkinter.ttk import Entry, Frame
from typing import Dict, Optional, Tuple, Any

from pyguiadapterlite.components.scrollarea import NColumnScrollableArea, ColumnConfig

from ._widgets import TextEdit
from .common import TEXT_EDIT_FONT
from .._messages import messages
from ..schema import AmakeSchema


class _GeneralPropertiesTab(NColumnScrollableArea):

    _GENERAL_PROPERTIES = [
        "version",
        "author",
        "created_at",
        "website",
        "default_target",
        "targets",
        "description",
    ]

    def __init__(self, parent: Widget, schema: AmakeSchema):
        super().__init__(
            parent,
            n_columns=2,
            column_configs=(
                ColumnConfig(anchor=E + W, weight=0, padding_x=5, padding_y=2),
                ColumnConfig(anchor=E + W, weight=1, padding_x=5, padding_y=2),
            ),
        )

        self._normal_properties_edits: Dict[str, Entry] = {}
        self._targets_edit: Optional[TextEdit] = None
        self._description_edit: Optional[TextEdit] = None

        self._general_properties = {
            prop_name: getattr(schema, prop_name)
            for prop_name in self._GENERAL_PROPERTIES
        }

        self._create_widgets()

    @property
    def general_properties(self) -> Dict[str, Any]:
        self._update_general_properties()
        return self._general_properties.copy()

    def _update_general_properties(self):
        for prop_name, widget in self._normal_properties_edits.items():
            value = widget.get()
            if prop_name in self._general_properties:
                self._general_properties[prop_name] = value

        targets = self._targets_edit.get_text().split("\n")
        self._general_properties["targets"] = [t.strip() for t in targets if t.strip()]
        description = self._description_edit.get("1.0", "end-1c")
        self._general_properties["description"] = description.strip()

    def _create_widgets(self):
        for prop_name, prop_value in self._general_properties.items():

            if prop_name == "targets":
                if prop_value:
                    prop_value = "\n".join(prop_value)
                label, widget = self._create_targets_row(prop_value)
            elif prop_name == "description":
                label, widget = self._create_description_row(prop_value)
            else:
                label, widget = self._create_normal_property_row(prop_name, prop_value)
            self.add_row((label, widget))

    def _create_normal_property_row(
        self, name: str, default_value: str = ""
    ) -> Tuple[Label, Entry]:
        label = Label(self._inner_frame, text=name)
        entry = Entry(self._inner_frame)
        entry.insert(0, default_value)
        self._normal_properties_edits[name] = entry
        return label, entry

    def _create_targets_row(self, default_value: str = "") -> Tuple[Label, Frame]:
        label = Label(self._inner_frame, text="targets")
        frame = Frame(self._inner_frame)
        textview = TextEdit(frame, height=8, font=TEXT_EDIT_FONT)
        textview.pack(side="top", fill="both", expand=True)
        textview.insert("1.0", default_value)
        desc_label = Label(
            frame, text=messages().MSG_GENERAL_TAB_TARGETS_HINT, fg="red", font="bold"
        )
        desc_label.pack(side="bottom", fill="x")
        self._targets_edit = textview
        return label, frame

    def _create_description_row(
        self, default_value: str = ""
    ) -> Tuple[Label, TextEdit]:
        label = Label(self._inner_frame, text="description")
        textview = TextEdit(self._inner_frame, height=10, font=TEXT_EDIT_FONT)
        textview.insert("1.0", default_value)
        self._description_edit = textview
        return label, textview
