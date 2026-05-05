import sqlite3
from contextlib import closing
from pathlib import Path

from payroll.models import Employee


class EmployeeRepository:
    def __init__(self, db_path: str = "payroll.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with closing(self._connect()) as con, con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    department TEXT NOT NULL,
                    base_salary REAL NOT NULL,
                    bonus_percent REAL NOT NULL DEFAULT 0,
                    tax_percent REAL NOT NULL DEFAULT 13,
                    overtime_hours REAL NOT NULL DEFAULT 0,
                    overtime_rate REAL NOT NULL DEFAULT 0,
                    fixed_deduction REAL NOT NULL DEFAULT 0
                )
                """
            )

    def list_all(self) -> list[Employee]:
        with closing(self._connect()) as con:
            rows = con.execute(
                """
                SELECT id, full_name, position, department, base_salary, bonus_percent, tax_percent,
                       overtime_hours, overtime_rate, fixed_deduction
                FROM employees ORDER BY id
                """
            ).fetchall()
        return [Employee(*row) for row in rows]

    def create(self, employee: Employee) -> int:
        with closing(self._connect()) as con, con:
            cur = con.execute(
                """
                INSERT INTO employees(
                    full_name, position, department, base_salary, bonus_percent, tax_percent,
                    overtime_hours, overtime_rate, fixed_deduction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee.full_name,
                    employee.position,
                    employee.department,
                    employee.base_salary,
                    employee.bonus_percent,
                    employee.tax_percent,
                    employee.overtime_hours,
                    employee.overtime_rate,
                    employee.fixed_deduction,
                ),
            )
            return int(cur.lastrowid)

    def update(self, employee: Employee) -> None:
        if employee.id is None:
            raise ValueError("employee.id is required")
        with closing(self._connect()) as con, con:
            con.execute(
                """
                UPDATE employees
                SET full_name=?, position=?, department=?, base_salary=?, bonus_percent=?, tax_percent=?,
                    overtime_hours=?, overtime_rate=?, fixed_deduction=?
                WHERE id=?
                """,
                (
                    employee.full_name,
                    employee.position,
                    employee.department,
                    employee.base_salary,
                    employee.bonus_percent,
                    employee.tax_percent,
                    employee.overtime_hours,
                    employee.overtime_rate,
                    employee.fixed_deduction,
                    employee.id,
                ),
            )

    def delete(self, employee_id: int) -> None:
        with closing(self._connect()) as con, con:
            con.execute("DELETE FROM employees WHERE id=?", (employee_id,))
