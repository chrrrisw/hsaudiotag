# Created By: Virgil Dupras
# Created On: 2005/12/17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import flac
from .testcase import TestCase, eq_

class TCMetaDataBlockHeader(TestCase):
    def test_valid_attrs(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        block = flac.MetaDataBlockHeader(fp)
        assert block.valid
        eq_(flac.STREAMINFO, block.type)
        assert not block.last_before_audio
        eq_(0x22, block.size)
        eq_(4, block.offset)
        assert isinstance(block.data(), flac.StreamInfo)
        fp.close()
    
    def test_next(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        header = flac.MetaDataBlockHeader(fp)
        assert header.valid
        eq_(flac.STREAMINFO, header.type)
        header = next(header)
        assert header.valid
        eq_(flac.SEEKTABLE, header.type)
        fp.close()
    
    def test_next_until_eof(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0) #the flac id is not a part of a block
        header = flac.MetaDataBlockHeader(fp)
        count = 0
        while header.valid:
            count += 1
            header = next(header)
        eq_(4496, header.offset)
        eq_(4, count)
        fp.close()
    

class TCMetaDataBlock(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(8, 0)
        refdata = fp.read(0x22)
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        block = header.data()
        eq_(refdata, block.data)
        fp.close()
    

class TCStreamInfo(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        block = header.data()
        eq_(44100, block.sample_rate)
        eq_(0x779958, block.sample_count)
        fp.close()
    

class TCVorbisComment(TestCase):
    def test_valid(self):
        fp = open(self.filepath('flac/test1.flac'), 'rb')
        fp.seek(4, 0)
        header = flac.MetaDataBlockHeader(fp)
        while header.type != flac.VORBIS_COMMENT:
            header = next(header)
        assert header.valid
        block = header.data()
        comment = block.comment
        eq_('Coolio', comment.artist)
        eq_('Country Line', comment.title)
        eq_('it takes a thief', comment.album)
        eq_(2, comment.track)
        eq_('It sucks', comment.comment)
        eq_('1994', comment.year)
        eq_('Hip-Hop', comment.genre)
        fp.close()
    

class TCFLAC(TestCase):
    def test_test1(self):
        f = flac.FLAC(self.filepath('flac/test1.flac'))
        assert f.valid
        eq_(123619, f.size)
        eq_(44100, f.sample_rate)
        eq_(177, f.duration)
        eq_('Coolio', f.artist)
        eq_('Country Line', f.title)
        eq_('it takes a thief', f.album)
        eq_(2, f.track)
        eq_('It sucks', f.comment)
        eq_('1994', f.year)
        eq_('Hip-Hop', f.genre)
        eq_(0x1190, f.audio_offset)
        eq_(123619 - 0x1190, f.audio_size)
    
    def verify_emptyness(self,f):
        eq_(0, f.bitrate)
        eq_(0, f.sample_rate)
        eq_(0, f.sample_count)
        eq_(0, f.duration)
        eq_('', f.artist)
        eq_('', f.album)
        eq_('', f.title)
        eq_('', f.genre)
        eq_('', f.comment)
        eq_('', f.year)
        eq_(0, f.track)
        eq_(0, f.audio_offset)
        eq_(0, f.audio_size)

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
