from tkinter import Tk, Toplevel, Widget
from tkinter.ttk import Frame
from typing import Union

from pyguiadapterlite import BaseSimpleDialog


class AboutDialog(BaseSimpleDialog):
    def __init__(
        self,
        parent: Union[Tk, Widget] = None,
        title: str = "",
        size: tuple = (350, 450),
        resizable: bool = True,
        ok_text: str = "Ok",
        cancel_text: str = "Cancel",
    ):
        super().__init__(parent, title, size, resizable, ok_text, cancel_text)

    def on_create_content_area(self, dialog: Toplevel):
        self._content_area = Frame(dialog)
        self._content_area.pack(fill="both", expand=True)
