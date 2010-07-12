# Created By: Virgil Dupras
# Created On: 2005/12/17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from . import flac
from .testcase import TestCase

class TCMetaDataBlockHeader(TestCase):
    def test_valid_attrs(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        block = flac.MetaDataBlockHeader(fp)
        self.assert_(block.valid)
        self.assertEqual(flac.STREAMINFO, block.type)
        self.assertFalse(block.last_before_audio)
        self.assertEqual(0x22, block.size)
        self.assertEqual(4, block.offset)
        self.assertTrue(isinstance(block.data(), flac.StreamInfo))
        fp.close()
    
    def test_next(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        header = flac.MetaDataBlockHeader(fp)
        self.assert_(header.valid)
        self.assertEqual(flac.STREAMINFO, header.type)
        header = next(header)
        self.assertTrue(header.valid)
        self.assertEqual(flac.SEEKTABLE, header.type)
        fp.close()
    
    def test_next_until_eof(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        header = flac.MetaDataBlockHeader(fp)
        count = 0
        while header.valid:
            count += 1
            header = next(header)
        self.assertEqual(4496, header.offset)
        self.assertEqual(4, count)
        fp.close()
    

class TCMetaDataBlock(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(8, 0)
        refdata = fp.read(0x22)
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        block = header.data()
        self.assertEqual(refdata, block.data)
        fp.close()
    

class TCStreamInfo(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        block = header.data()
        self.assertEqual(44100, block.sample_rate)
        self.assertEqual(0x779958, block.sample_count)
        fp.close()
    

class TCVorbisComment(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        while header.type != flac.VORBIS_COMMENT:
            header = next(header)
        self.assert_(header.valid)
        block = header.data()
        comment = block.comment
        self.assertEqual('Coolio', comment.artist)
        self.assertEqual('Country Line', comment.title)
        self.assertEqual('it takes a thief', comment.album)
        self.assertEqual(2, comment.track)
        self.assertEqual('It sucks', comment.comment)
        self.assertEqual('1994', comment.year)
        self.assertEqual('Hip-Hop', comment.genre)
        fp.close()
    

class TCFLAC(TestCase):
    def test_test1(self):
        f = flac.FLAC(self.filepath('flac/test1.flac'))
        self.assertTrue(f.valid)
        self.assertEqual(123619, f.size)
        self.assertEqual(44100, f.sample_rate)
        self.assertEqual(177, f.duration)
        self.assertEqual('Coolio', f.artist)
        self.assertEqual('Country Line', f.title)
        self.assertEqual('it takes a thief', f.album)
        self.assertEqual(2, f.track)
        self.assertEqual('It sucks', f.comment)
        self.assertEqual('1994', f.year)
        self.assertEqual('Hip-Hop', f.genre)
        self.assertEqual(0x1190, f.audio_offset)
        self.assertEqual(123619 - 0x1190, f.audio_size)
    
    def verify_emptyness(self,f):
        self.assertEqual(0, f.bitrate)
        self.assertEqual(0, f.sample_rate)
        self.assertEqual(0, f.sample_count)
        self.assertEqual(0, f.duration)
        self.assertEqual('', f.artist)
        self.assertEqual('', f.album)
        self.assertEqual('', f.title)
        self.assertEqual('', f.genre)
        self.assertEqual('', f.comment)
        self.assertEqual('', f.year)
        self.assertEqual(0, f.track)
        self.assertEqual(0, f.audio_offset)
        self.assertEqual(0, f.audio_size)

    def test_invalid_zerofile(self):
        f = flac.FLAC(self.filepath('zerofile'))
        self.verify_emptyness(f)

    def test_invalid_zerofill(self):
        f = flac.FLAC(self.filepath('zerofill'))
        self.verify_emptyness(f)

    def test_invalid_randomfile(self):
        f = flac.FLAC(self.filepath('randomfile'))
        self.verify_emptyness(f)

    def test_invalid_mp3(self):
        f = flac.FLAC(self.filepath('mpeg/test1.mp3'))
        self.verify_emptyness(f)

    def test_invalid_wma(self):
        f = flac.FLAC(self.filepath('wma/test1.wma'))
        self.verify_emptyness(f)

    def test_invalid_mp4(self):
        f = flac.FLAC(self.filepath('mp4/test1.m4a'))
        self.verify_emptyness(f)

if __name__ == "__main__":
	unittest.main()