# Created By: Virgil Dupras
# Created On: 2005/02/06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from . import wma
from .testcase import TestCase

class TCWma(TestCase):
    def test1(self):
        # test1.wma is a normal, valid wma file
        w = wma.WMADecoder(self.filepath('wma/test1.wma'))
        self.assertEqual(w.artist, 'Modest Mouse')
        self.assertEqual(w.album, 'The Moon & Antarctica')
        self.assertEqual(w.title, '3rd Planet')
        self.assertEqual(w.genre, 'Rock')
        self.assertEqual(w.comment, '')
        self.assertEqual(w.year, '2000')
        self.assertEqual(w.track, 1)
        self.assertEqual(w.bitrate, 192)
        self.assertEqual(w.size, 77051)
        self.assertEqual(w.duration, 239)
        self.assertEqual(w.audio_offset, 0x15a0)
        self.assertEqual(w.audio_size, 0x582682 - 0x15a0)
        self.assertTrue(w.valid)

    def test2(self):
        # test2.wma is a mpeg file, thus invalid
        w = wma.WMADecoder(self.filepath('wma/test2.wma'))
        self.assertFalse(w.valid)
        self.assertEqual(w.audio_offset, 0)
        self.assertEqual(w.audio_size, 0)

    def testZeroFile(self):
        w = wma.WMADecoder(self.filepath('zerofile'))
        self.assert_(not w.valid)
    
    def test1_non_ascii(self):
        # The album is Unicode
        w = wma.WMADecoder(self.filepath('wma/test1_non_ascii.wma'))
        self.assert_(isinstance(w.album, unicode))
        self.assertEqual(w.album, u'The Moon \u00c8 Antarctica')
    
    def test1_no_track(self):
        # This is a file with no WM/TRACK field
        w = wma.WMADecoder(self.filepath('wma/test1_no_track.wma'))
        self.assertEqual(0, w.track)
        
    def test3(self):
        # This is the file that made a customer's musicGuru copy bug. It was because it has no track.
        w = wma.WMADecoder(self.filepath('wma/test3.wma'))
        self.assertEqual(w.artist, 'Giovanni Marradi')
        self.assertEqual(w.album, 'Always')
        self.assertEqual(w.title, 'Gideon')
        self.assertEqual(w.genre, 'Easy Listening')
        self.assertEqual(w.comment, '')
        self.assertEqual(w.year, '')
        self.assertEqual(w.track, 0)
        self.assertEqual(w.bitrate, 48)
        self.assertEqual(w.size, 80767)
        self.assertEqual(w.duration, 238)
        self.assert_(w.valid)
    
    def test3_truncated_unicode(self):
        # This is the file has its WM/GENRE field last char truncated. Its value, 'Easy Listening' 
        # also has one char truncated. 'Gideon' in the unnamed fields part also has one truncated char.
        w = wma.WMADecoder(self.filepath('wma/test3_truncated_unicode.wma'))
        self.assertEqual(w.genre, 'Easy Listening')
        self.assertEqual(w.title, 'Gideon')
        
    def test3_invalid_unicode_surregate(self):
        # This is the file has an invalid char (0xffff) in its WM/GENRE field. 'Gideon' in the 
        # unnamed fields part also has an invalid surregate (0xdbff and another 0xdbff).
        w = wma.WMADecoder(self.filepath('wma/test3_invalid_unicode_surregate.wma'))
        self.assertEqual(w.genre, '')
        self.assertEqual(w.title, '')
        
    def test3_incomplete(self):
        # This file is truncated right in the middle of a field header. The error that it made was an
        # unpack error.
        w = wma.WMADecoder(self.filepath('wma/test3_incomplete.wma'))
        self.assertEqual(w.genre, '')
        self.assertEqual(w.title, '')
        
    def test4(self):
        # VBR
        w = wma.WMADecoder(self.filepath('wma/test4.wma'))
        self.assertEqual(w.artist, 'Red Hot Chilly Peppers')
        self.assertEqual(w.album, '')
        self.assertEqual(w.title, 'Scar Tissue')
        self.assertEqual(w.genre, '')
        self.assertEqual(w.comment, '')
        self.assertEqual(w.year, '')
        self.assertEqual(w.track, 2)
        self.assertEqual(w.bitrate, 370)
        self.assertEqual(w.size, 673675)
        self.assertEqual(w.duration, 217)
        self.assertTrue(w.valid)
    
    def test5(self):
        # Another VBR
        w = wma.WMADecoder(self.filepath('wma/test5.wma'))
        self.assertEqual(w.bitrate, 303)
        self.assertEqual(w.duration, 295)
        
    def test6(self):
        # Another VBR. This one had a huge, 30 seconds, duration gap
        w = wma.WMADecoder(self.filepath('wma/test6.wma'))
        self.assertEqual(w.bitrate, 422)
        self.assertEqual(w.duration, 298)
        
    def test7(self):
        # Yet another VBR wma with buggy duration.
        w = wma.WMADecoder(self.filepath('wma/test7.wma'))
        self.assertEqual(w.bitrate, 327)
        self.assertEqual(w.duration, 539)
    

if __name__ == "__main__":
	unittest.main()
