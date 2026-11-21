import unittest
from sentinel.uart_mesh import payload21,decode21,pack,unpack,FRAME
class TestUART(unittest.TestCase):
    def test_frame_size_and_payload(self):
        p=payload21('LUNA',42,100)
        self.assertEqual(len(p),21)
        frame=pack(1,'A','B',1,3,p)
        self.assertEqual(len(frame),FRAME.size)
        q=unpack(frame)
        self.assertEqual(q['packet']['alias'],'LUNA')
        self.assertEqual(q['packet']['sequence'],42)
        self.assertEqual(q['forwarder'],'B')
        self.assertEqual(q['hop'],1)
    def test_crc_detects_change(self):
        frame=bytearray(pack(1,'A','A',0,4,payload21()))
        frame[14]^=0x10
        with self.assertRaises(ValueError):unpack(bytes(frame))
    def test_payload_crc(self):
        p=bytearray(payload21());p[6]^=1
        with self.assertRaises(ValueError):decode21(bytes(p))
if __name__=='__main__':unittest.main()
