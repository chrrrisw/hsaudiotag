# Created By: Virgil Dupras
# Created On: 2004/12/12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..id3v1 import *
from .testcase import TestCase, eq_

class TCId3v1(TestCase):
    def _do_test(self, filename, expected):
        tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
        eq_(tag.version, expected[0])
        eq_(tag.track, expected[1])
        eq_(tag.title, expected[2])
        eq_(tag.artist, expected[3])
        eq_(tag.album, expected[4])
        eq_(tag.year, expected[5])
        eq_(tag.genre, expected[6])
        eq_(tag.comment, expected[7])
    
    def _do_test_empty_tag(self, tagdata):
        self.failIf(tagdata.exists)
        eq_(tagdata.version, 0)
        eq_(tagdata.size, 0)
        eq_(tagdata.artist, '')
        eq_(tagdata.album, '')
        eq_(tagdata.year, '')
        eq_(tagdata.genre, '')
        eq_(tagdata.comment, '')
        eq_(tagdata.track, 0)
    
    def _do_fail(self, as_filename):
        assert not Id3v1(self.filepath('id3v1/{0}'.format(as_filename))).exists
    
    def test001(self):
        testdata = (TAG_VERSION_1_0, 0, "Title", "Artist", "Album", "2003", "Hip-Hop", "Comment")
        self._do_test("id3v1_001_basic.mp3", testdata)
    
    def test002(self):
        testdata = (TAG_VERSION_1_1, 12, "Title", "Artist", "Album", "2003", "Hip-Hop", "Comment")
        self._do_test("id3v1_002_basic.mp3", testdata)
    
    def test003(self):
        self._do_fail("id3v1_003_basic_F.mp3")
    
    def test004(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "2003", "Blues", "")
        self._do_test("id3v1_004_basic.mp3", testdata)
    
    def test005(self):
        testdata = (TAG_VERSION_1_0, 0, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA", "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
            "cccccccccccccccccccccccccccccC", "2003", "Blues", "dddddddddddddddddddddddddddddD")
        self._do_test("id3v1_005_basic.mp3", testdata)
    
    def test006(self):
        testdata = (TAG_VERSION_1_1, 1, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA", "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
"cccccccccccccccccccccccccccccC", "2003", "Blues", "dddddddddddddddddddddddddddD")
        self._do_test("id3v1_006_basic.mp3", testdata)
    
    def test007(self):
        testdata = (TAG_VERSION_1_0, 0, "12345", "12345", "12345", "2003", "Blues", "12345")
        self._do_test("id3v1_007_basic_W.mp3", testdata)
    
    def test008(self):
        testdata = (TAG_VERSION_1_1, 1, "12345", "12345", "12345", "2003", "Blues", "12345")
        self._do_test("id3v1_008_basic_W.mp3", testdata)
    
    def test009(self):
        testdata = (TAG_VERSION_1_1, 99, "", "", "", "2003", "Blues", "")
        self._do_test("id3v1_009_basic.mp3", testdata)
    
    def test010(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "0000", "Blues", "")
        self._do_test("id3v1_010_year.mp3", testdata)
    
    def test011(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "9999", "Blues", "")
        self._do_test("id3v1_011_year.mp3", testdata)
    
    #About failed year field:
    #I think that a whole tag shouldn't be invalidated because of a badly
    #formated year field. The test suite flag the 3 next files as failures
    #but I will not do so in my testcase
    def test012(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "\x20\x20\x203", "Blues", "")
        self._do_test("id3v1_012_year_F.mp3", testdata)
    
    def test013(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "112", "Blues", "")
        self._do_test("id3v1_013_year_F.mp3", testdata)
    
    def test014(self):
        testdata = (TAG_VERSION_1_0, 0, "", "", "", "", "Blues", "")
        self._do_test("id3v1_014_year_F.mp3", testdata)
    
    def testgenres(self):
        for i in range(15, 95):
            filename = "id3v1_%03d_genre.mp3" % i
            tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
            eq_(tag.genre, tag.title)
        for i in range(95, 163):
            filename = "id3v1_%03d_genre_W.mp3" % i
            tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
            eq_(tag.genre, tag.title)
        for i in range(163, 271):
            filename = "id3v1_%03d_genre_F.mp3" % i
            tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
            eq_(tag.genre, "")
    
    def testzero(self):
        #test that id3v1 handle invalid files gracefully
        self._do_test_empty_tag(Id3v1(self.filepath('zerofile')))
        self._do_test_empty_tag(Id3v1(self.filepath('randomfile')))
    
    def test_non_ascii(self):
        tag = Id3v1(self.filepath('id3v1/id3v1_non_ascii.mp3'))
        assert isinstance(tag.title, str)
        eq_('Title\u00c8', tag.title)
    
    def test_newlines_and_return_carriage(self):
        tag = Id3v1(self.filepath('id3v1/id3v1_newlines.mp3'))
        eq_('foo bar baz', tag.title)
        eq_('foo bar baz', tag.artist)
        eq_('foo bar baz', tag.album)
        eq_('foo bar baz', tag.comment)
        eq_('2  3', tag.year)
    
