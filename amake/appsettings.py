from pyguiadapterlite import JsonSettingsBase
from pyguiadapterlite.types import LooseChoiceValue, BoolValue2

from ._messages import messages

LANGS = ["auto", "en_US", "zh_CN"]
DEFAULT_LANG = "auto"


class AmakeAppSettings(JsonSettingsBase):
    _msgs = messages()

    locale = LooseChoiceValue(
        label=_msgs.MSG_LANGUAGE_FIELD,
        choices=LANGS,
        default_value=DEFAULT_LANG,
    )
    always_on_top = BoolValue2(
        label=_msgs.MSG_ACTION_ALWAYS_ON_TOP, default_value=False
    )
    hdpi_mode = BoolValue2(label=_msgs.MSG_HDPI_MODE_FIELD, default_value=False)
    confirm_exit = BoolValue2(label=_msgs.MSG_CONFIRM_EXIT_FIELD, default_value=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(
        self,
        file_path: str,
        ensure_ascii=False,
        indent=4,
        encoding="utf-8",
        **kwargs,
    ):

        if not file_path:
            raise FileNotFoundError("please specify save filepath")
        super().save(
            file_path=file_path,
            ensure_ascii=ensure_ascii,
            indent=indent,
            encoding=encoding,
            **kwargs,
        )

    @classmethod
    def load(
        cls,
        file_path: str,
        encoding="utf-8",
        **kwargs,
    ) -> "AmakeAppSettings":
        settings = super().load(file_path=file_path, encoding=encoding, **kwargs)
        assert isinstance(settings, cls)
        return settings

    @classmethod
    def default(cls) -> "AmakeAppSettings":
        return cls()
