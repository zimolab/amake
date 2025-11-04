import enum
from typing import List, Callable, Dict, Any, Optional

from pyguiadapterlite import FnExecuteWindow


class EventType(enum.Enum):
    AFTER_WINDOW_CREATE = 0
    BEFORE_WINDOW_CLOSE = 1
    BEFORE_EXECUTE = 2
    AFTER_EXECUTE = 3


class AmakeEventHandler(object):
    def __init__(self):
        self._after_window_create_callbacks = []
        self._before_window_close_callbacks = []
        self._before_execute_callbacks = []
        self._after_execute_callbacks = []

    def _callback_list(self, event_type: EventType) -> List[Callable]:
        if event_type == EventType.AFTER_WINDOW_CREATE:
            return self._after_window_create_callbacks
        if event_type == EventType.BEFORE_WINDOW_CLOSE:
            return self._before_window_close_callbacks
        if event_type == EventType.BEFORE_EXECUTE:
            return self._before_execute_callbacks
        if event_type == EventType.AFTER_EXECUTE:
            return self._after_execute_callbacks
        raise ValueError(f"invalid event type: {event_type}")

    def add_event_callback(self, event_type: EventType, callback: Callable):
        if not callable(callback):
            raise ValueError(f"not a callable: {callback}")
        callback_list = self._callback_list(event_type)
        if callback in callback_list:
            raise ValueError(f"callback already exist: {callback}")
        callback_list.append(callback)

    def remove_event_callback(self, event_type: EventType, callback: Callable):
        callback_list = self._callback_list(event_type)
        if callback not in callback_list:
            raise ValueError(f"callback not found: {callback}")
        callback_list.remove(callback)

    def is_event_callback_exist(
        self, event_type: EventType, callback: Callable
    ) -> bool:
        callback_list = self._callback_list(event_type)
        return callback in callback_list

    def clear_event_callbacks(self, event_type: EventType):
        callback_list = self._callback_list(event_type)
        callback_list.clear()

    def after_window_create(self, win: FnExecuteWindow):
        for callback in self._after_window_create_callbacks:
            callback(win)

    def before_window_close(self, win: FnExecuteWindow) -> bool:
        if not self._before_window_close_callbacks:
            return True
        for callback in self._before_window_close_callbacks:
            if not callback(win):
                return False
        return True

    def before_execute(
        self, win: FnExecuteWindow, parameters_values: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if not self._before_execute_callbacks:
            return parameters_values
        for callback in self._before_execute_callbacks:
            parameters_values = callback(win, parameters_values.copy())
            if parameters_values is None:
                return None
        return parameters_values

    def after_execute(
        self, win: FnExecuteWindow, result: Any, exception: Optional[Exception]
    ):
        for callback in self._after_execute_callbacks:
            callback(win, result, exception)
