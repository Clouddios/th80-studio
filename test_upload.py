import unittest
from PIL import Image
from protocol import packet, photo_config, encode_frame
from transfer import upload

class UploadTests(unittest.TestCase):
    def test_erase_packet_matches_original_program_header(self):
        self.assertEqual(packet(0x23), bytes.fromhex('04 23 00 23 00 00 00 00')+bytes(56))

    def test_rejects_oversized_or_unrepresentable_packets(self):
        for args in [(0,b'',0),(0x21,bytes(57),0),(0x21,b'',-1),(0x21,b'',0x1000000)]:
            with self.assertRaises(ValueError): packet(*args)

    def test_frame_uses_rgb565_big_endian_and_flash_alignment(self):
        image=Image.new('RGB',(240,135))
        image.putpixel((0,0),(255,0,0));image.putpixel((1,0),(0,255,0));image.putpixel((2,0),(0,0,255))
        encoded=encode_frame(image)
        self.assertEqual(encoded[:6],bytes.fromhex('f800 07e0 001f'))
        self.assertEqual(len(encoded),65536)
        self.assertEqual(encoded[64800:],bytes(736))

    def test_photo_config_changes_only_display_and_frame_counts(self):
        original=bytes(range(48))
        modified=photo_config(original)
        self.assertEqual(modified[33],1);self.assertEqual(modified[34],1);self.assertEqual(modified[46],1)
        for i in set(range(48))-{33,34,46}: self.assertEqual(modified[i],original[i])
        with self.assertRaises(ValueError): photo_config(bytes(47))

    def test_upload_streams_both_slots_and_commits(self):
        calls=[]
        def exchange(command,data=b'',position=0): calls.append((command,data,position));return bytes(4)
        frame=bytes([0xa5])*65536
        upload(exchange,bytes(48),frame,lambda value:None)
        self.assertEqual([c[0] for c in calls[:5]],[1,6,2,0x23,1])
        self.assertEqual(calls[-1][0],2)
        chunks=[c for c in calls if c[0]==0x21]
        self.assertEqual(b''.join(c[1] for c in chunks),frame+frame)
        self.assertEqual(chunks[0][2],0)
        self.assertEqual(chunks[-1][2]+len(chunks[-1][1]),131072)

    def test_failure_stops_transfer_without_retrying_erase(self):
        commands=[]
        def exchange(command,data=b'',position=0):
            commands.append(command)
            if command==6: raise TimeoutError('No ACK')
            return bytes(4)
        with self.assertRaises(TimeoutError): upload(exchange,bytes(48),bytes(65536),lambda value:None)
        self.assertEqual(commands,[1,6])

if __name__=='__main__': unittest.main()
