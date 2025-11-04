import ast
import dataclasses
import inspect
from typing import List, Any, Callable, Dict, Optional


class ProcessorError(RuntimeError):
    pass


class InvalidProcessorFunction(ProcessorError):
    pass


class ProcessorFunctionNotFound(ProcessorError):
    pass


class ProcessorFunctionAlreadyExist(ProcessorError):
    pass


class InvalidArgument(ProcessorError):
    pass


@dataclasses.dataclass
class Command(object):
    name: str
    func: Callable
    args: List[Any]


class CommandTokenizer(object):
    def __init__(self, invalid_arg_handler: Callable[[str], Any] = lambda x: x):
        self._invalid_arg_handler = invalid_arg_handler

    @staticmethod
    def tokenize(command_str: str) -> List[str]:
        """
        将命令字符串分割为token
        支持识别带引号的字符串和复杂数据结构
        """
        tokens = []
        current_token = ""
        in_quotes = None  # 当前是否在引号内，None表示不在，'或"表示在哪种引号内
        in_brackets = 0  # 括号嵌套深度
        in_parens = 0  # 圆括号嵌套深度
        escape_next = False  # 是否转义下一个字符

        i = 0
        while i < len(command_str):
            char = command_str[i]

            # 处理转义字符
            if escape_next:
                current_token += char
                escape_next = False
                i += 1
                continue

            if char == "\\":
                escape_next = True
                current_token += char
                i += 1
                continue

            # 处理引号
            if char in ('"', "'") and in_brackets == 0 and in_parens == 0:
                if in_quotes is None:
                    in_quotes = char
                elif in_quotes == char:
                    in_quotes = None
                current_token += char
                i += 1
                continue

            # 处理方括号（列表）
            if char == "[" and in_quotes is None:
                in_brackets += 1
                current_token += char
                i += 1
                continue

            if char == "]" and in_quotes is None and in_brackets > 0:
                in_brackets -= 1
                current_token += char
                i += 1
                continue

            # 处理圆括号（元组）
            if char == "(" and in_quotes is None:
                in_parens += 1
                current_token += char
                i += 1
                continue

            if char == ")" and in_quotes is None and in_parens > 0:
                in_parens -= 1
                current_token += char
                i += 1
                continue

            # 处理空格分隔（仅在不在引号或括号内时）
            if (
                char == " "
                and in_quotes is None
                and in_brackets == 0
                and in_parens == 0
            ):
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                i += 1
                continue

            current_token += char
            i += 1

        # 添加最后一个token
        if current_token:
            tokens.append(current_token)
        return tokens

    def parse_value(self, token: str) -> Any:
        if not token:
            return ""

        if token.lower() in ("none", "null"):
            return None

        if token.lower() == "true":
            return True

        if token.lower() == "false":
            return False

        try:
            return ast.literal_eval(token)
        except BaseException as e:
            if not self._invalid_arg_handler:
                raise InvalidArgument(f"invalid argument: {token}") from e
            return self._invalid_arg_handler(token)


class ProcessorExecutor(object):
    def __init__(self, invalid_arg_handler: Callable[[str], Any] = lambda x: x):
        self._registry: Dict[str, Callable] = {}
        self._tokenizer = CommandTokenizer(invalid_arg_handler)

    def register(self, func: Callable, name: Optional[str] = None):
        if not callable(func):
            raise InvalidProcessorFunction(f"not a function")

        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) == 0:
            raise InvalidProcessorFunction(f"at least one parameter is required")

        if name is None:
            name = func.__name__
        if name in self._registry:
            raise ProcessorFunctionAlreadyExist(
                f"pipeline function already exist: {name}"
            )
        self._registry[name] = func

    def unregister(self, name: str):
        if name not in self._registry:
            raise ProcessorFunctionNotFound(f"pipeline function not found: {name}")
        del self._registry[name]

    def get_function(self, name: str) -> Callable:
        if name not in self._registry:
            raise ProcessorFunctionNotFound(f"pipeline function not found: {name}")
        return self._registry[name]

    def unregister_all(self):
        self._registry = {}

    @property
    def processor_functions(self) -> List[str]:
        return list(self._registry.keys())

    @staticmethod
    def split_processor_str(pipeline_str: str) -> List[str]:
        """
        分割管道字符串，但忽略引号内的管道符号
        """
        parts = []
        current_part = ""
        in_quotes = None
        escape_next = False

        i = 0
        while i < len(pipeline_str):
            char = pipeline_str[i]

            # 处理转义字符
            if escape_next:
                current_part += char
                escape_next = False
                i += 1
                continue

            if char == "\\":
                escape_next = True
                current_part += char
                i += 1
                continue

            # 处理引号
            if char in ('"', "'"):
                if in_quotes is None:
                    in_quotes = char
                elif in_quotes == char:
                    in_quotes = None
                current_part += char
                i += 1
                continue

            # 处理管道符号（仅在不在引号内时分割）
            if char == "|" and in_quotes is None:
                parts.append(current_part.strip())
                current_part = ""
                i += 1
                continue

            current_part += char
            i += 1

        # 添加最后一部分
        if current_part:
            parts.append(current_part.strip())

        return parts

    def parse_processor(self, processor_str: str) -> List[Command]:
        """解析管道字符串"""
        commands = []
        parts = self.split_processor_str(processor_str)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            tokens = self._tokenizer.tokenize(part)
            func_name = tokens[0]
            func = self.get_function(func_name)
            # 解析参数
            args = [self._tokenizer.parse_value(token) for token in tokens[1:]]
            commands.append(Command(func_name, func, args))
        return commands

    def execute(
        self, pipeline_str: str, initial_input: Any = None, debug: bool = False
    ) -> Any:
        """执行管道"""
        if debug:
            return self.debug_execute(pipeline_str, initial_input)

        commands = self.parse_processor(pipeline_str)
        if not commands:
            return initial_input

        func = commands[0].func
        args = commands[0].args or []

        # 执行第一个命令
        current_data = self._exec_func(func, initial_input, args)

        # 执行后续命令
        for command in commands[1:]:
            func = command.func
            args = command.args
            current_data = self._exec_func(func, current_data, args)
        return current_data

    @staticmethod
    def _exec_func(func: Callable, input_data: Any, args: List[Any]) -> Any:
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) == 0:
            raise InvalidProcessorFunction(f"at least one parameter is required")
        if len(params) == 1:
            return func(input_data)
        return func(input_data, *args)

    def debug_execute(self, pipeline_str: str, initial_input: Any = None) -> Any:
        """执行管道并显示调试信息"""

        def _args_str(arg):
            if arg:
                return "args = (" + ",".join(map(str, arg)) + ")"
            return "args = <NoArgs>"

        def _input_str(data):
            return f"input = {data} (type:{type(data)})"

        def _func_str(no, f):
            return f"({no}) {f}".ljust(15)

        def _output_str(data):
            return f"output = {data} (type:{type(data)})"

        def _proc_str(no, f, arg, ip, op):
            return f"{_func_str(no, f)}  {_input_str(ip)}  {_args_str(arg)}  {_output_str(op)}"

        commands = self.parse_processor(pipeline_str)
        if not commands:
            return initial_input

        # 执行第一个命令
        func = commands[0].func
        args = commands[0].args
        name = commands[0].name
        current_data = self._exec_func(func, initial_input, args)
        print(_proc_str(0, name, args, initial_input, current_data))
        for i, command in enumerate(commands[1:], 1):
            func = command.func
            args = command.args
            name = command.name
            prev_data = current_data

            current_data = self._exec_func(func, current_data, args)
            print(_proc_str(i, name, args, prev_data, current_data))

        return current_data
