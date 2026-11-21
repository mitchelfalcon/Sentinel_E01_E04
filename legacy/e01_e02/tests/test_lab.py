import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import csv
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from client import build_packet, send_one
from server import create_server, read_packet

class TestGEALab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.server = create_server(host='127.0.0.1', port=0, data_dir=Path(cls.tmp.name))
        cls.port = cls.server.server_port
        cls.base = f'http://127.0.0.1:{cls.port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def test_payload_sizes(self):
        for bits in [168, 336, 672, 1344, 8192, 32768, 524288]:
            p = build_packet(bits, 7)
            self.assertEqual(len(p), bits // 8)
            self.assertEqual(read_packet(p)['sequence'], 7)

    def test_health(self):
        with urlopen(f'{self.base}/health') as response:
            data = json.load(response)
        self.assertTrue(data['ok'])
        self.assertFalse(data['internet_requerido'])

    def test_post_and_csv(self):
        p = build_packet(168, 992)
        req = Request(f'{self.base}/api/alert?scenario=cold', data=p, method='POST')
        with urlopen(req) as response:
            ack = json.load(response)
        self.assertEqual(ack['bits'], 168)
        self.assertEqual(ack['sequence'], 992)
        with (Path(self.tmp.name) / 'gea_recepciones.csv').open(encoding='utf-8') as fh:
            rows = list(csv.DictReader(fh))
        self.assertTrue(any(r['sequence'] == '992' and r['scenario'] == 'cold' for r in rows))

    def test_bad_packet_rejected(self):
        req = Request(f'{self.base}/api/alert', data=bytes(20), method='POST')
        with self.assertRaises(HTTPError) as context:
            urlopen(req)
        self.assertEqual(context.exception.code, 400)

    def test_client_rtt(self):
        result = send_one(self.base, 336, 123, 'hot', 3)
        self.assertEqual(result[4], 'OK')
        self.assertGreaterEqual(result[5], 0)

if __name__ == '__main__':
    unittest.main()
