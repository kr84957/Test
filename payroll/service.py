from dataclasses import dataclass


@dataclass(slots=True)
class PayrollBreakdown:
    base_salary: float
    bonus_amount: float
    overtime_amount: float
    gross_income: float
    tax_amount: float
    fixed_deduction: float
    net_income: float


class PayrollCalculator:
    @staticmethod
    def calculate(
        *,
        base_salary: float,
        bonus_percent: float,
        tax_percent: float,
        overtime_hours: float,
        overtime_rate: float,
        fixed_deduction: float,
    ) -> PayrollBreakdown:
        PayrollCalculator._validate_non_negative(
            base_salary=base_salary,
            bonus_percent=bonus_percent,
            tax_percent=tax_percent,
            overtime_hours=overtime_hours,
            overtime_rate=overtime_rate,
            fixed_deduction=fixed_deduction,
        )

        bonus_amount = base_salary * (bonus_percent / 100)
        overtime_amount = overtime_hours * overtime_rate
        gross_income = base_salary + bonus_amount + overtime_amount
        tax_amount = gross_income * (tax_percent / 100)
        net_income = gross_income - tax_amount - fixed_deduction

        return PayrollBreakdown(
            base_salary=round(base_salary, 2),
            bonus_amount=round(bonus_amount, 2),
            overtime_amount=round(overtime_amount, 2),
            gross_income=round(gross_income, 2),
            tax_amount=round(tax_amount, 2),
            fixed_deduction=round(fixed_deduction, 2),
            net_income=round(net_income, 2),
        )

    @staticmethod
    def _validate_non_negative(**values: float) -> None:
        for name, value in values.items():
            if value < 0:
                raise ValueError(f"{name} must be >= 0")
