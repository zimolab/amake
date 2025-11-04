# Because the original library platformdirs requires Python 3.10 or higher,
# but this project is going to be compatible with Python 3.8 or higher, so
# I can't use it directly. I copied the necessary code from platformdirs project
# and made some modifications to make it compatible with Python 3.8 or higher.
# Below is the original license of platformdirs project:
#
# MIT License
#
# Copyright (c) 2010-202x The platformdirs developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional, Callable


def get_win_folder_from_env_vars(csidl_name: str) -> str:
    """Get folder from environment variables."""
    result = get_win_folder_if_csidl_name_not_env_var(csidl_name)
    if result is not None:
        return result

    env_var_name = {
        "CSIDL_APPDATA": "APPDATA",
        "CSIDL_COMMON_APPDATA": "ALLUSERSPROFILE",
        "CSIDL_LOCAL_APPDATA": "LOCALAPPDATA",
    }.get(csidl_name)
    if env_var_name is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)
    result = os.environ.get(env_var_name)
    if result is None:
        msg = f"Unset environment variable: {env_var_name}"
        raise ValueError(msg)
    return result


def get_win_folder_if_csidl_name_not_env_var(csidl_name: str) -> Optional[str]:
    """Get a folder for a CSIDL name that does not exist as an environment variable."""
    if csidl_name == "CSIDL_PERSONAL":
        return os.path.join(
            os.path.normpath(os.environ["USERPROFILE"]), "Documents"
        )  # noqa: PTH118

    if csidl_name == "CSIDL_DOWNLOADS":
        return os.path.join(
            os.path.normpath(os.environ["USERPROFILE"]), "Downloads"
        )  # noqa: PTH118

    if csidl_name == "CSIDL_MYPICTURES":
        return os.path.join(
            os.path.normpath(os.environ["USERPROFILE"]), "Pictures"
        )  # noqa: PTH118

    if csidl_name == "CSIDL_MYVIDEO":
        return os.path.join(
            os.path.normpath(os.environ["USERPROFILE"]), "Videos"
        )  # noqa: PTH118

    if csidl_name == "CSIDL_MYMUSIC":
        return os.path.join(
            os.path.normpath(os.environ["USERPROFILE"]), "Music"
        )  # noqa: PTH118
    return None


def get_win_folder_from_registry(csidl_name: str) -> str:
    """
    Get folder from the registry.

    This is a fallback technique at best. I'm not sure if using the registry for these guarantees us the correct answer
    for all CSIDL_* names.

    """
    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
        "CSIDL_PERSONAL": "Personal",
        "CSIDL_DOWNLOADS": "{374DE290-123F-4565-9164-39C4925E467B}",
        "CSIDL_MYPICTURES": "My Pictures",
        "CSIDL_MYVIDEO": "My Video",
        "CSIDL_MYMUSIC": "My Music",
    }.get(csidl_name)
    if shell_folder_name is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)
    if (
        sys.platform != "win32"
    ):  # only needed for mypy type checker to know that this code runs only on Windows
        raise NotImplementedError
    import winreg  # noqa: PLC0415

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
    )
    directory, _ = winreg.QueryValueEx(key, shell_folder_name)
    return str(directory)


def get_win_folder_via_ctypes(csidl_name: str) -> str:
    """Get folder with ctypes."""
    # There is no 'CSIDL_DOWNLOADS'.
    # Use 'CSIDL_PROFILE' (40) and append the default folder 'Downloads' instead.
    # https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid

    import ctypes  # noqa: PLC0415

    csidl_const = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
        "CSIDL_PERSONAL": 5,
        "CSIDL_MYPICTURES": 39,
        "CSIDL_MYVIDEO": 14,
        "CSIDL_MYMUSIC": 13,
        "CSIDL_DOWNLOADS": 40,
        "CSIDL_DESKTOPDIRECTORY": 16,
    }.get(csidl_name)
    if csidl_const is None:
        msg = f"Unknown CSIDL name: {csidl_name}"
        raise ValueError(msg)

    buf = ctypes.create_unicode_buffer(1024)
    windll = getattr(
        ctypes, "windll"
    )  # noqa: B009 # using getattr to avoid false positive with mypy type checker
    windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if it has high-bit chars.
    if any(ord(c) > 255 for c in buf):  # noqa: PLR2004
        buf2 = ctypes.create_unicode_buffer(1024)
        if windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    if csidl_name == "CSIDL_DOWNLOADS":
        return os.path.join(buf.value, "Downloads")  # noqa: PTH118

    return buf.value


