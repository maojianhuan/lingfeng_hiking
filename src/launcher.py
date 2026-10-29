"""Windows 桌面 exe 入口，不启动 Web 服务。"""
import sys
import tkinter as tk
from tkinter import messagebox

from app import OutingApp, PROJECT_URL, VERSION


def main():
    root = tk.Tk()
    root.withdraw()
    OutingApp(root)
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        messagebox.showinfo(
            f'凌峰出队助手 v{VERSION}',
            f'最新版本请访问：\n{PROJECT_URL}\n\n点击“确定”后启动桌面程序。',
            parent=root,
        )
    root.deiconify()
    root.mainloop()


if __name__ == '__main__':
    main()
