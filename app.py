import tkinter as tk
from tkinter import messagebox, ttk

from payroll.auth import AuthService
from payroll.models import Employee
from payroll.repository import EmployeeRepository
from payroll.service import PayrollCalculator


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИМСИТ Payroll Pro — Вход")
        self.geometry("540x420")
        self.configure(bg="#0f172a")
        self.auth = AuthService()
        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Card.TFrame", background="#111827")
        style.configure("Card.TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#111827", foreground="#93c5fd", font=("Segoe UI", 18, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.place(relx=0.5, rely=0.5, anchor="center", width=430, height=320)

        ttk.Label(card, text="Payroll Pro", style="Title.TLabel").pack(anchor="w", pady=(0, 14))
        ttk.Label(card, text="Логин", style="Card.TLabel").pack(anchor="w")
        self.username = tk.StringVar()
        ttk.Entry(card, textvariable=self.username, font=("Segoe UI", 11)).pack(fill="x", pady=(4, 12))

        ttk.Label(card, text="Пароль", style="Card.TLabel").pack(anchor="w")
        self.password = tk.StringVar()
        ttk.Entry(card, textvariable=self.password, show="•", font=("Segoe UI", 11)).pack(fill="x", pady=(4, 16))

        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Button(row, text="Войти", style="Primary.TButton", command=self.login).pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Регистрация", command=self.register).pack(side="left")

    def login(self):
        if self.auth.authenticate(self.username.get(), self.password.get()):
            self.destroy()
            PayrollApp().mainloop()
            return
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register(self):
        try:
            self.auth.register(self.username.get(), self.password.get())
            messagebox.showinfo("Готово", "Пользователь зарегистрирован")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))


class PayrollApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИМСИТ — Payroll Pro")
        self.geometry("1280x740")
        self.configure(bg="#0b1220", padx=16, pady=16)
        self.repo = EmployeeRepository()
        self._apply_style()
        self._build_layout()
        self._refresh_grid()

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabelframe", background="#111827", foreground="#e5e7eb")
        style.configure("TLabelframe.Label", background="#111827", foreground="#93c5fd", font=("Segoe UI", 10, "bold"))
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", background="#0f172a", fieldbackground="#0f172a", foreground="#e5e7eb", rowheight=28)
        style.map("Treeview", background=[("selected", "#1d4ed8")])

    def _build_layout(self):
        self.vars = {k: tk.StringVar(v) for k, v in {
            "full_name": "", "position": "", "department": "", "base_salary": "",
            "bonus_percent": "0", "tax_percent": "13", "overtime_hours": "0",
            "overtime_rate": "0", "fixed_deduction": "0"
        }.items()}

        form = ttk.LabelFrame(self, text="Карточка сотрудника", padding=12)
        form.pack(fill="x", pady=(0, 10))
        fields = [
            ("ФИО", "full_name"), ("Должность", "position"), ("Подразделение", "department"),
            ("Оклад", "base_salary"), ("Премия %", "bonus_percent"), ("Налог %", "tax_percent"),
            ("Сверхурочные часы", "overtime_hours"), ("Ставка сверхурочных", "overtime_rate"), ("Удержание", "fixed_deduction")
        ]
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 3)
            c *= 2
            ttk.Label(form, text=label).grid(row=r, column=c, sticky="w", padx=5, pady=5)
            ttk.Entry(form, textvariable=self.vars[key], width=28 if key in {"full_name", "position", "department"} else 18).grid(row=r, column=c+1, padx=5, pady=5, sticky="w")

        row = ttk.Frame(form)
        row.grid(row=3, column=0, columnspan=6, sticky="w", pady=(10, 0))
        for text, cmd in [("Добавить", self.add_employee), ("Обновить", self.update_employee), ("Удалить", self.delete_employee), ("Рассчитать", self.calculate_selected)]:
            ttk.Button(row, text=text, command=cmd).pack(side="left", padx=4)

        table_box = ttk.LabelFrame(self, text="Реестр сотрудников", padding=8)
        table_box.pack(fill="both", expand=True)
        cols = ("id","full_name","position","department","base_salary","bonus_percent","tax_percent","overtime_hours","overtime_rate","fixed_deduction")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings")
        for c, t, w in [
            ("id","ID",55),("full_name","ФИО",220),("position","Должность",150),("department","Подразделение",160),
            ("base_salary","Оклад",110),("bonus_percent","Премия %",90),("tax_percent","Налог %",90),
            ("overtime_hours","Сверхур. часы",110),("overtime_rate","Ставка",100),("fixed_deduction","Удерж.",100)
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.result_var = tk.StringVar("Готово к расчёту")
        ttk.Label(self, textvariable=self.result_var, font=("Segoe UI", 10, "bold"), foreground="#86efac", background="#0b1220").pack(anchor="w", pady=(10, 0))

    def _refresh_grid(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for e in self.repo.list_all():
            self.tree.insert("", "end", values=(e.id,e.full_name,e.position,e.department,e.base_salary,e.bonus_percent,e.tax_percent,e.overtime_hours,e.overtime_rate,e.fixed_deduction))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            raise ValueError("Выберите сотрудника")
        return int(self.tree.item(sel[0], "values")[0])

    def _read_emp(self, selected_id=None):
        try:
            emp = Employee(selected_id, self.vars["full_name"].get().strip(), self.vars["position"].get().strip(), self.vars["department"].get().strip(),
                           float(self.vars["base_salary"].get()), float(self.vars["bonus_percent"].get()), float(self.vars["tax_percent"].get()),
                           float(self.vars["overtime_hours"].get()), float(self.vars["overtime_rate"].get()), float(self.vars["fixed_deduction"].get()))
        except ValueError as e:
            raise ValueError("Проверьте числовые поля") from e
        if not emp.full_name or not emp.position or not emp.department:
            raise ValueError("ФИО, должность и подразделение обязательны")
        return emp

    def add_employee(self):
        try:
            self.repo.create(self._read_emp())
            self._refresh_grid()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def update_employee(self):
        try:
            self.repo.update(self._read_emp(self._selected_id()))
            self._refresh_grid()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_employee(self):
        try:
            self.repo.delete(self._selected_id())
            self._refresh_grid()
        except ValueError as e:
            messagebox.showwarning("Внимание", str(e))

    def on_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        for key, val in zip(["full_name","position","department","base_salary","bonus_percent","tax_percent","overtime_hours","overtime_rate","fixed_deduction"], vals[1:]):
            self.vars[key].set(str(val))

    def calculate_selected(self):
        try:
            emp = self._read_emp(self._selected_id())
            br = PayrollCalculator.calculate(base_salary=emp.base_salary, bonus_percent=emp.bonus_percent, tax_percent=emp.tax_percent,
                                            overtime_hours=emp.overtime_hours, overtime_rate=emp.overtime_rate, fixed_deduction=emp.fixed_deduction)
            self.result_var.set(f"{emp.full_name}: начислено {br.gross_income:.2f} ₽, налог {br.tax_amount:.2f} ₽, удержание {br.fixed_deduction:.2f} ₽, к выплате {br.net_income:.2f} ₽")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    LoginWindow().mainloop()
