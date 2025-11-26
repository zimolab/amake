from tkinter.ttk import Combobox, Separator, Label
from typing import Optional, List

from pyguiadapterlite import FnExecuteWindow

from .._messages import messages


class AmakeWidgets(object):
    def __init__(self):
        self._msgs = messages()
        self._targets_combobox: Optional[Combobox] = None
        self._created = False

    def create(self, window: FnExecuteWindow):
        if self._created:
            return

        separator = Separator(window.bottom_area, orient="vertical")
        separator.pack(side="left", fill="y", padx=5, pady=5)
        label = Label(window.bottom_area, text=self._msgs.MSG_TARGET_COMBO_LABEL)
        label.pack(side="left", padx=5, pady=5)
        self._targets_combobox = Combobox(window.bottom_area)
        self._targets_combobox.pack(side="left", fill="x", padx=5, pady=5)
        self._created = True

    def set_targets(self, targets: List[str]):
        assert self._created
        self._targets_combobox.config(values=targets)

    def set_current_target(self, target: str):
        assert self._created
        self._targets_combobox.set(target)

    def get_current_target(self) -> str:
        assert self._created
        return self._targets_combobox.get()
