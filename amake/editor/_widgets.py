from tkinter import TclError, Menu
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Treeview
from typing import Literal, Dict, Any, List, Optional, Callable, Union

from .._messages import messages


class TextEdit(ScrolledText):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._msgs = messages()

        self._context_menu = None

        self.create_default_menu()
        self._bind_keyboard_events()

    def _bind_keyboard_events(self):
        """绑定键盘导航事件"""
        # 允许文本组件获得焦点
        self.config(takefocus=1)

        # 方向键
        self.bind("<Up>", self._on_arrow_key)
        self.bind("<Down>", self._on_arrow_key)
        self.bind("<Left>", self._on_arrow_key)
        self.bind("<Right>", self._on_arrow_key)

        # PageUp 和 PageDown
        self.bind("<Prior>", self._on_page_up)  # PageUp
        self.bind("<Next>", self._on_page_down)  # PageDown

        # Home 和 End
        self.bind("<Home>", self._on_home)
        self.bind("<End>", self._on_end)

        # Ctrl+Home 和 Ctrl+End
        self.bind("<Control-Home>", self._on_ctrl_home)
        self.bind("<Control-End>", self._on_ctrl_end)

        self.config(undo=True)
        self.bind("<Control-c>", self._on_ctrl_c)
        self.bind("<Control-v>", self._on_ctrl_v)
        self.bind("<Control-x>", self._on_ctrl_x)
        self.bind("<Control-z>", self._on_ctrl_z)
        self.bind("<Control-y>", self._on_ctrl_y)
        self.bind("<Control-a>", self._on_ctrl_a)

    def _on_arrow_key(self, event):
        """处理方向键事件"""
        # 允许默认的滚动行为
        return

    def _on_page_up(self, event=None):
        _ = event
        """PageUp - 向上翻页"""
        self.yview_scroll(-1, "pages")
        return "break"

    def _on_page_down(self, event=None):
        """PageDown - 向下翻页"""
        _ = event
        self.yview_scroll(1, "pages")
        return "break"

    def _on_home(self, event):
        """Home - 移动到行首"""
        if event.state & 0x1:  # Shift 键被按下
            self.tag_add("sel", "insert linestart", "insert")
        else:
            self.mark_set("insert", "insert linestart")
        return "break"

    def _on_end(self, event):
        """End - 移动到行尾"""
        if event.state & 0x1:  # Shift 键被按下
            self.tag_add("sel", "insert", "insert lineend")
        else:
            self.mark_set("insert", "insert lineend")
        return "break"

    def _on_ctrl_home(self, event):
        """Ctrl+Home - 移动到文档开头"""
        _ = event
        self.mark_set("insert", "1.0")
        self.see("1.0")
        return "break"

    def _on_ctrl_end(self, event):
        """Ctrl+End - 移动到文档末尾"""
        _ = event
        self.mark_set("insert", "end")
        self.see("end")
        return "break"

    def _on_ctrl_a(self, event):
        """Ctrl+A - 全选"""
        _ = event
        self.tag_add("sel", "1.0", "end")
        return "break"

    def _on_ctrl_c(self, event):
        """Ctrl+C - 复制"""
        _ = event
        try:
            self.event_generate("<<Copy>>")
        except TclError:
            pass
        return "break"

    def _on_ctrl_v(self, event):
        """Ctrl+V - 粘贴"""
        _ = event
        try:
            self.event_generate("<<Paste>>")
        except TclError as e:
            print(e, "unable to generate paste event")
        return "break"

    def _on_ctrl_x(self, event):
        """Ctrl+X - 剪切"""
        _ = event
        try:
            self.event_generate("<<Cut>>")
        except TclError:
            pass
        return "break"

    def _on_ctrl_z(self, event):
        """Ctrl+Z - 撤销"""
        _ = event
        try:
            self.edit_undo()
        except TclError:
            pass
        return "break"

    def _on_ctrl_y(self, event):
        """Ctrl+Y - 重做"""
        _ = event
        try:
            self.edit_redo()
        except TclError:
            pass
        return "break"

    def set_text(self, text: str):
        self.delete("1.0", "end")
        self.insert("1.0", text)

    def append_text(self, text: str):
        self.insert("end", text)

    def get_text(self) -> str:
        return self.get("1.0", "end-1c")

    def set_wrap(self, wrap: Literal["none", "char", "word"]):
        self.config(wrap=wrap)

    def clear(self):
        self.delete("1.0", "end")

    def create_default_menu(self):
        """创建右键菜单"""
        self._context_menu = Menu(self, tearoff=0)
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_COPY_ACTION, command=self.copy
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_CUT_ACTION,
            command=lambda e=None: self._on_ctrl_x(e),
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_PASTE_ACTION,
            command=lambda e=None: self._on_ctrl_v(e),
        )
        self._context_menu.add_separator()
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_UNDO_ACTION,
            command=lambda e=None: self._on_ctrl_z(e),
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_REDO_ACTION,
            command=lambda e=None: self._on_ctrl_y(e),
        )

        self._context_menu.add_separator()

        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_SELECT_ALL_ACTION, command=self.select_all
        )

        self._context_menu.add_separator()

        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_SCROLL_TOP, command=self.scroll_to_top
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_SCROLL_BOTTOM, command=self.scroll_to_bottom
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_PAGEUP, command=self._on_page_up
        )
        self._context_menu.add_command(
            label=self._msgs.MSG_TEXTEDIT_PAGEDOWN, command=self._on_page_down
        )

        # 绑定右键事件
        self.bind("<Button-3>", self.show_context_menu)  # 右键点击

    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._context_menu.grab_release()

    def copy(self):
        """复制选中的文本"""
        try:
            self.event_generate("<<Copy>>")
        except TclError:
            pass

    def select_all(self):
        """全选文本"""
        self.tag_add("sel", "1.0", "end")

    def scroll_to_top(self):
        """滚动到顶部"""
        self.see("1.0")

    def scroll_to_bottom(self):
        """滚动到底部"""
        self.see("end")


