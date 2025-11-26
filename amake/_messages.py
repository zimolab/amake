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
        self.MSG_EDIT_APPSETTINGS = tr_("Settings")
        self.MSG_ACTION_ABOUT_SCHEMA = tr_("About Schema")
        self.MSG_ABOUT_SCHEMA_TITLE = tr_("About Schema")
        self.MSG_SCHEMA_AUTHOR = tr_("Author")
        self.MSG_SCHEMA_VERSION = tr_("Version")
        self.MSG_SCHEMA_WEBSITE = tr_("Website")
        self.MSG_SCHEMA_DESCRIPTION = tr_("Description")
        self.MSG_SCHEMA_CREATED_AT = tr_("Created At")

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
        self.MSG_LOAD_CONFIGS_DIALOG_TITLE = tr_("Load Configurations")
        self.MSG_CONFIGS_FILE_FILTER = tr_("Configurations Files")
        self.MSG_JSON_FILE_FILTER = tr_("JSON Files")

        self.MSG_LANGUAGE_FIELD = tr_("Language")
        self.MSG_HDPI_MODE_FIELD = tr_("High DPI Mode")
        self.MSG_CONFIRM_EXIT_FIELD = tr_("Confirm Exit")

        self.MSG_SAVE_SETTINGS_ERROR = tr_("Failed to save application settings!")
        self.MSG_SETTINGS_SAVED = tr_(
            "Application settings has been saved! Some changes may require a restart of the program."
        )

        self.MSG_SCHEMA_EDITOR_TITLE = tr_("Schema Editor")
        self.MSG_SCHEMA_EDITOR_GENERAL_TAB_TITLE = tr_("General")
        self.MSG_SCHEMA_EDITOR_VARS_TAB_TITLE = tr_("Variables")
        self.MSG_SCHEMA_EDITOR_CANCEL_BTN_TEXT = tr_("Cancel")
        self.MSG_SCHEMA_EDITOR_SAVE_BTN_TEXT = tr_("Save")
        self.MSG_SCHEMA_EDITOR_PREVIEW_BTN_TEXT = tr_("Save")
        self.MSG_SCHEMA_EDITOR_DUPLICATE_VAR_ERROR = tr_(
            "Duplicated variable names found: {}"
        )
        self.MSG_SCHEMA_EDITOR_VARNAME_CONFLICT_ERROR = tr_(
            "The following variable names are reserved by amake internally, please choose other names: {}"
        )

        self.MSG_VARS_TAB_VARNAME_COL_TITLE = tr_("Variable Name")
        self.MSG_VARS_TAB_VARTYPE_COL_TITLE = tr_("Type")
        self.MSG_VARS_TAB_VARLABEL_COL_TITLE = tr_("Label")
        self.MSG_VARS_TAB_VARGROUP_COL_TITLE = tr_("Default Value")
        self.MSG_VARS_TAB_UP_BTN_TEXT = tr_("Up")
        self.MSG_VARS_TAB_DOWN_BTN_TEXT = tr_("Down")
        self.MSG_VARS_TAB_ADD_BTN_TEXT = tr_("Add")
        self.MSG_VARS_TAB_REMOVE_BTN_TEXT = tr_("Remove")
        self.MSG_VARS_TAB_CLEAR_BTN_TEXT = tr_("Remove All")
        self.MSG_VARS_TAB_CANCEL_BTN_TEXT = tr_("Cancel")

        self.MSG_VARS_TAB_VARNAME_LABEL = tr_("Variable Name")
        self.MSG_VARS_TAB_VARLABEL_LABEL = tr_("Label")
        self.MSG_VARS_TAB_VARTYPE_LABEL = tr_("Type")
        self.MSG_VARS_TAB_VARGROUP_LABEL = tr_("Group")
        self.MSG_VARS_TAB_VARDESC_LABEL = tr_("Description")
        self.MSG_VARS_TAB_VAREXTRAS_LABEL = tr_("Extra Properties")
        self.MSG_VARS_TAB_VARPROCESSORS_LABEL = tr_("Processors")
        self.MSG_VARS_TAB_INVALID_VAR_ERROR = tr_("invalid extra properties found: {}")

        self.MSG_VARS_TAB_EDIT_BTN_TEXT = tr_("Edit")
        self.MSG_VARS_TAB_NO_SELECTION_WARNING = tr_("No variable selected!")
        self.MSG_VARS_TAB_REMOVE_CONFIRM = tr_(
            "Do you want to remove the selected variable?"
        )
        self.MSG_VARS_TAB_REMOVE_ALL_CONFIRM = tr_(
            "Do you want to remove all variables?"
        )
        self.MSG_VARS_TAB_EDITOR_TITLE = tr_("Variable Definition Editor")

        self.MSG_GENERAL_TAB_TARGETS_HINT = tr_("↑ one target per line ↑")

        self.MSG_TARGET_COMBO_LABEL = tr_("Target:")

        self.MSG_TEXTEDIT_COPY_ACTION = tr_("Copy")
        self.MSG_TEXTEDIT_CUT_ACTION = tr_("Cut")
        self.MSG_TEXTEDIT_PASTE_ACTION = tr_("Paste")
        self.MSG_TEXTEDIT_UNDO_ACTION = tr_("Undo")
        self.MSG_TEXTEDIT_REDO_ACTION = tr_("Redo")
        self.MSG_TEXTEDIT_SELECT_ALL_ACTION = tr_("Select All")
        self.MSG_TEXTEDIT_SCROLL_TOP = tr_("Scroll to Top")
        self.MSG_TEXTEDIT_SCROLL_BOTTOM = tr_("Scroll to Bottom")
        self.MSG_TEXTEDIT_PAGEUP = tr_("Page Up")
        self.MSG_TEXTEDIT_PAGEDOWN = tr_("Page Down")

        self.MSG_MKOPTS_GROUP_NAME = tr_("Make Options")
        self.MSG_MKOPTS_YES = tr_("Yes")
        self.MSG_MKOPTS_NO = tr_("No")
        self.MSG_MKOPTS_MKCMD_LABEL = tr_("make command")
        self.MSG_MKOPTS_MKCMD_DESC = tr_("make command or path to make executable.")
        self.MSG_MKOPTS_OVERRIDE_LABEL = tr_("override makefile variables")
        self.MSG_MKOPTS_OVERRIDE_DESC = tr_(
            "override makefile variables with the same name using -e option."
        )
        self.MSG_MKOPT_DEBUG_LV_LABEL = tr_("debug level(--debug)")
        self.MSG_MKOPT_DEBUG_LV_DESC = tr_("debug level of make.")
        self.MSG_MKOPTS_DIR_LABEL = tr_("makefile directory(--directory)")
        self.MSG_MKOPTS_DIR_DESC = tr_("path to makefile.")
        self.MSG_MKOPTS_MAKEFILE_LABEL = tr_("makefile(--makefile)")
        self.MSG_MKOPTS_MAKEFILE_DESC = tr_("the makefile to be used.")

        self.MSG_MAKEFILE_TYPE = tr_("Makefile")

        self.MSG_MKOPTS_EXTRA_LABEL = tr_("extra options ")
        self.MSG_MKOPTS_EXTRA_DESC = tr_("extra options to be passed to make command.")
        self.MSG_MKOPTS_DRY_RUN_LABEL = tr_("dry run(--dry-run)")
        self.MSG_MKOPTS_DRY_RUN_DESC = tr_("don't actually run any commands.")
        self.MSG_MKOPTS_IGNORE_ERRORS_LABEL = tr_("ignore errors(--ignore-errors)")
        self.MSG_MKOPTS_IGNORE_ERRORS_DESC = tr_("ignore errors and keep going.")
        self.MSG_MKOPTS_ALWAYS_LABEL = tr_("always make(--always-make)")
        self.MSG_MKOPTS_ALWAYS_DESC = tr_(
            "always remake everything, even if the target is up to date."
        )
        self.MSG_MKOPTS_JOBS_LABEL = tr_("jobs count(--jobs)")
        self.MSG_MKOPTS_JOBS_DESC = tr_("number of jobs to run simultaneously.")
        self.MSG_MKOPTS_INCLUDE_DIR_LABEL = tr_("include directories(--include-dir)")
        self.MSG_MKOPTS_INCLUDE_DIR_TITLE = tr_("Include Directory List")
        self.MSG_MKOPTS_INCLUDE_DIR_DESC = tr_("directories to search for makefiles.")


_messages: Optional[_Messages] = None


def messages() -> _Messages:
    global _messages
    if _messages is None:
        _messages = _Messages()
    return _messages
