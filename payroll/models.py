from dataclasses import dataclass


@dataclass(slots=True)
class Employee:
    id: int | None
    full_name: str
    position: str
    department: str
    base_salary: float
    bonus_percent: float = 0.0
    tax_percent: float = 13.0
    overtime_hours: float = 0.0
    overtime_rate: float = 0.0
    fixed_deduction: float = 0.0