class TableView(Treeview):
    def __init__(self, master, headers: Union[List[str], Dict[str, str]], **kwargs):
        # key -> display text
        header_map = {}
        if isinstance(headers, list):
            for key in headers:
                header_map[key] = key
        else:
            header_map = headers.copy()

        self._headers = header_map

        kwargs.setdefault("columns", list(header_map.values()))
        kwargs.setdefault("show", "headings")
        kwargs.setdefault("selectmode", "extended")

        super().__init__(master, **kwargs)

        self._data: List[Dict[str, Any]] = []
        self._double_click_callback: Optional[Callable[[List[int]], None]] = None

        self._setup_columns()
        self.bind("<Double-1>", self._on_double_click)

    def _setup_columns(self):
        """配置表格列"""
        # 第一列（#0）用于树形结构，我们隐藏它
        self.column("#0", width=0, stretch=False)

        for header in self._headers.values():
            self.column(header, width=100, anchor="center")
            self.heading(header, text=header, anchor="center")

    # noinspection PyUnusedLocal
    def _on_double_click(self, event):
        """处理双击事件"""
        if self._double_click_callback:
            self._double_click_callback(self.selected_indexes)

    def _rebuild_treeview(self):
        """重新构建Treeview显示"""
        # 保存当前选中状态
        old_selection = self.selected_indexes
        # 清空并重新插入所有项目
        self.delete(*self.get_children())
        for obj in self._data:
            values = [obj.get(header, "") for header in self._headers.keys()]
            self.insert("", "end", values=values)
        # 恢复选中状态
        self._select_indexes(old_selection)

    def _select_index(self, index: int):
        """选中指定索引的项目"""
        children = self.get_children()
        if 0 <= index < len(children):
            self.selection_set(children[index])

    def _select_indexes(self, indexes: List[int]):
        """选中多个索引的项目"""
        children = self.get_children()
        selected_items = []
        for index in indexes:
            if 0 <= index < len(children):
                selected_items.append(children[index])
        self.selection_set(selected_items)

    def add_item(self, obj: Dict[str, Any]):
        self._data.append(obj)
        display_values = [obj.get(header, "") for header in self._headers.keys()]
        self.insert("", "end", values=display_values)

    def add_items(self, objs: List[Dict[str, Any]]):
        self._data.extend(objs)
        for obj in objs:
            display_values = [obj.get(header, "") for header in self._headers.keys()]
            self.insert("", "end", values=display_values)

    def update_item(self, index: int, obj: Dict[str, Any]):
        """更新指定索引的项目"""
        if 0 <= index < len(self._data):
            obj_ = self._data[index]
            obj_.update(obj)
            values = [obj_.get(header, "") for header in self._headers.keys()]
            # 获取Treeview中的item ID
            item_id = self.get_children()[index]
            self.item(item_id, values=values)
        else:
            raise IndexError(f"index out of range: {index}")

    def set_item(self, index: int, obj: Dict[str, Any]):
        """设置指定索引的项目"""
        if 0 <= index < len(self._data):
            self._data[index] = obj
            values = [obj.get(header, "") for header in self._headers.keys()]
            # 获取Treeview中的item ID
            item_id = self.get_children()[index]
            self.item(item_id, values=values)
        else:
            raise IndexError(f"index out of range: {index}")

    def remove_item(self, index: int) -> Optional[Dict[str, Any]]:
        if 0 <= index < len(self._data):
            removed_item = self._data.pop(index)
            # 获取Treeview中的item ID并删除
            item_id = self.get_children()[index]
            self.delete(item_id)
            return removed_item
        return None

    def remove_selected_items(self) -> List[Dict[str, Any]]:
        selected_indexes = self.selected_indexes
        if not selected_indexes:
            return []

        selected_indexes.sort(reverse=True)
        removed_items = []
        for index in selected_indexes:
            removed_item = self.remove_item(index)
            if removed_item:
                removed_items.append(removed_item)
        return removed_items

    def clear_items(self):
        self._data.clear()
        self.delete(*self.get_children())

    def item_at(self, index: int) -> Optional[Dict[str, Any]]:
        if 0 <= index < len(self._data):
            return self._data[index]
        return None

    def index_of(self, obj: Dict[str, Any]) -> Optional[int]:
        try:
            return self._data.index(obj)
        except ValueError:
            return None

    @property
    def count(self) -> int:
        return len(self._data)

    @property
    def items(self) -> List[Dict[str, Any]]:
        return self._data.copy()

    @property
    def selected_indexes(self) -> List[int]:
        selected_items = self.selection()
        children = self.get_children()
        indexes = []
        for item in selected_items:
            if item in children:
                indexes.append(children.index(item))

        return indexes

    @property
    def selected_items(self) -> List[Dict[str, Any]]:
        indexes = self.selected_indexes
        return [self._data[i] for i in indexes if 0 <= i < len(self._data)]

    def move_to(self, src_index: int, dst_index: int):
        if (
            0 <= src_index < len(self._data)
            and 0 <= dst_index < len(self._data)
            and src_index != dst_index
        ):
            # 移动数据
            item = self._data.pop(src_index)
            self._data.insert(dst_index, item)
            # 重新构建Treeview
            self._rebuild_treeview()
        else:
            raise IndexError(f"index out of range: {src_index} or {dst_index}")

    def move_up(self):
        selected_indexes = self.selected_indexes
        if not selected_indexes:
            return

        # 只处理第一个选中的项目
        index = selected_indexes[0]
        if index > 0:
            self.move_to(index, index - 1)
            # 重新选中移动后的项目
            self._select_index(index - 1)

    def move_down(self):
        selected_indexes = self.selected_indexes
        if not selected_indexes:
            return

        # 只处理最后一个选中的项目
        index = selected_indexes[-1]
        if index < len(self._data) - 1:
            self.move_to(index, index + 1)
            # 重新选中移动后的项目
            self._select_index(index + 1)

    def add_double_click_callback(self, callback: Callable[[List[int]], None]):
        self._double_click_callback = callback
