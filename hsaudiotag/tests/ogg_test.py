# Created By: Virgil Dupras
# Created On: 2005/12/16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import ogg
from .util import TestData, eq_

def test_page_valid_on_test1():
    fp = open(TestData.filepath('ogg/test1.ogg'), 'rb')
    page = ogg.VorbisPage(fp)
    assert page.valid
    eq_(0, page.page_number)
    eq_(0, page.position)
    eq_(30, page.size)
    fp.seek(page.start_offset + page.header_size)
    data = fp.read(page.size)
    eq_(data, page.read())
    page = next(page)
    assert page.valid
    eq_(1, page.page_number)
    eq_(0, page.position)
    eq_(0x10f1, page.size)
    page = next(page)
    assert page.valid
    eq_(2, page.page_number)
    eq_(0, page.position)
    eq_(0x91, page.size)
    page = next(page)
    assert page.valid
    eq_(3, page.page_number)
    eq_(0x2800, page.position)
    eq_(0x1019, page.size)
    fp.close()
    

def test_file_valid_on_test1():
    o = ogg.Vorbis(TestData.filepath('ogg/test1.ogg'))
    eq_(101785, o.size)
    eq_(160, o.bitrate)
    eq_(44100, o.sample_rate)
    eq_(0x6d3eae, o.sample_count)
    eq_(162, o.duration)
    eq_('The White Stripes', o.artist)
    eq_('The White Stripes', o.album)
    eq_('Astro', o.title)
    eq_('', o.genre)
    eq_('', o.comment)
    eq_('1999', o.year)
    eq_(8, o.track)
    eq_(0x1158, o.audio_offset)
    eq_(101785 - 0x1158, o.audio_size)

def test_file_valid_on_test2():
    o = ogg.Vorbis(TestData.filepath('ogg/test2.ogg'))
    eq_(103168, o.size)
    eq_(199, o.bitrate)
    eq_(44100, o.sample_rate)
    eq_(0xb2a2c8, o.sample_count)
    eq_(265, o.duration)
    eq_('Ariane Moffatt', o.artist)
    eq_('Le coeur dans la t\u00eate', o.album)
    eq_('Le coeur dans la t\u00eate', o.title)
    eq_('Pop', o.genre)
    eq_('', o.comment)
    eq_('2005', o.year)
    eq_(3, o.track)
    eq_(0xf79, o.audio_offset)
    eq_(103168 - 0xf79, o.audio_size)

def verify_emptyness(o):
    eq_(0, o.bitrate)
    eq_(0, o.sample_rate)
    eq_(0, o.sample_count)
    eq_(0, o.duration)
    eq_('', o.artist)
    eq_('', o.album)
    eq_('', o.title)
    eq_('', o.genre)
    eq_('', o.comment)
    eq_('', o.year)
    eq_(0, o.track)
    eq_(0, o.audio_offset)
    eq_(0, o.audio_size)

def test_invalid_zerofile():
    o = ogg.Vorbis(TestData.filepath('zerofile'))
    verify_emptyness(o)

def test_invalid_zerofill():
    o = ogg.Vorbis(TestData.filepath('zerofill'))
    verify_emptyness(o)

def test_invalid_randomfile():
    o = ogg.Vorbis(TestData.filepath('randomfile'))
    verify_emptyness(o)

def test_invalid_mp3():
    o = ogg.Vorbis(TestData.filepath('mpeg/test1.mp3'))
    verify_emptyness(o)

def test_invalid_wma():
    o = ogg.Vorbis(TestData.filepath('wma/test1.wma'))
    verify_emptyness(o)

def test_invalid_mp4():
    o = ogg.Vorbis(TestData.filepath('mp4/test1.m4a'))
    verify_emptyness(o)

