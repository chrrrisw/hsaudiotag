# Created By: Virgil Dupras
# Created On: 2004/12/12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..id3v1 import *
from .util import TestData, eq_

def _do_test(filename, expected):
    tag = Id3v1(TestData.filepath(u'id3v1/{0}'.format(filename)))
    eq_(tag.version, expected[0])
    eq_(tag.track, expected[1])
    eq_(tag.title, expected[2])
    eq_(tag.artist, expected[3])
    eq_(tag.album, expected[4])
    eq_(tag.year, expected[5])
    eq_(tag.genre, expected[6])
    eq_(tag.comment, expected[7])

def _do_test_empty_tag(tagdata):
    assert not tagdata.exists
    eq_(tagdata.version, 0)
    eq_(tagdata.size, 0)
    eq_(tagdata.artist, u'')
    eq_(tagdata.album, u'')
    eq_(tagdata.year, u'')
    eq_(tagdata.genre, u'')
    eq_(tagdata.comment, u'')
    eq_(tagdata.track, 0)

def _do_fail(as_filename):
    assert not Id3v1(TestData.filepath(u'id3v1/{0}'.format(as_filename))).exists

def test001():
    testdata = (TAG_VERSION_1_0, 0, u"Title", u"Artist", u"Album", u"2003", u"Hip-Hop", u"Comment")
    _do_test(u"id3v1_001_basic.mp3", testdata)

def test002():
    testdata = (TAG_VERSION_1_1, 12, u"Title", u"Artist", u"Album", u"2003", u"Hip-Hop", u"Comment")
    _do_test(u"id3v1_002_basic.mp3", testdata)

def test003():
    _do_fail(u"id3v1_003_basic_F.mp3")

def test004():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"2003", u"Blues", u"")
    _do_test(u"id3v1_004_basic.mp3", testdata)

def test005():
    testdata = (TAG_VERSION_1_0, 0, u"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA", u"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
        u"cccccccccccccccccccccccccccccC", u"2003", u"Blues", u"dddddddddddddddddddddddddddddD")
    _do_test(u"id3v1_005_basic.mp3", testdata)

def test006():
    testdata = (TAG_VERSION_1_1, 1, u"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA", u"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
u"cccccccccccccccccccccccccccccC", u"2003", u"Blues", u"dddddddddddddddddddddddddddD")
    _do_test(u"id3v1_006_basic.mp3", testdata)

def test007():
    testdata = (TAG_VERSION_1_0, 0, u"12345", u"12345", u"12345", u"2003", u"Blues", u"12345")
    _do_test(u"id3v1_007_basic_W.mp3", testdata)

def test008():
    testdata = (TAG_VERSION_1_1, 1, u"12345", u"12345", u"12345", u"2003", u"Blues", u"12345")
    _do_test(u"id3v1_008_basic_W.mp3", testdata)

def test009():
    testdata = (TAG_VERSION_1_1, 99, u"", u"", u"", u"2003", u"Blues", u"")
    _do_test(u"id3v1_009_basic.mp3", testdata)

def test010():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"0000", u"Blues", u"")
    _do_test(u"id3v1_010_year.mp3", testdata)

def test011():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"9999", u"Blues", u"")
    _do_test(u"id3v1_011_year.mp3", testdata)

#About failed year field:
#I think that a whole tag shouldn't be invalidated because of a badly
#formated year field. The test suite flag the 3 next files as failures
#but I will not do so in my testcase
def test012():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"\x20\x20\x203", u"Blues", u"")
    _do_test(u"id3v1_012_year_F.mp3", testdata)

def test013():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"112", u"Blues", u"")
    _do_test(u"id3v1_013_year_F.mp3", testdata)

def test014():
    testdata = (TAG_VERSION_1_0, 0, u"", u"", u"", u"", u"Blues", u"")
    _do_test(u"id3v1_014_year_F.mp3", testdata)

def testgenres():
    for i in xrange(15, 95):
        filename = u"id3v1_%03d_genre.mp3" % i
        tag = Id3v1(TestData.filepath(u'id3v1/{0}'.format(filename)))
        eq_(tag.genre, tag.title)
    for i in xrange(95, 163):
        filename = u"id3v1_%03d_genre_W.mp3" % i
        tag = Id3v1(TestData.filepath(u'id3v1/{0}'.format(filename)))
        eq_(tag.genre, tag.title)
    for i in xrange(163, 271):
        filename = u"id3v1_%03d_genre_F.mp3" % i
        tag = Id3v1(TestData.filepath(u'id3v1/{0}'.format(filename)))
        eq_(tag.genre, u"")

def testzero():
    #test that id3v1 handle invalid files gracefully
    _do_test_empty_tag(Id3v1(TestData.filepath(u'zerofile')))
    _do_test_empty_tag(Id3v1(TestData.filepath(u'randomfile')))

def test_non_ascii():
    tag = Id3v1(TestData.filepath(u'id3v1/id3v1_non_ascii.mp3'))
    assert isinstance(tag.title, unicode)
    eq_(u'Title\u00c8', tag.title)

def test_newlines_and_return_carriage():
    tag = Id3v1(TestData.filepath(u'id3v1/id3v1_newlines.mp3'))
    eq_(u'foo bar baz', tag.title)
    eq_(u'foo bar baz', tag.artist)
    eq_(u'foo bar baz', tag.album)
    eq_(u'foo bar baz', tag.comment)
    eq_(u'2  3', tag.year)

