import os
import subprocess
import sys
import tkinter
from pathlib import Path
from tkinter import messagebox
from typing import Optional, Union


def show_error_message(message: str, title: Optional[str] = None):
    tk = tkinter.Tk()
    tk.withdraw()
    messagebox.showerror(title=title, message=message, parent=tk)
    tk.destroy()


def show_info_message(message: str, title: Optional[str] = None):
    tk = tkinter.Tk()
    tk.withdraw()
    messagebox.showinfo(title=title, message=message, parent=tk)
    tk.destroy()


def ask_yes_no_question(message: str, title: Optional[str] = None) -> bool:
    tk = tkinter.Tk()
    tk.withdraw()
    ret = messagebox.askyesno(title=title, message=message, parent=tk)
    tk.destroy()
    return ret


def find_duplicates(lst: list) -> list:
    """使用集合查找重复元素"""
    seen = set()
    duplicates = set()

    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return list(duplicates)


def move_to_desktop_center(window: Union[tkinter.Tk, tkinter.Toplevel]):
    """将窗口移动到屏幕中心"""
    window.withdraw()
    # window.update_idletasks()
    window.update()
    w, h = window.winfo_width(), window.winfo_height()
    x = (window.winfo_screenwidth() - w) // 2
    y = (window.winfo_screenheight() - h) // 2
    window.geometry(f"+{int(x)}+{int(y)}")
    window.deiconify()


def open_file_in_editor(file_path: Union[str, Path]):
    """
    使用系统默认文本编辑器打开文件
    """
    file_path = str(Path(file_path).resolve())
    if sys.platform.startswith("win"):
        # Windows 系统
        os.startfile(file_path)
    elif sys.platform.startswith("darwin"):
        # macOS 系统
        subprocess.run(["open", file_path])
    else:
        # Linux 和其他 Unix 系统
        subprocess.run(["xdg-open", file_path])
