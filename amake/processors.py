import os.path
from pathlib import Path
from typing import Any, Union, Callable, Optional, Dict

_BUILTINS = {}


def _add_to_builtins(
    func: Callable, name: Optional[str] = None, aliases: Optional[list] = None
):
    global _BUILTINS
    name = name or func.__name__
    _BUILTINS[name] = func

    if not aliases:
        return

    for alias in set(aliases):
        if alias == name:
            continue
        if alias in _BUILTINS:
            raise ValueError(f"Alias {alias} already exists in builtin pipe functions")


def ensure_type(input_data: Any, expected_type: str, failure_value: Any = "") -> Any:
    if type(input_data).__name__ == expected_type:
        return input_data
    return failure_value


_add_to_builtins(ensure_type)


def ensure_str(input_data: Any, failure_value: str = "") -> str:
    return ensure_type(input_data, "str", failure_value)


_add_to_builtins(ensure_str)


def to_str(input_data: Any) -> str:
    if input_data is None:
        return ""
    return str(input_data)


_add_to_builtins(to_str, aliases=["str"])


def to_int(input_data: Any) -> int:
    if not input_data:
        return 0
    return int(input_data)


_add_to_builtins(to_int, aliases=["int"])


def to_bool(input_data: Any) -> bool:
    return bool(input_data)


_add_to_builtins(to_bool, aliases=["bool"])


def to_float(input_data: Any) -> float:
    if not input_data:
        return 0.0
    return float(input_data)


_add_to_builtins(to_float, aliases=["float"])


def upper(input_data: str) -> str:
    return input_data.upper()


_add_to_builtins(upper)


def lower(input_data: str) -> str:
    return input_data.lower()


_add_to_builtins(lower)


def capitalize(input_data: str) -> str:
    return input_data.capitalize()


_add_to_builtins(capitalize)


def title(input_data: str) -> str:
    return input_data.title()


_add_to_builtins(title)


def split(input_data: str, separator: str = " ") -> list:
    return input_data.split(separator)


_add_to_builtins(split)


def replace(input_data: str, old: str, new: str, count: int = -1) -> str:
    return input_data.replace(old, new, count)


_add_to_builtins(replace)


def strip(input_data: str, chars: str = None) -> str:
    return input_data.strip(chars)


_add_to_builtins(strip)


def lstrip(input_data: str, chars: str = None) -> str:
    return input_data.lstrip(chars)


_add_to_builtins(lstrip)


def rstrip(input_data: str, chars: str = None) -> str:
    return input_data.rstrip(chars)


_add_to_builtins(rstrip)


def strslice(input_data: str, start: int, end: int = None):
    return input_data[start:end]


_add_to_builtins(strslice, aliases=["slice"])


def join(input_data: list, separator: str = " ") -> str:
    return separator.join(input_data)


_add_to_builtins(join)


def prefix(input_data: str, pre: str) -> str:
    return pre + input_data


_add_to_builtins(prefix)


def suffix(input_data: str, suf: str) -> str:
    return input_data + suf


_add_to_builtins(suffix)


def reverse(input_data: Union[str, list]) -> Union[str, list]:
    if isinstance(input_data, str):
        return input_data[::-1]
    elif isinstance(input_data, list):
        return input_data[::-1]
    else:
        return input_data


_add_to_builtins(reverse)


def left(input_data: str, length: int) -> str:
    return input_data[:length]


_add_to_builtins(left)


def right(input_data: str, length: int) -> str:
    return input_data[-length:]


_add_to_builtins(right)


def ifelse(condition: bool, true_value: Any, false_value: Any) -> Any:
    return true_value if condition else false_value


_add_to_builtins(ifelse)


def distinct(input_data: list) -> list:
    return list(set(input_data))


_add_to_builtins(distinct)


def no_empty(input_data: list) -> list:
    return [x for x in input_data if x]


_add_to_builtins(no_empty)


def ifeq(input_data: Any, value: Any, true_value: Any, *args: Any):
    if input_data == value:
        return true_value
    if args:
        return args[0]
    return input_data


_add_to_builtins(ifeq)


def ifneq(input_data: Any, value: Any, true_value: Any, *args: Any):
    if input_data != value:
        return true_value
    if args:
        return args[0]
    return input_data


_add_to_builtins(ifneq, aliases=["ifne"])


def prefix_ifeq(input_data: str, value: str, prefix_: str) -> str:
    if input_data == value:
        return prefix_ + input_data
    return input_data


_add_to_builtins(prefix_ifeq)


def prefix_ifneq(input_data: str, value: str, prefix_: str) -> str:
    if input_data != value:
        return prefix_ + input_data
    return input_data


_add_to_builtins(prefix_ifneq)


def suffix_ifeq(input_data: str, value: str, suffix_: str) -> str:
    if input_data == value:
        return input_data + suffix_
    return input_data


_add_to_builtins(suffix_ifeq)


def suffix_ifneq(input_data: str, value: str, suffix_: str) -> str:
    if input_data != value:
        return input_data + suffix_
    return input_data


_add_to_builtins(suffix_ifneq)


def prefix_each(input_data: list, prefix_: str):
    return [prefix_ + x for x in input_data]


_add_to_builtins(prefix_each)


def suffix_each(input_data: list, suffix_: str):
    return [x + suffix_ for x in input_data]


_add_to_builtins(suffix_each)


def replace_each(input_data: list, old: str, new: str):
    return [x.replace(old, new) for x in input_data]


_add_to_builtins(replace_each)


def strip_each(input_data: list, chars: str = None):
    return [x.strip(chars) for x in input_data]


_add_to_builtins(strip_each)


def asbpath(input_data: str) -> str:
    if not input_data or not input_data.strip():
        return ""
    return os.path.abspath(input_data)


_add_to_builtins(asbpath)


def normpath(input_data: str) -> str:
    if not input_data or not input_data.strip():
        return ""
    return os.path.normpath(input_data)


_add_to_builtins(normpath)


def posixpath(input_data: str) -> str:
    if not input_data or not input_data.strip():
        return ""
    return Path(input_data).as_posix()


_add_to_builtins(posixpath)


def abspath_each(input_data: list) -> list:
    if not input_data:
        return []
    return [os.path.abspath(x) for x in input_data]


_add_to_builtins(abspath_each)


def normpath_each(input_data: list) -> list:
    if not input_data:
        return []
    return [os.path.normpath(x) for x in input_data]


_add_to_builtins(normpath_each)


def posixpath_each(input_data: list) -> list:
    if not input_data:
        return []
    return [Path(x).as_posix() for x in input_data]


_add_to_builtins(posixpath_each)


def pretend_each(input_data: list, value: Any) -> list:
    ret = []
    for x in input_data:
        ret.append(value)
        ret.append(x)
    return ret


_add_to_builtins(pretend_each)


def extend_each(input_data: list, value: Any) -> list:
    ret = []
    for x in input_data:
        ret.append(x)
        ret.append(value)
    return ret


_add_to_builtins(extend_each)


def get_builtins() -> Dict[str, Callable]:
    return _BUILTINS.copy()


def get_builtin_processor(name: str) -> Optional[Callable]:
    return _BUILTINS.get(name, None)
