import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from PIL import Image
from protocol import animation_config, clock_config, display_config
from transfer import upload_animation, write_config
from media import load_media

class AnimationClockTests(unittest.TestCase):
    def test_animation_config_preserves_unrelated_settings(self):
        old=bytes(range(48));new=animation_config(old,3,120)
        self.assertEqual([new[i] for i in (33,34,43,44,46)],[1,3,120,0,3])
        for i in set(range(48))-{33,34,43,44,46}: self.assertEqual(new[i],old[i])

    def test_invalid_animation_never_writes_usb(self):
        calls=[]
        for frames,delay in [([],100),([bytes(65536)]*19,100),([b'bad'],100),([bytes(65536)],59)]:
            with self.assertRaises(ValueError): upload_animation(lambda *args:calls.append(args),bytes(48),frames,delay,lambda value:None)
        self.assertEqual(calls,[])

    def test_animation_stream_order_and_counts(self):
        calls=[];progress=[]
        frames=[bytes([1])*65536,bytes([2])*65536]
        upload_animation(lambda cmd,data=b'',position=0:calls.append((cmd,data,position)),bytes(48),frames,100,progress.append)
        config=next(data for cmd,data,pos in calls if cmd==6)
        self.assertEqual((config[34],config[46],config[43]),(2,2,100))
        stream=b''.join(data for cmd,data,pos in calls if cmd==0x21)
        self.assertEqual(stream,frames[0]+frames[1]+frames[0]+frames[1])
        chunks=[(data,pos) for cmd,data,pos in calls if cmd==0x21]
        self.assertEqual(chunks[-1][1]+len(chunks[-1][0]),262144)
        self.assertEqual(progress[-1],100)

    def test_clock_bcd_and_sunday_zero_preserve_images(self):
        old=bytes(range(48));new=clock_config(old,datetime(2026,10,11,23,58,49))
        self.assertEqual(new[33:42],bytes.fromhex('00 22 49 58 23 00 11 10 26'))
        for i in set(range(48))-{33,35,36,37,38,39,40,41}: self.assertEqual(old[i],new[i])
        self.assertEqual(display_config(new,1)[33],1)

    def test_clock_write_never_erases_images(self):
        calls=[]
        write_config(lambda cmd,data=b'',position=0:calls.append((cmd,data)),clock_config(bytes(48),datetime(2026,10,10)))
        self.assertEqual([c[0] for c in calls],[1,6,2])

    def test_gif_keeps_both_frames_and_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'two.gif'
            Image.new('RGB',(20,20),'red').save(path,save_all=True,append_images=[Image.new('RGB',(20,20),'blue')],duration=100,loop=0)
            media=load_media(path)
            self.assertEqual(len(media.frames),2);self.assertEqual(media.delay_ms,100)
            self.assertEqual(media.frames[0].getpixel((120,60)),(255,0,0))
            self.assertEqual(media.frames[1].getpixel((120,60)),(0,0,255))

    def test_long_gif_samples_whole_loop_instead_of_truncating(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'long.gif'
            frames=[Image.new('RGB',(8,8),(i*5,0,0)) for i in range(36)]
            frames[0].save(path,save_all=True,append_images=frames[1:],duration=100,loop=0)
            media=load_media(path)
            self.assertEqual(media.original_count,36)
            self.assertEqual(len(media.frames),18);self.assertEqual(media.delay_ms,200)
            self.assertGreater(media.frames[-1].getpixel((0,0))[0],160)

    def test_static_transparency_is_composited_on_black(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'alpha.png'
            Image.new('RGBA',(20,20),(255,0,0,0)).save(path)
            media=load_media(path)
            self.assertEqual(media.frames[0].getpixel((0,0)),(0,0,0))
            self.assertIsNone(media.delay_ms)
