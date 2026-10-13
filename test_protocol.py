import unittest
from protocol import config_query, matches_response, select_device

class ProtocolTests(unittest.TestCase):
    def test_query_is_read_command_with_expected_checksum(self):
        self.assertEqual(config_query(0), bytes.fromhex('04 09 00 05 04 00 00 00') + bytes(56))
        self.assertEqual(config_query(44)[:8], bytes.fromhex('04 35 00 05 04 2c 00 00'))

    def test_query_rejects_offsets_outside_config(self):
        for offset in [-1, 1, 48, 0x1000000]:
            with self.assertRaises(ValueError): config_query(offset)

    def test_rejects_short_stale_and_wrong_command_response(self):
        query=config_query(0)
        self.assertFalse(matches_response(query,b'\x04'))
        self.assertFalse(matches_response(query,bytes.fromhex('04 35 00 05')+bytes(4)))
        self.assertFalse(matches_response(query,bytes.fromhex('04 09 00 06')+bytes(4)))
        self.assertTrue(matches_response(query,bytes.fromhex('04 09 00 05 01 02 03 04')))

    def test_selects_only_exact_product_and_vendor_interface(self):
        good={'vendor_id':0x320f,'product_id':0x5055,'product_string':'EPOMAKER TH80 Pro V2','usage_page':0xff1c,'usage':0x92,'path':b'expected'}
        unrelated=dict(good,product_string='ZUOYA GMK87')
        keyboard=dict(good,usage_page=1,usage=6)
        self.assertEqual(select_device([unrelated,keyboard,good])['path'],b'expected')
        with self.assertRaises(ValueError): select_device([unrelated,keyboard])
        with self.assertRaises(ValueError): select_device([good,dict(good,path=b'second')])

if __name__=='__main__': unittest.main()
