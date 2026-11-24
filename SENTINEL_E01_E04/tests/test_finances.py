import unittest
from scripts.validate_budget import validate_budget
class TestFinances(unittest.TestCase):
 def test_budget_balances(self):
  r=validate_budget();self.assertEqual(r['capex_MXN'],66800)
  self.assertEqual(r['opex_mensual_MXN'],2140)
  self.assertEqual(r['tco_36_meses_MXN'],143840)
if __name__=='__main__':unittest.main()
