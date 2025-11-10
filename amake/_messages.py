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
        self.MSG_INFO_DIALOG_TITLE = tr_("Information")
        self.MSG_CONFIRM_DIALOG_TITLE = tr_("Confirmation")
        self.MSG_WARNING_DIALOG_TITLE = tr_("Warning")
        self.MSG_ERROR_DIALOG_TITLE = tr_("Error")
        self.MSG_ABOUT_DIALOG_TITLE = tr_("About")
        self.MSG_LICENSE_DIALOG_TITLE = tr_("License")

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
        self.MSG_EDIT_APP_CONFIGS = tr_("Edit App Configs")
        self.MSG_RESET_APP_CONFIGS = tr_("Reset App Configs")
        self.MSG_ASK_RESET_APP_CONFIGS = tr_("Do you want to reset app configs?")
        self.MSG_APP_CONFIGS_CHANGE_INFO = tr_(
            "The modifications to the app config file will be applied after restarting the application."
        )
        self.MSG_WAIT_EXECUTION_DONE = tr_("Please wait for execution to finish...")
        self.MSG_MAKE_CMD = tr_("Make Command")
        self.MSG_MAKE_TARGET = tr_("Make Target")
        self.MSG_MAKE_OPTIONS = tr_("Make Options")
        self.MSG_VARIABLES = tr_("Variables")
        self.MSG_OVERRIDE_VARIABLES = tr_("Override")
        self.MSG_CMD_LINE = tr_("Command Line")
        self.MSG_FAILED_TO_GENERATE_CMD = tr_("Failed to generate command line")

        self.MSG_GENERATE_SCRIPT_DIALOG_TITLE = tr_("Generate Build Script")
        self.MSG_SHELL_SCRIPT_FILE_TYPE = tr_("Shell Script")
        self.MSG_ALL_FILE_TYPE = tr_("All Files")
        self.MSG_BUILD_SCRIPT_GENERATED = tr_(
            "Build script generated successfully, you can find it at: "
        )
        self.MSG_FAILED_TO_GENERATE_SCRIPT = tr_(
            "Failed to generate build script because of the following error: "
        )
        self.MSG_NO_LICENSE_FILE = tr_(
            "This program is under the MIT license(license file not found)!"
        )
        self.MSG_OPEN_SCHEMA_WEBSITE_WARNING = tr_(
            "You are about to open an external website provided by the schema author.\n\n"
            "Caution: We cannot guarantee the safety of external content. Proceed at your own risk. "
            f"Open the following website?\n\n"
        )
        self.MSG_CONFIGS_LOAD_FAILURE = tr_("Failed to load configurations!")


_messages: Optional[_Messages] = None


def messages() -> _Messages:
    global _messages
    if _messages is None:
        _messages = _Messages()
    return _messages
