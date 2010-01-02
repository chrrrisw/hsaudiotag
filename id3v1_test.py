# Created By: Virgil Dupras
# Created On: 2004/12/12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .id3v1 import *
from .testcase import TestCase

class TCId3v1(TestCase):
    def _do_test(self, filename, expected):
        tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
        self.assertEqual(tag.version, expected[0])
        self.assertEqual(tag.track, expected[1])
        self.assertEqual(tag.title, expected[2])
        self.assertEqual(tag.artist, expected[3])
        self.assertEqual(tag.album, expected[4])
        self.assertEqual(tag.year, expected[5])
        self.assertEqual(tag.genre, expected[6])
        self.assertEqual(tag.comment, expected[7])
    
    def _do_test_empty_tag(self, tagdata):
        self.failIf(tagdata.exists)
        self.assertEqual(tagdata.version, 0)
        self.assertEqual(tagdata.size, 0)
        self.assertEqual(tagdata.artist, '')
        self.assertEqual(tagdata.album, '')
        self.assertEqual(tagdata.year, '')
        self.assertEqual(tagdata.genre, '')
        self.assertEqual(tagdata.comment, '')
        self.assertEqual(tagdata.track, 0)
    
    def _do_fail(self, as_filename):
        self.assertFalse(Id3v1(self.filepath('id3v1/{0}'.format(as_filename))).exists)
    
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
            self.assertEqual(tag.genre, tag.title)
        for i in range(95, 163):
            filename = "id3v1_%03d_genre_W.mp3" % i
            tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
            self.assertEqual(tag.genre, tag.title)
        for i in range(163, 271):
            filename = "id3v1_%03d_genre_F.mp3" % i
            tag = Id3v1(self.filepath('id3v1/{0}'.format(filename)))
            self.assertEqual(tag.genre, "")
    
    def testzero(self):
        #test that id3v1 handle invalid files gracefully
        self._do_test_empty_tag(Id3v1(self.filepath('zerofile')))
        self._do_test_empty_tag(Id3v1(self.filepath('randomfile')))
    
    def test_non_ascii(self):
        tag = Id3v1(self.filepath('id3v1/id3v1_non_ascii.mp3'))
        self.assert_(isinstance(tag.title, unicode))
        self.assertEqual(u'Title\u00c8', tag.title)
    
    def test_newlines_and_return_carriage(self):
        tag = Id3v1(self.filepath('id3v1/id3v1_newlines.mp3'))
        self.assertEqual('foo bar baz', tag.title)
        self.assertEqual('foo bar baz', tag.artist)
        self.assertEqual('foo bar baz', tag.album)
        self.assertEqual('foo bar baz', tag.comment)
        self.assertEqual('2  3', tag.year)
    
