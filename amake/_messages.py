from typing import Optional

from . import common


class _Messages:
    def __init__(self):
        tr_ = common.trfunc()
        self.MSG_APP_NAME = tr_("amake")
        self.MSG_EXE_BTN_TEXT = tr_("Run")
        self.MSG_CANCEL_BTN_NAME = tr_("Cancel")
        self.MSG_CLEAR_BTN_NAME = tr_("Clear")
        self.MSG_CLEAR_CHECKBOX_TEXT = tr_("Clear Output on Run")
        self.MSG_OUTPUT_TAB_TITLE = tr_("Output")
        self.MSG_DOCUMENT_TAB_TITLE = tr_("Document")
        self.MSG_DEFAULT_PARAM_GROUP_NAME = tr_("Main")


_MESSAGES: Optional[_Messages] = None


def Messages() -> _Messages:
    global _MESSAGES
    if _MESSAGES is None:
        _MESSAGES = _Messages()
    return _MESSAGES
