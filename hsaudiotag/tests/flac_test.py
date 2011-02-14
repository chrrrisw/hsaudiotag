# Created By: Virgil Dupras
# Created On: 2005/12/17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import flac
from .util import TestData, eq_
from io import open

#--- Metadata block header
def test_header_has_valid_attrs():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    block = flac.MetaDataBlockHeader(fp)
    assert block.valid
    eq_(flac.STREAMINFO, block.type)
    assert not block.last_before_audio
    eq_(0x22, block.size)
    eq_(4, block.offset)
    assert isinstance(block.data(), flac.StreamInfo)
    fp.close()

def test_next():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    header = flac.MetaDataBlockHeader(fp)
    assert header.valid
    eq_(flac.STREAMINFO, header.type)
    header = header.next()
    assert header.valid
    eq_(flac.SEEKTABLE, header.type)
    fp.close()

def test_next_until_eof():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    header = flac.MetaDataBlockHeader(fp)
    count = 0
    while header.valid:
        count += 1
        header = header.next()
    eq_(4496, header.offset)
    eq_(4, count)
    fp.close()

#--- Metadata block
def test_valid_block():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(8, 0)
    refdata = fp.read(0x22)
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    block = header.data()
    eq_(refdata, block.data)
    fp.close()

#--- Stream info
def test_valid_stream_info():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    block = header.data()
    eq_(44100, block.sample_rate)
    eq_(0x779958, block.sample_count)
    fp.close()

#--- Vorbis comment
def test_valid_vorbis_comment():
    fp = open(TestData.filepath(u'flac/test1.flac'), u'rb')
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    while header.type != flac.VORBIS_COMMENT:
        header = header.next()
    assert header.valid
    block = header.data()
    comment = block.comment
    eq_(u'Coolio', comment.artist)
    eq_(u'Country Line', comment.title)
    eq_(u'it takes a thief', comment.album)
    eq_(2, comment.track)
    eq_(u'It sucks', comment.comment)
    eq_(u'1994', comment.year)
    eq_(u'Hip-Hop', comment.genre)
    fp.close()

#--- FLAC
def test_test1():
    f = flac.FLAC(TestData.filepath(u'flac/test1.flac'))
    assert f.valid
    eq_(f.size, 123619)
    eq_(f.sample_rate, 44100)
    eq_(f.duration, 177)
    eq_(f.artist, u'Coolio')
    eq_(f.title, u'Country Line')
    eq_(f.album, u'it takes a thief')
    eq_(f.track, 2)
    eq_(f.comment, u'It sucks')
    eq_(f.year, u'1994')
    eq_(f.genre, u'Hip-Hop')
    eq_(f.audio_offset, 0x1190)
    eq_(f.audio_size, 123619 - 0x1190)

def verify_emptyness(f):
    eq_(0, f.bitrate)
    eq_(0, f.sample_rate)
    eq_(0, f.sample_count)
    eq_(0, f.duration)
    eq_(u'', f.artist)
    eq_(u'', f.album)
    eq_(u'', f.title)
    eq_(u'', f.genre)
    eq_(u'', f.comment)
    eq_(u'', f.year)
    eq_(0, f.track)
    eq_(0, f.audio_offset)
    eq_(0, f.audio_size)

def test_invalid_zerofile():
    f = flac.FLAC(TestData.filepath(u'zerofile'))
    verify_emptyness(f)

def test_invalid_zerofill():
    f = flac.FLAC(TestData.filepath(u'zerofill'))
    verify_emptyness(f)

def test_invalid_randomfile():
    f = flac.FLAC(TestData.filepath(u'randomfile'))
    verify_emptyness(f)

def test_invalid_mp3():
    f = flac.FLAC(TestData.filepath(u'mpeg/test1.mp3'))
    verify_emptyness(f)

def test_invalid_wma():
    f = flac.FLAC(TestData.filepath(u'wma/test1.wma'))
    verify_emptyness(f)

def test_invalid_mp4():
    f = flac.FLAC(TestData.filepath(u'mp4/test1.m4a'))
    verify_emptyness(f)
