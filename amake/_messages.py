from typing import Optional

from . import common


class _Messages:
    def __init__(self):
        tr_ = common.trfunc()
        self.MSG_EXE_BTN_TEXT = tr_("Run")
        self.MSG_CANCEL_BTN_TEXT = tr_("Cancel")
        self.MSG_CLEAR_BTN_TEXT = tr_("Clear")
        self.MSG_CLEAR_CHECKBOX_TEXT = tr_("Clear Output on Run")
        self.MSG_OUTPUT_TAB_TITLE = tr_("Output")
        self.MSG_DOCUMENT_TAB_TITLE = tr_("Document")
        self.MSG_DEFAULT_PARAM_GROUP_NAME = tr_("Main")
        self.MSG_RUNNING_COMMAND = tr_("Running command: ")
        self.MSG_ASK_CANCEL_EXECUTION = tr_("User ask to cancel execution")
        self.MSG_TERMINATING_PROCESS = tr_("Terminating process...")
        self.MSG_PROCESS_FINISHED = tr_("Process Finished")
        self.MSG_EXIT_CODE = tr_("exit code: ")
        self.MSG_QUIT_DIALOG_TITLE = tr_("Quit")
        self.MSG_QUIT_CONFIRMATION = tr_(
            "Do you want to save configurations before quitting?"
        )
        self.MSG_EXECUTION_TIME = tr_("Execution time: ")
        self.MSG_COMMAND_FAILED = tr_("Failed to run command:")
        self.MSG_MENU_FILE = tr_("File")
        self.MSG_MENU_VIEW = tr_("View")
        self.MSG_MENU_TOOLS = tr_("Tools")
        self.MSG_MENU_HELP = tr_("Help")

        self.MSG_SUCCESS_DIALOG_TITLE = tr_("Success")
        self.MSG_FAILURE_DIALOG_TITLE = tr_("Failure")

        self.MSG_ACTION_SAVE_CONFIGS = tr_("Save Configurations")
        self.MSG_ACTION_LOAD_CONFIGS = tr_("Load Configurations")
        self.MSG_ACTION_QUIT = tr_("Quit")
        self.MSG_ACTION_TEST_MAKE_CMD = tr_("Test Make Command")
        self.MSG_ACTION_PRINT_MAKE_HELP = tr_("Print Make Help")
        self.MSG_ACTION_GENERATE_CMD = tr_("Generate Command Line")
        self.MSG_ACTION_GENERATE_BUILD_SCRIPT = tr_("Generate Build Script")
        self.MSG_ACTION_ALWAYS_ON_TOP = tr_("Always on Top")
        self.MSG_ACTION_ABOUT = tr_("About")
        self.MSG_ACTION_LICENSE = tr_("License")
        self.MSG_ACTION_SCHEMA_WEBSITE = tr_("Goto Schema Website")
        self.MSG_CONFIGS_SAVE_SUCCESS = tr_("Configurations saved successfully")
        self.MSG_CONFIGS_SAVE_FAILURE = tr_("Failed to save configurations")


_MESSAGES: Optional[_Messages] = None


def Messages() -> _Messages:
    global _MESSAGES
    if _MESSAGES is None:
        _MESSAGES = _Messages()
    return _MESSAGES
