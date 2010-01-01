# Created By: Virgil Dupras
# Created On: 2005/12/16
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from . import ogg
from .testcase import TestCase

class TCOggVorbisPage(TestCase):
    def test_valid_test1(self):
        fp = open(self.filepath('ogg/test1.ogg'), 'rb')
        page = ogg.VorbisPage(fp)
        self.assert_(page.valid)
        self.assertEqual(0, page.page_number)
        self.assertEqual(0, page.position)
        self.assertEqual(30, page.size)
        fp.seek(page.start_offset + page.header_size)
        data = fp.read(page.size)
        self.assertEqual(data, page.read())
        page = page.next()
        self.assert_(page.valid)
        self.assertEqual(1, page.page_number)
        self.assertEqual(0, page.position)
        self.assertEqual(0x10f1, page.size)
        page = page.next()
        self.assert_(page.valid)
        self.assertEqual(2, page.page_number)
        self.assertEqual(0, page.position)
        self.assertEqual(0x91, page.size)
        page = page.next()
        self.assert_(page.valid)
        self.assertEqual(3, page.page_number)
        self.assertEqual(0x2800, page.position)
        self.assertEqual(0x1019, page.size)
        fp.close()
    

class TCOggVorbis(TestCase):
    def test_valid_test1(self):
        o = ogg.Vorbis(self.filepath('ogg/test1.ogg'))
        self.assertEqual(101785, o.size)
        self.assertEqual(160, o.bitrate)
        self.assertEqual(44100, o.sample_rate)
        self.assertEqual(0x6d3eae, o.sample_count)
        self.assertEqual(162, o.duration)
        self.assertEqual('The White Stripes', o.artist)
        self.assertEqual('The White Stripes', o.album)
        self.assertEqual('Astro', o.title)
        self.assertEqual('', o.genre)
        self.assertEqual('', o.comment)
        self.assertEqual('1999', o.year)
        self.assertEqual(8, o.track)
        self.assertEqual(0x1158, o.audio_offset)
        self.assertEqual(101785 - 0x1158, o.audio_size)

    def test_valid_test2(self):
        o = ogg.Vorbis(self.filepath('ogg/test2.ogg'))
        self.assertEqual(103168, o.size)
        self.assertEqual(199, o.bitrate)
        self.assertEqual(44100, o.sample_rate)
        self.assertEqual(0xb2a2c8, o.sample_count)
        self.assertEqual(265, o.duration)
        self.assertEqual('Ariane Moffatt', o.artist)
        self.assertEqual(u'Le coeur dans la t\u00eate', o.album)
        self.assertEqual(u'Le coeur dans la t\u00eate', o.title)
        self.assertEqual('Pop', o.genre)
        self.assertEqual('', o.comment)
        self.assertEqual('2005', o.year)
        self.assertEqual(3, o.track)
        self.assertEqual(0xf79, o.audio_offset)
        self.assertEqual(103168 - 0xf79, o.audio_size)

    def verify_emptyness(self, o):
        self.assertEqual(0, o.bitrate)
        self.assertEqual(0, o.sample_rate)
        self.assertEqual(0, o.sample_count)
        self.assertEqual(0, o.duration)
        self.assertEqual('', o.artist)
        self.assertEqual('', o.album)
        self.assertEqual('', o.title)
        self.assertEqual('', o.genre)
        self.assertEqual('', o.comment)
        self.assertEqual('', o.year)
        self.assertEqual(0, o.track)
        self.assertEqual(0, o.audio_offset)
        self.assertEqual(0, o.audio_size)

    def test_invalid_zerofile(self):
        o = ogg.Vorbis(self.filepath('zerofile'))
        self.verify_emptyness(o)

    def test_invalid_zerofill(self):
        o = ogg.Vorbis(self.filepath('zerofill'))
        self.verify_emptyness(o)

    def test_invalid_randomfile(self):
        o = ogg.Vorbis(self.filepath('randomfile'))
        self.verify_emptyness(o)

    def test_invalid_mp3(self):
        o = ogg.Vorbis(self.filepath('mpeg/test1.mp3'))
        self.verify_emptyness(o)

    def test_invalid_wma(self):
        o = ogg.Vorbis(self.filepath('wma/test1.wma'))
        self.verify_emptyness(o)

    def test_invalid_mp4(self):
        o = ogg.Vorbis(self.filepath('mp4/test1.m4a'))
        self.verify_emptyness(o)
    

if __name__ == "__main__":
	unittest.main()
