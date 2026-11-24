import unittest, tempfile, csv, hashlib, json
from pathlib import Path
from sentinel.mesh_sim import simulate,choose_route
from sentinel.analyze import analyze,parse,stats,wilson95
from sentinel.verify_rf import verify
class TestSuite(unittest.TestCase):
 def test_e04_is_deterministic(self):
  a,sa=simulate(42,30,10);b,sb=simulate(42,30,10);self.assertEqual(a,b);self.assertEqual(sa,sb)
 def test_routing_fails_over(self):
  self.assertEqual(choose_route(set()),('A','B','C'));self.assertEqual(choose_route({'B'}),('A','D','C'));self.assertIsNone(choose_route({'B','D'}))
 def test_four_states(self):
  rows,_=simulate(5,2,2);states={r['state'] for r in rows};self.assertTrue({'GENERADO','RECIBIDO','ENTREGADO','ATENDIDO_SIMULADO'}<=states)
 def test_reference_csv(self):
  a=analyze(out=str(Path(tempfile.gettempdir())/'sentinel_stats_test.json'));self.assertEqual(a['e01']['n'],50);self.assertEqual(a['e02_hot']['n'],50)
 def test_wilson_50_of_50(self):
  self.assertEqual(wilson95(50,50),(92.87,100.0))
 def test_rf_empty_template(self):
  v=verify('data/plantillas/e04_rf_log_template.csv');self.assertEqual(v['records'],0)
if __name__=='__main__':unittest.main()
