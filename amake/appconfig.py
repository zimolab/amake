import builtins
import dataclasses

from .common import Serializable


# __APP_DEFAULT_LOCALES_MAP__ = {
#     "System": "auto",
#     "English": "en_US",
#     "简体中文": "zh_CN",
# }


@dataclasses.dataclass
class AmakeAppConfig(Serializable):
    locale: str = "auto"
    clear_output_on_run: bool = True
    always_on_top: bool = False

    def __post_init__(self):
        self._i18n = None

    def setup_i18n(self, locale_dir):
        from pyguiadapterlite.i18n import I18N

        self._i18n = I18N(domain="amake", localedir=locale_dir, locale_code=self.locale)
        # 把当前_i18n的翻译函数注入到全局空间
        # 之后，可以使用common.trfunc()/common.ntrfunc()来获取到下面两个翻译函数
        # _debug("injecting i18n functions into global namespace")
        setattr(builtins, "__tr__", self.gettext)
        setattr(builtins, "__ntr__", self.ngettext)

    # @property
    # def locales_map(self) -> Dict[str, str]:
    #     if self._locales_map is not None:
    #         return self._locales_map
    #     # self._locales_map = self._load_locales_map()
    #     return self._locales_map

    def gettext(self, string_id: str) -> str:
        if self._i18n is None:
            return string_id
        return self._i18n.gettext(string_id)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        if self._i18n is None:
            return singular if n == 1 else plural
        return self._i18n.ngettext(singular, plural, n)

    def tr(self, string_id: str) -> str:
        return self.gettext(string_id)

    def ntr(self, singular: str, plural: str, n: int) -> str:
        return self.ngettext(singular, plural, n)

    @classmethod
    def default(cls) -> "AmakeAppConfig":
        return cls()

    # def _load_locales_map(self) -> Dict[str, str]:
    #     global __APP_DEFAULT_LOCALES_MAP__
    #     try:
    #         _debug(f"loading locales map from file: {__APP_LOCALES_MAP_FILEPATH__}")
    #         with open(__APP_LOCALES_MAP_FILEPATH__, "r", encoding="utf-8") as f:
    #             obj = json.load(f)
    #             if not isinstance(obj, dict):
    #                 raise ValueError("locales map should be a dict")
    #             return obj
    #     except BaseException as e:
    #         _debug(f"failed to load locales map from file, using default: {e}")
    #         _debug(f"saving default locales map to file")
    #         self._save_locales_map(__APP_DEFAULT_LOCALES_MAP__)
    #         return __APP_DEFAULT_LOCALES_MAP__.copy()

    # @staticmethod
    # def _save_locales_map(obj: Dict[str, str]):
    #     try:
    #         with open(__APP_LOCALES_MAP_FILEPATH__, "w", encoding="utf-8") as f:
    #             json.dump(obj, f, indent=4, ensure_ascii=False)
    #     except BaseException as e:
    #         _debug(f"failed to save locales map to file: {e}")


# def load_configurations(
#     app_config: AmakeAppConfig,
#     schema: AmakeSchema,
#     configurations_filename: Optional[str] = None,
#     working_dir: Union[str, Path, None] = None,
#     gui_mode: bool = True,
# ) -> AmakeConfigurations:
#     _debug("load variables configurations")
#     tr_ = app_config.gettext
#
#     if not working_dir:
#         working_dir = Path.cwd()
#     _debug(f"loading configurations from {working_dir}")
#     if not configurations_filename:
#         _debug(f"finding configurations file in {_DEFAULT_AMAKE_CONFIGS_FILENAMES}")
#         for filename in _DEFAULT_AMAKE_CONFIGS_FILENAMES:
#             filepath = working_dir / filename
#             if filepath.is_file():
#                 configurations_filename = filepath.as_posix()
#                 _debug(f"found configurations file {configurations_filename}")
#                 break
#         if not configurations_filename:
#             _debug(f"no configurations file found, ask for creating a new one")
#             ret = ask_yes_no_question(
#                 message=tr_(
#                     "No configurations file found, do you want to create a new one from the schema?"
#                 ),
#                 gui_mode=gui_mode,
#             )
#             if not ret:
#                 _debug(f"user cancelled, exit")
#                 sys.exit(1)
#
#             _debug(f"creating new configurations file")
#             configurations_filepath = working_dir / _DEFAULT_AMAKE_CONFIGS_FILENAMES[0]
#             configurations = AmakeConfigurations.make_from_schema(schema)
#             configurations.save(
#                 configurations_filepath.as_posix(),
#                 remember_filepath=True,
#                 encoding="utf-8",
#                 indent=4,
#                 ensure_ascii=False,
#             )
#             if not configurations_filepath.is_file():
#                 show_error_message(
#                     message=tr_("Failed to create new configurations file!"),
#                     gui_mode=gui_mode,
#                 )
#                 _debug(f"failed to create new configurations file, exit")
#                 sys.exit(1)
#
#             show_info_message(
#                 message=tr_(
#                     "New configurations file created successfully! You can edit it now!"
#                 ),
#             )
#             return configurations
#
#     configurations_filepath = Path(working_dir) / configurations_filename
#     try:
#         configurations = AmakeConfigurations.load(configurations_filepath.as_posix())
#         _debug(f"loaded configurations file {configurations_filepath}")
#         return configurations
#     except Exception as e:
#         _debug(f"failed to load configurations file {configurations_filepath}: {e}")
#         show_error_message(
#             message=tr_(f"Failed to load configurations file: {e}"),
#             gui_mode=gui_mode,
#         )
#         sys.exit(1)
#

# def check_variable_conflicts(
#     app_config: AmakeAppConfig,
#     schema: AmakeSchema,
#     configurations: AmakeConfigurations,
#     gui_mode: bool = True,
# ):
#     _debug("check variable name conflicts")
#     tr_ = app_config.gettext
#
#     conflicts = schema.check_conflicts(configurations.options.keys())
#     if not conflicts:
#         _debug("no variable conflicts found")
#         return
#     show_error_message(
#         message=tr_(
#             "The following variables are reserved by amake internal, please rename them in the schema!"
#             "\n\n" + "\n".join(conflicts)
#         ),
#         gui_mode=gui_mode,
#     )
#     sys.exit(1)
