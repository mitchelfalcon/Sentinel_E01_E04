import unittest
from sentinel.distance_model import simulate_distance,P_LINK,DISTANCES_KM
from sentinel.mesh_sim import simulate

class TestDistance(unittest.TestCase):
    def test_deterministic_sensitivity(self):
        a,sa=simulate_distance(20261123,200);b,sb=simulate_distance(20261123,200)
        self.assertEqual(a,b);self.assertEqual(sa,sb)
        self.assertEqual(len(a),200*len(P_LINK)*len(DISTANCES_KM))
        self.assertEqual(len(sa),len(P_LINK)*len(DISTANCES_KM))
    def test_e04_reference(self):
        events,s=simulate(seed=42,count=100,fail_after=50)
        self.assertEqual(s['delivered'],97)
        self.assertAlmostEqual(s['p50_ms'],44.964,places=3)
        self.assertAlmostEqual(s['p95_ms'],67.484,places=3)
        self.assertEqual(set(r['provenance'] for r in events),{'SIMULADO_NO_RF'})

if __name__=='__main__':unittest.main()