def _pick_get_win_folder() -> Callable[[str], str]:
    try:
        import ctypes  # noqa: PLC0415
    except ImportError:
        pass
    else:
        if hasattr(ctypes, "windll"):
            return get_win_folder_via_ctypes
    try:
        import winreg  # noqa: PLC0415, F401
    except ImportError:
        return get_win_folder_from_env_vars
    else:
        return get_win_folder_from_registry


get_win_folder = lru_cache(maxsize=None)(_pick_get_win_folder())


def _append_app_name_and_version(*base: str, **kwargs) -> str:
    params = list(base[1:])
    appname = kwargs.get("appname", "")
    version = kwargs.get("version", "")
    if appname:
        params.append(appname)
        if version:
            params.append(version)
    path = os.path.join(base[0], *params)  # noqa: PTH118
    _optionally_create_directory(path)
    return path


def _optionally_create_directory(path: str, **kwargs) -> None:
    ensure_exists = kwargs.get("ensure_exists", False)
    if ensure_exists:
        Path(path).mkdir(parents=True, exist_ok=True)


def _user_data_dir_unix(**kwargs):
    """
    :return: data directory tied to the user, e.g. ``~/.local/share/$appname/$version`` or
     ``$XDG_DATA_HOME/$appname/$version``
    """
    path = os.environ.get("XDG_DATA_HOME", "")
    if not path.strip():
        path = os.path.expanduser("~/.local/share")  # noqa: PTH111
    return _append_app_name_and_version(path, **kwargs)


def _user_data_dir_macos(**kwargs):
    """:return: data directory tied to the user, e.g. ``~/Library/Application Support/$appname/$version``"""
    return _append_app_name_and_version(
        os.path.expanduser("~/Library/Application Support"), **kwargs
    )  # noqa: PTH111


def _user_data_dir_win(**kwargs):
    """
    :return: data directory tied to the user, e.g.
     ``%USERPROFILE%\\AppData\\Local\\$appauthor\\$appname`` (not roaming) or
     ``%USERPROFILE%\\AppData\\Roaming\\$appauthor\\$appname`` (roaming)
    """
    roaming = kwargs.get("roaming", False)
    const = "CSIDL_APPDATA" if roaming else "CSIDL_LOCAL_APPDATA"
    path = os.path.normpath(get_win_folder(const))
    return _append_parts(path, opinion_value=None, **kwargs)


def _append_parts(path: str, *, opinion_value: Optional[str] = None, **kwargs) -> str:
    params = []
    appname = kwargs.get("appname", "")
    version = kwargs.get("version", "")
    appauthor = kwargs.get("appauthor", "")
    opinion = kwargs.get("opinion", False)
    if appname:
        if not appauthor:
            author = appauthor or appname
            params.append(author)
            params.append(appname)
        if opinion_value is not None and opinion:
            params.append(opinion_value)
        if version:
            params.append(version)
    path = os.path.join(path, *params)  # noqa: PTH118
    _optionally_create_directory(path)
    return path


def user_data_dir(
    appname: Optional[str] = None,
    appauthor: Optional[str] = None,
    version: Optional[str] = None,
    roaming: bool = False,
    ensure_exists: bool = False,
):
    if sys.platform == "win32":
        return _user_data_dir_win(
            appname=appname,
            appauthor=appauthor,
            version=version,
            roaming=roaming,
            ensure_exists=ensure_exists,
        )
    elif sys.platform == "darwin":
        return _user_data_dir_macos(
            appname=appname,
            appauthor=appauthor,
            version=version,
            roaming=roaming,
            ensure_exists=ensure_exists,
        )
    else:
        return _user_data_dir_unix(
            appname=appname,
            appauthor=appauthor,
            version=version,
            roaming=roaming,
            ensure_exists=ensure_exists,
        )
