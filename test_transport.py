import unittest
from protocol import packet, config_query
from transfer import Device

class FakeHID:
    def __init__(self,responses): self.responses=list(responses);self.writes=[]
    def write(self,data): self.writes.append(data);return len(data)
    def read(self,size,timeout): return self.responses.pop(0)

class TransportTests(unittest.TestCase):
    def test_discards_unrelated_ack_before_matching(self):
        request=packet(0x21,b'abc',56)
        ack=request[:4]+bytes(4)
        device=Device();device.handle=FakeHID([packet(1)[:8],ack])
        self.assertEqual(device.transact(request),ack)
        self.assertEqual(device.handle.writes,[request])

    def test_rejected_write_is_not_retried(self):
        request=packet(0x23)
        device=Device();device.handle=FakeHID([request[:4]+bytes(3)+b'\xff'])
        with self.assertRaises(OSError): device.transact(request)
        self.assertEqual(device.handle.writes,[request])

    def test_query_payload_can_contain_ff(self):
        request=config_query(0)
        ack=request[:4]+b'\x00\x01\x00\xff'
        device=Device();device.handle=FakeHID([ack])
        self.assertEqual(device.transact(request),ack)
