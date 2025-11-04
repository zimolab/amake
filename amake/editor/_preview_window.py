import dataclasses
from tkinter import Toplevel
from typing import Optional

from pyguiadapterlite import FnExecuteWindow, FnExecuteWindowConfig
from pyguiadapterlite.core.fn import FnInfo

from amake.schema import AmakeSchema
from amake.utils import move_to_desktop_center


def _placeholder_function(**kwargs):
    pass


@dataclasses.dataclass(frozen=True)
class PreviewWindowConfig(FnExecuteWindowConfig):
    title: str = "Preview Amake Schema"


class PreviewWindow(FnExecuteWindow):
    def __init__(
        self, parent, schema: AmakeSchema, config: Optional[PreviewWindowConfig] = None
    ):

        config = config or PreviewWindowConfig()

        config = dataclasses.replace(
            config,
            print_function_result=False,
            show_function_result=False,
        )

        info = FnInfo(
            fn=_placeholder_function,
            window_config=config,
            document=schema.description,
            parameter_configs=schema.parameter_configs,
            cancelable=False,
        )

        super().__init__(parent, info)

        self._bottom_area.forget()

    def on_execute(self):
        self.show_warning("You are in preview mode!")
        return

    @classmethod
    def preview(
        cls, parent, schema: AmakeSchema, config: Optional[PreviewWindowConfig] = None
    ):
        toplevel = Toplevel(parent)
        cls(toplevel, schema, config)
        move_to_desktop_center(toplevel)
        toplevel.grab_set()
        toplevel.wait_window()
        toplevel.destroy()
