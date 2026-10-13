import unittest
from color_wheel import normalize_hex, wheel_hex, rgb_configuration

class ColorTests(unittest.TestCase):
    def test_hex_is_normalized_and_invalid_input_is_rejected(self):
        self.assertEqual(normalize_hex('35ff00'),'#35FF00')
        self.assertEqual(normalize_hex(' #0066ff '),'#0066FF')
        for value in ('#gg0000','#123','red','#12345678'):
            with self.assertRaises(ValueError): normalize_hex(value)

    def test_wheel_center_and_red_edge_and_darkness(self):
        self.assertEqual(wheel_hex(0,0,100),'#FFFFFF')
        self.assertEqual(wheel_hex(100,0,100),'#FF0000')
        self.assertEqual(wheel_hex(100,0,100,0),'#000000')

    def test_rgb_write_only_changes_mode_and_rgb_preserving_auxiliary_byte(self):
        original=bytes(range(48))
        result=rgb_configuration(original,'#0066FF')
        self.assertEqual(result[5:9],bytes([0,0,102,255]))
        self.assertEqual(result[:5]+result[9:],original[:5]+original[9:])
