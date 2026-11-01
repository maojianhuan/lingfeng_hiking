"""凌峰出队助手原生桌面界面。"""
from pathlib import Path
from zipfile import BadZipFile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.font import nametofont

from openpyxl.utils.exceptions import InvalidFileException

from duties import assign_duties, duty_rows
from finance import make_insurance_report, make_report, read_members, ATTENDING, WITHDRAW_DAY_BEFORE, WITHDRAW_SAME_DAY

VERSION = '0.3.2'
PROJECT_URL = 'https://github.com/maojianhuan/lingfeng_hiking'


class OutingApp:
    def __init__(self, root):
        self.root = root
        self.members = []
        self.source_path = None
        self.assignment_input = None
        self.assignment = None
        self.role_indices = []
        self.withdrawals = {}
        root.title(f'凌峰出队助手 v{VERSION}')
        root.geometry('1040x740')
        root.minsize(880, 640)
        font_family = nametofont('TkDefaultFont', root=root).actual('family')
        style = ttk.Style(root)
        style.configure('Title.TLabel', font=(font_family, 20, 'bold'))
        style.configure('Heading.TLabel', font=(font_family, 11, 'bold'))
        outer = ttk.Frame(root, padding=20)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='凌峰出队助手', style='Title.TLabel').pack(anchor='w')
        ttk.Label(outer, text='导入报名表 → 选择成员及负责人 → 导出财务与保险名单').pack(anchor='w', pady=(5, 14))
        import_bar = ttk.Frame(outer)
        import_bar.pack(fill='x')
        ttk.Button(import_bar, text='导入报名 Excel', command=self.import_file).pack(side='left')
        self.file_label = ttk.Label(import_bar, text='尚未导入报名表')
        self.file_label.pack(side='left', padx=12)
        tabs = ttk.Notebook(outer)
        tabs.pack(fill='both', expand=True, pady=12)
        body = ttk.Frame(tabs)
        tabs.add(body, text='职能安排')
        self.finance_page = ttk.Frame(tabs, padding=10)
        tabs.add(self.finance_page, text='财务结算')
        tabs.bind('<<NotebookTabChanged>>', lambda event: self.refresh_finance_members())
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        member_panel = ttk.LabelFrame(body, text='本次出队成员 · 按报名时间排序', padding=10)
        member_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 16))
        member_panel.rowconfigure(1, weight=1)
        member_panel.columnconfigure(0, weight=1)
        ttk.Label(member_panel, text='勾选纳入结算；退出时间在财务页设置').grid(row=0, column=0, sticky='w', pady=(0, 8))
        self.member_list = tk.Listbox(member_panel, selectmode=tk.MULTIPLE, exportselection=False,
                                     width=23, activestyle='none', font=(font_family, 11),
                                     selectbackground='#246B55', selectforeground='white',
                                     relief='flat', borderwidth=0)
        self.member_list.grid(row=1, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(member_panel, orient='vertical', command=self.member_list.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.member_list.configure(yscrollcommand=scrollbar.set)
        self.member_list.bind('<<ListboxSelect>>', self.selection_changed)
        buttons = ttk.Frame(member_panel)
        buttons.grid(row=2, column=0, sticky='ew', pady=(8, 0))
        ttk.Button(buttons, text='全选', command=lambda: self.select_all(True)).pack(side='left')
        ttk.Button(buttons, text='清空', command=lambda: self.select_all(False)).pack(side='left', padx=8)
        self.count_label = ttk.Label(member_panel, text='已选 0 人')
        self.count_label.grid(row=3, column=0, sticky='w', pady=(8, 0))

        main = ttk.Frame(body)
        main.grid(row=0, column=1, sticky='nsew')
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        form = ttk.LabelFrame(main, text='负责人', padding=12)
        form.grid(row=0, column=0, sticky='ew')
        self.roles = {}
        for column, role in enumerate(('领队', '副领队', '财务')):
            form.columnconfigure(column, weight=1)
            ttk.Label(form, text=role).grid(row=0, column=column, sticky='w', padx=4)
            combo = ttk.Combobox(form, state='readonly', values=['未指定'], width=16)
            combo.current(0)
            combo.grid(row=1, column=column, sticky='ew', padx=4, pady=(5, 12))
            combo.bind('<<ComboboxSelected>>', self.configuration_changed)
            self.roles[role] = combo
        preview = ttk.LabelFrame(main, text='自动职能安排', padding=12)
        preview.grid(row=2, column=0, sticky='nsew')
        preview.rowconfigure(0, weight=1)
        preview.columnconfigure(0, weight=1)
        self.preview = tk.Text(preview, width=50, height=11, wrap='word', state='disabled',
                               font=(font_family, 11), relief='flat', padx=6, pady=6)
        self.preview.grid(row=0, column=0, sticky='nsew')
        preview_scroll = ttk.Scrollbar(preview, orient='vertical', command=self.preview.yview)
        preview_scroll.grid(row=0, column=1, sticky='ns')
        self.preview.configure(yscrollcommand=preview_scroll.set)
        ttk.Label(preview, text='联合优化志愿与负责人；优先自愿、其次非新人；装备、后勤、队医负责须为学院路校区。',
                  wraplength=600).grid(row=1, column=0, sticky='w', pady=(8, 0))
        exports = ttk.Frame(main)
        exports.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        ttk.Button(exports, text='导出购买保险信息', command=self.export_insurance).pack(side='left', padx=12)
        self.build_finance_page()
        self.status = tk.StringVar(value='请选择报名明细 Excel；全部处理均在本机完成。')
        ttk.Label(outer, textvariable=self.status, wraplength=960).pack(anchor='w')
        self.set_preview('导入报名表后，指定领队和财务即可自动生成职能安排。')

    def set_preview(self, text):
        self.preview.configure(state='normal')
        self.preview.delete('1.0', 'end')
        self.preview.insert('1.0', text)
        self.preview.configure(state='disabled')

    def import_file(self):
        path = filedialog.askopenfilename(parent=self.root, title='选择报名明细',
                                          filetypes=[('Excel 工作簿', '*.xlsx')])
        if not path:
            return
        try:
            self.load_file(path)
        except (ValueError, OSError, BadZipFile, InvalidFileException) as exc:
            messagebox.showerror('导入失败', str(exc), parent=self.root)

    def load_file(self, path):
        members = read_members(path)
        if not members:
            raise ValueError('报名表没有成员记录。')
        self.members = members
        self.withdrawals = {}
        self.expenses.delete(*self.expenses.get_children())
        self.source_path = Path(path)
        self.assignment_input = None
        self.assignment = None
        self.role_indices = []
        for combo in self.roles.values():
            combo.configure(values=['未指定'])
            combo.current(0)
        self.member_list.delete(0, 'end')
        for member in members:
            self.member_list.insert('end', member['姓名'])
        self.member_list.selection_set(0, 'end')
        self.file_label.configure(text=self.source_path.name)
        self.status.set(f'已导入 {len(members)} 人，请指定领队、副领队和财务。')
        self.selection_changed()

    def select_all(self, selected):
        if selected:
            self.member_list.selection_set(0, 'end')
        else:
            self.member_list.selection_clear(0, 'end')
        self.selection_changed()

    def selection_changed(self, event=None):
        previous = {role: self.role_indices[combo.current() - 1]
                    if combo.current() > 0 else None for role, combo in self.roles.items()}
        selected = [i for i in self.member_list.curselection() if i not in self.withdrawals]
        names = [self.members[i]['姓名'] for i in selected]
        # 同名成员在负责人选择框中用报名位置区分，成员列表仍仅显示姓名。
        labels = [name if names.count(name) == 1 else f'{name}（第 {i + 1} 位报名）'
                  for i, name in zip(selected, names)]
        self.role_indices = selected
        for role, combo in self.roles.items():
            combo.configure(values=['未指定'] + labels)
            old = previous[role]
            combo.current(selected.index(old) + 1 if old in selected else 0)
        self.count_label.configure(text=f'实际出队 {len(selected)} / {len(self.members)} 人')
        self.configuration_changed()
        self.refresh_finance_members()

    def selected_members(self, require_roles=False):
        selected = [i for i in self.member_list.curselection() if i not in self.withdrawals]
        if not selected:
            raise ValueError('请至少选择一名出队成员。')
        if not require_roles:
            return [dict(self.members[i]) for i in selected]
        roles = {role: self.role_indices[combo.current() - 1] if combo.current() > 0 else None
                 for role, combo in self.roles.items()}
        if roles['领队'] is None or roles['财务'] is None:
            raise ValueError('请指定领队和财务；副领队可暂不指定。')
        specified = [i for i in roles.values() if i is not None]
        if len(set(specified)) != len(specified):
            raise ValueError('领队、副领队和财务不能由同一人兼任，请调整选择。')
        return [{**self.members[i], '角色': next((role for role, index in roles.items() if index == i), '队员')}
                for i in selected]

    def get_assignment(self):
        chosen = self.selected_members(require_roles=True)
        if self.assignment_input != chosen:
            self.assignment = assign_duties(chosen)
            self.assignment_input = chosen
        return self.assignment

    def configuration_changed(self, event=None):
        try:
            assigned = self.get_assignment()
        except ValueError as exc:
            self.set_preview(str(exc))
            return
        rows = duty_rows(assigned)
        heading = rows[0]
        lines = [f'领队：{heading[1]}　副领队：{heading[3]}　财务：{heading[5]}']
        lines.extend(f'{duty}：{names}' for duty, names in rows[1:])
        self.set_preview('\n\n'.join(lines))

    def build_finance_page(self):
        page = self.finance_page
        ttk.Label(page, text='一天线结算：提前两天以上退出请在“职能安排”页取消选择；其他退出人员保留勾选，在此设置退出时间。',
                  wraplength=760).pack(anchor='w')
        member_table = ttk.Frame(page)
        member_table.pack(fill='x', pady=8)
        self.finance_list = ttk.Treeview(member_table, columns=('name', 'state'), show='headings', height=5, selectmode='browse')
        self.finance_list.heading('name', text='结算成员')
        self.finance_list.heading('state', text='出队状态')
        self.finance_list.pack(side='left', fill='x', expand=True)
        scrollbar = ttk.Scrollbar(member_table, orient='vertical', command=self.finance_list.yview)
        scrollbar.pack(side='right', fill='y')
        self.finance_list.configure(yscrollcommand=scrollbar.set)
        self.finance_list.bind('<<TreeviewSelect>>', self.finance_member_selected)
        state_bar = ttk.Frame(page)
        state_bar.pack(fill='x')
        ttk.Label(state_bar, text='选中成员的状态').pack(side='left')
        self.withdrawal_state = ttk.Combobox(state_bar, state='readonly', width=22,
                                             values=[ATTENDING, WITHDRAW_DAY_BEFORE, WITHDRAW_SAME_DAY])
        self.withdrawal_state.current(0)
        self.withdrawal_state.pack(side='left', padx=8)
        ttk.Button(state_bar, text='应用状态', command=self.apply_withdrawal).pack(side='left')
        costs = ttk.Frame(page)
        costs.pack(fill='x', pady=12)
        self.bus = tk.StringVar(value='1000')
        self.radios = tk.StringVar(value='2')
        ttk.Label(costs, text='包车费（元）').pack(side='left')
        ttk.Entry(costs, textvariable=self.bus, width=12).pack(side='left', padx=8)
        ttk.Label(costs, text='对讲机数量（12 元／台）').pack(side='left')
        ttk.Spinbox(costs, textvariable=self.radios, from_=0, to=999, width=8).pack(side='left', padx=8)
        ttk.Label(page, text='额外公共物资支出（所有结算成员均摊，含提前一天及当天退出人员）').pack(anchor='w')
        expense_table = ttk.Frame(page)
        expense_table.pack(fill='both', expand=True, pady=8)
        self.expenses = ttk.Treeview(expense_table, columns=('name', 'amount'), show='headings', height=3)
        self.expenses.heading('name', text='支出名称')
        self.expenses.heading('amount', text='总金额（元）')
        self.expenses.pack(side='left', fill='both', expand=True)
        expense_scroll = ttk.Scrollbar(expense_table, orient='vertical', command=self.expenses.yview)
        expense_scroll.pack(side='right', fill='y')
        self.expenses.configure(yscrollcommand=expense_scroll.set)
        entry = ttk.Frame(page)
        entry.pack(fill='x')
        self.expense_name = tk.StringVar()
        self.expense_amount = tk.StringVar()
        ttk.Label(entry, text='名称').pack(side='left')
        ttk.Entry(entry, textvariable=self.expense_name, width=24).pack(side='left', padx=6)
        ttk.Label(entry, text='金额').pack(side='left')
        ttk.Entry(entry, textvariable=self.expense_amount, width=12).pack(side='left', padx=6)
        ttk.Button(entry, text='添加支出', command=self.add_expense).pack(side='left')
        ttk.Button(entry, text='删除选中支出', command=self.delete_expense).pack(side='left', padx=6)
        ttk.Label(page, text='提前一天退出：公共物资＋保险＋20 元车费；当天退出改为正常均摊剩余车费。退出免领队费和装备费。\n融资默认 0，导出后填写；退款＝预收－费用－融资。',
                  wraplength=760).pack(anchor='w', pady=10)
        ttk.Button(page, text='导出财务与职能报表', command=self.export_finance).pack(anchor='w')

    def refresh_finance_members(self):
        if not hasattr(self, 'finance_list'):
            return
        old = self.finance_list.selection()
        self.finance_list.delete(*self.finance_list.get_children())
        for i in self.member_list.curselection():
            self.finance_list.insert('', 'end', iid=str(i), values=(self.members[i]['姓名'], self.withdrawals.get(i, ATTENDING)))
        if old and self.finance_list.exists(old[0]):
            self.finance_list.selection_set(old[0])

    def finance_member_selected(self, event=None):
        chosen = self.finance_list.selection()
        if chosen:
            self.withdrawal_state.set(self.withdrawals.get(int(chosen[0]), ATTENDING))

    def apply_withdrawal(self):
        chosen = self.finance_list.selection()
        if not chosen:
            return
        index = int(chosen[0])
        state = self.withdrawal_state.get()
        if state == ATTENDING:
            self.withdrawals.pop(index, None)
        else:
            self.withdrawals[index] = state
        self.selection_changed()

    @staticmethod
    def money(text, label):
        from decimal import Decimal, InvalidOperation
        try:
            amount = Decimal(text.strip())
        except InvalidOperation:
            raise ValueError(f'{label}须为非负金额，最多两位小数。')
        if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
            raise ValueError(f'{label}须为非负金额，最多两位小数。')
        return float(amount)

    def add_expense(self):
        try:
            name = self.expense_name.get().strip()
            if not name:
                raise ValueError('请输入公共支出名称。')
            amount = self.money(self.expense_amount.get(), '公共支出')
            self.expenses.insert('', 'end', values=(name, amount))
            self.expense_name.set('')
            self.expense_amount.set('')
        except ValueError as exc:
            messagebox.showerror('无法添加支出', str(exc), parent=self.root)

    def delete_expense(self):
        for item in self.expenses.selection():
            self.expenses.delete(item)

    def cost_values(self):
        bus = self.money(self.bus.get(), '包车费用')
        text = self.radios.get().strip()
        if not text.isascii() or not text.isdecimal():
            raise ValueError('对讲机数量必须为非负整数。')
        return bus, int(text)

    def save_report(self, content, name):
        path = filedialog.asksaveasfilename(parent=self.root, title='保存 Excel 报表',
                                            initialfile=name, defaultextension='.xlsx',
                                            filetypes=[('Excel 工作簿', '*.xlsx')], confirmoverwrite=True)
        if not path:
            return
        target = Path(path)
        if self.source_path and target.resolve() == self.source_path.resolve():
            raise ValueError('不能覆盖当前报名源文件，请使用其他文件名保存报表。')
        target.write_bytes(content)
        self.status.set(f'已保存：{target}')

    def export_finance(self):
        try:
            bus, radios = self.cost_values()
            assigned = self.get_assignment()
            active = iter(assigned)
            settlement = [({**self.members[i], '角色': '退出', '出队状态': self.withdrawals[i]}
                           if i in self.withdrawals else {**next(active), '出队状态': ATTENDING})
                          for i in self.member_list.curselection()]
            expenses = [(self.expenses.item(item, 'values')[0],
                         float(self.expenses.item(item, 'values')[1])) for item in self.expenses.get_children()]
            content = make_report(settlement, bus, radios, 12, expenses)
            self.save_report(content, '出队财务报表.xlsx')
        except (ValueError, OSError) as exc:
            messagebox.showerror('财务报表无法导出', str(exc), parent=self.root)

    def export_insurance(self):
        try:
            content = make_insurance_report(self.selected_members())
            self.save_report(content, '出队保险名单.xlsx')
        except (ValueError, OSError) as exc:
            messagebox.showerror('保险名单无法导出', str(exc), parent=self.root)


def main():
    root = tk.Tk()
    OutingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
