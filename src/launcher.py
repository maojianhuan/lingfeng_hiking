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


def smoke_test():
    """构建时实际验证冻结程序的窗口初始化及求解器 DLL。"""
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    value = model.new_bool_var('value')
    model.add(value == 1)
    solver = cp_model.CpSolver()
    if solver.solve(model) != cp_model.OPTIMAL or solver.value(value) != 1:
        raise RuntimeError('CP-SAT 启动检查失败')
    root = tk.Tk()
    root.withdraw()
    try:
        OutingApp(root)
        root.update_idletasks()
    finally:
        root.destroy()


if __name__ == '__main__':
    if sys.argv[1:] == ['--smoke-test']:
        smoke_test()
    else:
        main()
