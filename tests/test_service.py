import unittest

from payroll.service import PayrollCalculator


class TestPayrollCalculator(unittest.TestCase):
    def test_calculate(self):
        result = PayrollCalculator.calculate(
            base_salary=100000,
            bonus_percent=10,
            tax_percent=13,
            overtime_hours=5,
            overtime_rate=1000,
            fixed_deduction=1200,
        )
        self.assertEqual(result.bonus_amount, 10000)
        self.assertEqual(result.gross_income, 115000)
        self.assertEqual(result.tax_amount, 14950)
        self.assertEqual(result.net_income, 98850)

    def test_negative_value_raises(self):
        with self.assertRaises(ValueError):
            PayrollCalculator.calculate(
                base_salary=-1,
                bonus_percent=0,
                tax_percent=13,
                overtime_hours=0,
                overtime_rate=0,
                fixed_deduction=0,
            )


if __name__ == '__main__':
    unittest.main()
