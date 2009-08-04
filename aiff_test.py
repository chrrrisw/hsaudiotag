# Created By: Virgil Dupras
# Created On: 2008-09-09
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from . import aiff
from .testcase import TestCase

class AiffFile(TestCase):
    def test_random(self):
        # a random file is not valid
        f = aiff.File(self.filepath('randomfile'))
        self.assertFalse(f.valid)
    
    def test_long_comm_field(self):
        # some COMM fields are longer than 18 bytes. They must be supported
        f = aiff.File(self.filepath('aiff/long_comm_field.aif'))
        self.assertTrue(f.valid)
        self.assertEqual(f.duration, 132)
    
    def test_with_id3(self):
        # this file is a track encoded from a CD with iTunes. It has a ID3 chunk. The SSND chunk
        # has been manually truncated (the file was 22mb)
        f = aiff.File(self.filepath('aiff/with_id3.aif'))
        self.assertTrue(f.valid)
        self.assertEqual(f.duration, 132)
        self.assertEqual(f.sample_rate, 44100)
        self.assertEqual(f.bitrate, 1411200)
        self.assertEqual(f.tag.artist, 'Assimil') # The id3v2 module takes care of it, no need to test it further
        self.assertEqual(f.audio_offset, 46)
        self.assertEqual(f.audio_size, 42)
    

if __name__ == "__main__":
	unittest.main()
