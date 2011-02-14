# Created By: Virgil Dupras
# Created On: 2010-12-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import auto, mp4
from .squeeze import expand_mp4, expand_mpeg
from .util import TestData, eq_

def test_invalid():
    # An invalid file is correctly detected as such
    f = auto.File(TestData.filepath(u'randomfile'))
    assert not f.valid

def test_mpeg():
    # auto.File can detect mpeg files.
    f = auto.File(expand_mpeg(TestData.filepath(u'mpeg/test1.mp3')))
    assert f.valid
    eq_(f.size, 2355703)
    eq_(f.bitrate, 128)
    eq_(f.duration, 147)
    eq_(f.audio_offset, 0x9a1)
    eq_(f.audio_size, f.size - 128 - 0x9a1)
    eq_(f.sample_rate, 44100)
    eq_(f.artist, u'Alice & The Serial Numbers')
    eq_(f.album, u'Mission 1')
    eq_(f.title, u'Intro Missions Started')
    eq_(f.genre, u'Electronic')
    eq_(f.year, u'2001')
    eq_(f.comment, u'0000039F 000003E6 00001D0B 000021C7 000111B5 000111B5 00007545 00008000 0000EA60 0000EA60')
    eq_(f.track, 1)

def test_mp4():
    # auto.File can detect mp4 files.
    f = auto.File(expand_mp4(TestData.filepath(u'mp4/test1.m4a')))
    assert f.valid
    eq_(f.title, u'This Is How It Goes')
    eq_(f.artist, u'Billy Talent')
    eq_(f.album, u'Billy Talent')
    eq_(f.genre, u'Punk')
    eq_(f.comment, u'')
    eq_(f.size, 3364781)
    eq_(f.sample_rate, 44100)
    eq_(f.duration, 207)
    eq_(f.bitrate, 128)
    eq_(f.year, u'2003')
    eq_(f.track, 1)

def test_wma():
    # auto.File can detect wma files.
    f = auto.File(TestData.filepath(u'wma/test1.wma'))
    assert f.valid
    eq_(f.artist, u'Modest Mouse')
    eq_(f.album, u'The Moon & Antarctica')
    eq_(f.title, u'3rd Planet')
    eq_(f.genre, u'Rock')
    eq_(f.comment, u'')
    eq_(f.year, u'2000')
    eq_(f.track, 1)
    eq_(f.bitrate, 192)
    eq_(f.size, 77051)
    eq_(f.duration, 239)
    eq_(f.audio_offset, 0x15a0)
    eq_(f.audio_size, 0x582682 - 0x15a0)

def test_ogg():
    # auto.File can detect ogg files.
    f = auto.File(TestData.filepath(u'ogg/test1.ogg'))
    assert f.valid
    eq_(f.size, 101785)
    eq_(f.bitrate, 160)
    eq_(f.sample_rate, 44100)
    eq_(f.duration, 162)
    eq_(f.artist, u'The White Stripes')
    eq_(f.album, u'The White Stripes')
    eq_(f.title, u'Astro')
    eq_(f.genre, u'')
    eq_(f.comment, u'')
    eq_(f.year, u'1999')
    eq_(f.track, 8)
    eq_(f.audio_offset, 0x1158)
    eq_(f.audio_size, 101785 - 0x1158)

def test_flac():
    # auto.File can detect flac files.
    f = auto.File(TestData.filepath(u'flac/test1.flac'))
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

def test_aiff():
    # auto.File can detect aiff files.
    f = auto.File(TestData.filepath(u'aiff/with_id3.aif'))
    assert f.valid
    eq_(f.duration, 132)
    eq_(f.sample_rate, 44100)
    eq_(f.bitrate, 1411200)
    eq_(f.artist, u'Assimil')
    eq_(f.audio_offset, 46)
    eq_(f.audio_size, 42)

def test_aiff_without_tag():
    # We don't crash on AIFF files without tags.
    f = auto.File(TestData.filepath(u'aiff/without_id3.aif')) # no crash
    assert f.valid
    eq_(f.duration, 132)
    eq_(f.artist, u'')
    eq_(f.track, 0)

def test_close_is_called_on_mp4(monkeypatch):
    # The mp4 file has to be closed after being read.
    global closed
    closed = False
    def mock_close(self):
        global closed
        closed = True
    monkeypatch.setattr(mp4.File, u'close', mock_close)
    f = auto.File(expand_mp4(TestData.filepath(u'mp4/test1.m4a')))
    assert closed
