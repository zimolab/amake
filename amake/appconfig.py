import builtins
import dataclasses

from .common import Serializable


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
        setattr(builtins, "__tr__", self.gettext)
        setattr(builtins, "__ntr__", self.ngettext)

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
