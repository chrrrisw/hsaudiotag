# Created By: Virgil Dupras
# Created On: 2005/01/15
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from .id3v2 import Id3v2, Header, POS_END, _read_id3_string
from .squeeze import expand_mpeg
from .testcase import TestCase

class TCId3v2(TestCase):
    def testNormal(self):
        tag = Id3v2(expand_mpeg(self.filepath('id3v2/normal.mp3')))
        self.assertEqual(tag.size,4096)
        self.assertEqual(tag.data_size,4086)
        self.assert_(tag.exists)
        self.assertEqual(tag.flags,())
        self.assertEqual(tag.title,'La Primavera')
        self.assertEqual(tag.artist,'Manu Chao')
        self.assertEqual(tag.album,'Proxima Estacion Esperanza (AD')
        self.assertEqual(tag.year,'2001')
        self.assertEqual(tag.genre,'Latin')
        self.assertEqual(tag.comment,'http://www.EliteMP3.ws')
    
    def testNotag(self):
        tag = Id3v2(expand_mpeg(self.filepath('id3v2/notag.mp3')))
        self.assert_(not tag.exists)
    
    def testThatspot(self):
        tag = Id3v2(self.filepath('id3v2/thatspot.tag'))
        expected_comment = """THAT SPOT RIGHT THERE (14 second demo clip)

This 14 second demo clip was recorded at CD-Quality using the standard MusicMatch Jukebox
software program.  If you like this track, you can click the "Buy CD" button in your MusicMatch
Jukebox "Track Info" window, and you'll be connected to a recommended online music retailer.


Enjoy your copy of MusicMatch Jukebox!"""
        self.assertEqual(tag.comment.replace('\r',''),expected_comment.replace('\r',''))
        self.assertEqual(tag.title,'That Spot Right There')
        self.assertEqual(tag.artist,'Carey Bell')
        self.assertEqual(tag.album,'Mellow Down Easy')
        self.assertEqual(tag.year,'')
        self.assertEqual(tag.genre,'Blues')
    
    def testOzzy(self):
        tag = Id3v2(self.filepath('id3v2/ozzy.tag'))
        self.assertEqual(tag.title,'Bark At The Moon')
        self.assertEqual(tag.artist,'Ozzy Osbourne')
        self.assertEqual(tag.album,'Bark At The Moon')
        self.assertEqual(tag.year,'1983')
        self.assertEqual(tag.genre,'Metal')
        self.assertEqual(tag.comment,'None')
        self.assertEqual(tag.track,1)
    
    def testUnicode(self):
        tag = Id3v2(self.filepath('id3v2/230-unicode.tag'))
        self.assertEqual(tag.frames['TXXX'].data.text,'example text frame\nThis text and the description should be in Unicode.')
    
    def testWithFooter(self):
        tag = Id3v2(expand_mpeg(self.filepath('id3v2/with_footer.mp3')))
        self.assert_(tag.exists)
        self.assertEqual(tag.artist,'AFI')
        self.assertEqual(tag.position,POS_END)
    
    def testTrack(self):
        tag = Id3v2(expand_mpeg(self.filepath('id3v2/test_track.mp3')))
        self.assertEqual(tag.track,1)
    
    def testZeroFile(self):
        tag = Id3v2(self.filepath('zerofile'))
        self.assert_(not tag.exists)
    
    def test_non_ascii_non_unicode(self):
        #Test a v2 tag with non-ascii char in a non-unicode string
        tag = Id3v2(self.filepath('id3v2/ozzy_non_ascii.tag'))
        self.assert_(isinstance(tag.title,unicode))
        self.assertEqual(tag.title,u'Bark At The \u00c8\u00c9\u00ca\u00cb')
    
    def test_numeric_genre(self):
        #A file with a genre field containing (<number>)
        tag = Id3v2(self.filepath('id3v2/numeric_genre.tag'))
        self.assertEqual('Metal',tag.genre)
    
    def test_numeric_genre2(self):
        #A file with a genre field containing (<number>)
        tag = Id3v2(self.filepath('id3v2/numeric_genre2.tag'))
        self.assertEqual('Rock',tag.genre)
    
    def test_numeric_genre3(self):
        #like numeric_genre, but the number is not between ()
        tag = Id3v2(self.filepath('id3v2/numeric_genre3.tag'))
        self.assertEqual('Rock',tag.genre)
    
    def test_unicode_truncated(self):
        tag = Id3v2(self.filepath('id3v2/230-unicode_truncated.tag'))
        self.assertEqual(tag.frames['TXXX'].data.text,
            'example text frame\nThis text and the description should be in Unicode.')
    
    def test_unicode_invalid_surregate(self):
        tag = Id3v2(self.filepath('id3v2/230-unicode_surregate.tag'))
        self.assertEqual(tag.frames['TXXX'].data.text,'')
    
    def test_unicode_comment(self):
        tag = Id3v2(self.filepath('id3v2/230-unicode_comment.tag'))
        self.assertEqual(tag.frames['COMM'].data.title,'example text frame')
        self.assertEqual(tag.frames['COMM'].data.text,
            'This text and the description should be in Unicode.')
        self.assertEqual(tag.comment,
            'This text and the description should be in Unicode.')
    
    def test_TLEN(self):
        tag = Id3v2(self.filepath('mpeg/test8.mp3'))
        self.assertEqual(tag.duration,299)
    
    def test_DecodeTrack(self):
        tag = Id3v2(self.filepath('zerofile'))
        method = tag._decode_track
        self.assertEqual(42,method('42'))
        self.assertEqual(0,method(''))
        self.assertEqual(12,method('12/24'))
        self.assertEqual(0,method(' '))
        self.assertEqual(0,method('/'))
        self.assertEqual(0,method('foo/12'))
    
    def test_Decodeduration(self):
        tag = Id3v2(self.filepath('zerofile'))
        tag._get_frame_text = lambda _:'4200'
        self.assertEqual(4,tag.duration)
        tag._get_frame_text = lambda _:''
        self.assertEqual(0,tag.duration)
        tag._get_frame_text = lambda _:'foo'
        self.assertEqual(0,tag.duration)
    
    def test_newlines(self):
        tag = Id3v2(self.filepath('id3v2/newlines.tag'))
        self.assertEqual('foo bar baz',tag.title)
        self.assertEqual('foo bar baz',tag.artist)
        self.assertEqual('foo bar baz',tag.album)
        self.assertEqual('foo bar baz',tag.genre)
        self.assertEqual('foo bar baz',tag.year)
        self.assertEqual('foo\nbar\rbaz',tag.comment)
    
    def test_version_22(self):
        tag = Id3v2(self.filepath('id3v2/v22.tag'))
        self.assertEqual('Chanson de Nuit - Op. 15 No. 1',tag.title)
        self.assertEqual('Kennedy / Pettinger',tag.artist)
        self.assertEqual('Salut d\'Amour (Elgar)',tag.album)
        self.assertNotEqual('',tag.comment)
        self.assertNotEqual('5/10',tag.track)
        self.assertEqual('1984',tag.year)
        self.assertEqual('Classical',tag.genre)
    
    def test_v24_no_syncsafe(self):
        #syncsafe is only for v2.4 and up.
        tag = Id3v2(self.filepath('id3v2/v24_no_syncsafe.tag'))
        self.assertEqual('Boccherini / Minuet (String Quartet in E major)',tag.title)
    
    def test_stringtype_one_be_encoded_no_bom(self):
        # Stringtype 1 is supposed to be utf-16 with a BOM. However, some tags have this string type
        # with no BOM. the 'utf-16' encoding defaults to native byte order when it happens.
        # On BE machines, it results in a badly interpreted tag. I've tried hard to fake a BE 
        # machine here, but it didn't work, so this test is kind of worthless unless ran on a BE 
        # machine.
        self.assertEqual(u'foobar', _read_id3_string(u'foobar'.encode('utf-16le'), 1))
    

class TCHeader(TestCase):
    def test_main(self):
        fp = open(self.filepath('id3v2/230-unicode_comment.tag'),'rb')
        h = Header(fp)
        self.assert_(h.valid)
        fp.close()

if __name__ == "__main__":
    unittest.main()
