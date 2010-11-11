# Created By: Virgil Dupras
# Created On: 2005/07/27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest
import io

from . import mp4
from .squeeze import expand_mp4
from .testcase import TestCase

class StubReader(io.BytesIO):
    """This class is to allow myself to remove the .seek .read code from mp4.Atom
    because an Atom will always be a child to another atom. only RootAtom will not.
    """
    def read(self, startat, readcount = -1):
        self.seek(startat)
        return io.BytesIO.read(self, readcount)

class TCMp4Atom(TestCase):
    """Test mp4.Atom class.

    The goal of this testcase is to test mp4.Atom with all kind
    of test atoms not necessarely from m4a files (garbage, hypothetic atoms).
    Call CreateAtom(data) to create an atom that reads from a stub
    created with str.
    """
    def CreateAtom(self, data, atomtype=mp4.Atom):
        return atomtype(StubReader(data), 0)

    def test_empty(self):
        """A 0 byte atom"""
        atom = self.CreateAtom(b'')
        self.assertEqual(atom.valid,False)
        self.assertEqual(atom.size,0)
        self.assertEqual(atom.type,'')
        self.assertEqual(atom.data,())

    def test_minimal(self):
        """A 8 bytes 'aaaa' atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x08aaaa')
        self.assertEqual(atom.valid,True)
        self.assertEqual(atom.size,8)
        self.assertEqual(atom.type,'aaaa')

    def test_wrong_size(self):
        """A 8 bytes 'aaaa' atom with a reported size of 12

        When this hapens, the size attribute is set to the actual
        size of the read data.
        """
        atom = self.CreateAtom(b'\x00\x00\x00\x0caaaa')
        self.assertEqual(atom.valid,True)
        self.assertEqual(atom.size,12)
        self.assertEqual(atom.type,'aaaa')

    def test_alphabet(self):
        """An 'alph' atom with the whole alphabet in it."""
        atom = self.CreateAtom(b'\x00\x00\x00\x22alphabcdefghijklmnopqrstuvwxyz')
        self.assertEqual(atom.valid,True)
        self.assertEqual(atom.size,34)
        self.assertEqual(atom.type,'alph')
        self.assertEqual(atom.read(0,10),b'abcdefghij')
        self.assertEqual(atom.read(0),b'abcdefghijklmnopqrstuvwxyz')

    def test_withinbox(self):
        """Test the attributes of an Atom that is within another atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz', mp4.AtomBox).atoms[3]
        self.assertEqual(atom.valid,True)
        self.assertEqual(atom.size,34)
        self.assertEqual(atom.type,'sub4')
        self.assertEqual(atom.read(0,10),b'abcdefghij')
        self.assertEqual(atom.read(0),b'abcdefghijklmnopqrstuvwxyz')
        self.assertEqual(atom.start_offset,24)
        self.assert_(isinstance(atom.parent,mp4.AtomBox))

    def test_data1(self):
        """Test the data of an atom. str field"""
        atom = self.CreateAtom(b'\x00\x00\x00\x22dataabcdefghijklmnopqrstuvwxyz')
        atom.cls_data_model = '*s'
        self.assertEqual(atom.data[0],b'abcdefghijklmnopqrstuvwxyz')

    def test_data2(self):
        """Test the data of an atom. int field"""
        atom = self.CreateAtom(b'\x00\x00\x00\x0cdata\x01\x02\x03\x04')
        atom.cls_data_model = 'i'
        self.assertEqual(atom.data[0],0x01020304)

    def test_data3(self):
        """Test the data of an atom. 2 short fields + str"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H*s'
        self.assertEqual(atom.data[0],0x0102)
        self.assertEqual(atom.data[1],0x0304)
        self.assertEqual(atom.data[2],b'aybabtu')

    def test_data4(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H7s'
        self.assertEqual(atom.data[0],0x0102)
        self.assertEqual(atom.data[1],0x0304)
        self.assertEqual(atom.data[2],b'aybabtu')

    def test_data5(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor that is not long enough"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H4s'
        self.assertEqual(atom.data[0],0x0102)
        self.assertEqual(atom.data[1],0x0304)
        self.assertEqual(atom.data[2],b'ayba')
        self.assertEqual(len(atom.data),3)

    def test_data6(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor that is too long"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H9s'
        self.assertEqual(atom.data[0],0x0102)
        self.assertEqual(atom.data[1],0x0304)
        self.assertEqual(atom.data[2],b'aybabtu  ')


class TCMp4AtomBox(TestCase):
    """Test mp4.AtomBox class.

    The goal of this testcase is to test mp4.Atom with all kind
    of test atoms not necessarely from m4a files (garbage, hypothetic atoms).
    Call CreateAtom(data) to create an atom that reads from a stub
    created with str.
    """
    def CreateAtom(self, data):
        return mp4.AtomBox(StubReader(data),0)

    def test_empty(self):
        """A 0 byte atom"""
        atom = self.CreateAtom(b'')
        self.assertEqual(atom.atoms,())

    def test_minimal(self):
        """A 8 bytes 'aaaa' atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x08aaaa')
        self.assertEqual(atom.atoms,())

    def test_box1(self):
        """A 'box1' atom with 4 subatoms in it."""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz')
        self.assertEqual(len(atom.atoms),4)

    def test_box2(self):
        """A 'box2' atom with 3 subatoms in it and some data before."""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz')
        atom.cls_data_model = '2H4s'
        self.assertEqual(len(atom.atoms),3)
        self.assertEqual(atom.data[0],0x0000)
        self.assertEqual(atom.data[1],0x0008)
        self.assertEqual(atom.data[2],b'sub1')
        self.assertEqual(atom.atoms[0].type,'sub2')

class TCMp4FileTest1(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test1.m4a')))

    def tearDown(self):
        if hasattr(self,'file'):
            self.file.close()

    def test_root(self):
        atom = self.file
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(3364781  ,atom.size)
        self.assertEqual('root',atom.type)
        self.assertEqual(4,len(atom.atoms))

    def test_atom_1(self):
        atom = self.file.atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x20  ,atom.size)
        self.assertEqual('ftyp',atom.type)

    def test_atom_2(self):
        atom = self.file.atoms[1]
        self.assertEqual(0x20  ,atom.start_offset)
        self.assertEqual(0x9ddc,atom.size)
        self.assertEqual('moov',atom.type)
        self.assertEqual(3,len(atom.atoms))

    def test_atom_2_1(self):
        atom = self.file.atoms[1].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x6c  ,atom.size)
        self.assertEqual('mvhd',atom.type)

    def test_atom_2_2(self):
        atom = self.file.atoms[1].atoms[1]
        self.assertEqual(0x6c  ,atom.start_offset)
        self.assertEqual(0x93d1,atom.size)
        self.assertEqual('trak',atom.type)
        self.assertEqual(2,len(atom.atoms))

    def test_atom_2_2_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x5c  ,atom.size)
        self.assertEqual('tkhd',atom.type)


    def test_atom_2_2_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1]
        self.assertEqual(0x5c  ,atom.start_offset)
        self.assertEqual(0x936d,atom.size)
        self.assertEqual('mdia',atom.type)
        self.assertEqual(3,len(atom.atoms))
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x20,atom.size)
        self.assertEqual('mdhd',atom.type)

    def test_atom_2_2_2_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[1]
        self.assertEqual(0x20  ,atom.start_offset)
        self.assertEqual(0x22  ,atom.size)
        self.assertEqual('hdlr',atom.type)

    def test_atom_2_2_2_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2]
        self.assertEqual(0x42  ,atom.start_offset)
        self.assertEqual(0x9323,atom.size)
        self.assertEqual('minf',atom.type)
        self.assertEqual(3,len(atom.atoms))
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_3_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x10  ,atom.size)
        self.assertEqual('smhd',atom.type)

    def test_atom_2_2_2_3_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[1]
        self.assertEqual(0x10  ,atom.start_offset)
        self.assertEqual(0x24  ,atom.size)
        self.assertEqual('dinf',atom.type)

    def test_atom_2_2_2_3_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2]
        self.assertEqual(0x34  ,atom.start_offset)
        self.assertEqual(0x92e7,atom.size)
        self.assertEqual('stbl',atom.type)
        self.assertEqual(5,len(atom.atoms))
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_3_3_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x67  ,atom.size)
        self.assertEqual('stsd',atom.type)

    def test_atom_2_2_2_3_3_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[1]
        self.assertEqual(0x67  ,atom.start_offset)
        self.assertEqual(0x18  ,atom.size)
        self.assertEqual('stts',atom.type)

    def test_atom_2_2_2_3_3_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[2]
        self.assertEqual(0x7f  ,atom.start_offset)
        self.assertEqual(0x28  ,atom.size)
        self.assertEqual('stsc',atom.type)

    def test_atom_2_2_2_3_3_4(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[3]
        self.assertEqual(0xa7  ,atom.start_offset)
        self.assertEqual(0x8b84,atom.size)
        self.assertEqual('stsz',atom.type)

    def test_atom_2_2_2_3_3_5(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[4]
        self.assertEqual(0x8c2b,atom.start_offset)
        self.assertEqual(0x6b4,atom.size)
        self.assertEqual('stco',atom.type)
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3(self):
        atom = self.file.atoms[1].atoms[2]
        self.assertEqual(0x943d,atom.start_offset)
        self.assertEqual(0x997 ,atom.size)
        self.assertEqual('udta',atom.type)
        self.assertEqual(1,len(atom.atoms))
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0]
        self.assertEqual(0x0   ,atom.start_offset)
        self.assertEqual(0x98f ,atom.size)
        self.assertEqual('meta',atom.type)
        self.assertEqual(3,len(atom.atoms))
        self.assertEqual(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3_1_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[0]
        self.assertEqual(0x4   ,atom.start_offset)
        self.assertEqual(0x22  ,atom.size)
        self.assertEqual('hdlr',atom.type)

    def test_atom_2_3_1_2(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1]
        self.assertEqual(0x26   ,atom.start_offset)
        self.assertEqual(0x203 ,atom.size)
        self.assertEqual('ilst',atom.type)

    def test_atom_2_3_1_2_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[0]
        self.assertEqual('\xa9nam',atom.type)
        self.assertEqual('This Is How It Goes',atom.attr_data)

    def test_atom_2_3_1_2_2(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[1]
        self.assertEqual('\xa9ART',atom.type)
        self.assertEqual('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_3(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[2]
        self.assertEqual('\xa9wrt',atom.type)
        self.assertEqual('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_4(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[3]
        self.assertEqual('\xa9alb',atom.type)
        self.assertEqual('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_5(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[4]
        self.assertEqual('gnre',atom.type)
        self.assertEqual(0x2c,atom.attr_data)

    def test_atom_2_3_1_2_6(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[5]
        self.assertEqual('trkn',atom.type)
        self.assertEqual(0x1,atom.attr_data)

    def test_atom_2_3_1_2_7(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[6]
        self.assertEqual('\xa9day',atom.type)
        self.assertEqual('2003',atom.attr_data)

    def test_atom_2_3_1_2_8(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[7]
        self.assertEqual('cpil',atom.type)

    def test_atom_2_3_1_2_9(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[8]
        self.assertEqual('tmpo',atom.type)

    def test_atom_2_3_1_2_10(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[9]
        self.assertEqual('\xa9too',atom.type)
        self.assertEqual('iTunes v4.7.1.30, QuickTime 6.5.2',atom.attr_data)

    def test_atom_2_3_1_2_11(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[10]
        self.assertEqual('----',atom.type)

    def test_atom_2_3_1_3(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[2]
        self.assertEqual(0x229 ,atom.start_offset)
        self.assertEqual(0x75e ,atom.size)
        self.assertEqual('free',atom.type)

    def test_atom_3(self):
        atom = self.file.atoms[2]
        self.assertEqual(0x9dfc,atom.start_offset)
        self.assertEqual(0x2a24,atom.size)
        self.assertEqual('free',atom.type)

    def test_atom_4(self):
        atom = self.file.atoms[3]
        self.assertEqual(0xc820  ,atom.start_offset)
        self.assertEqual(0x328f8d,atom.size)
        self.assertEqual('mdat'  ,atom.type)
        self.assertEqual(atom.start_offset + atom.size, atom.parent.size)

    def test_find(self):
        self.assertEqual(self.file.atoms[1],self.file.find('moov'));
        self.assertEqual(None,self.file.find('bleh'));
        self.assertEqual(self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[4],self.file.find('moov.udta.meta.ilst.gnre'));

    def test_valid(self):
        self.assertEqual(self.file.valid,True)

    def test_info(self):
        self.assertEqual('This Is How It Goes',self.file.title)
        self.assertEqual('Billy Talent',self.file.artist)
        self.assertEqual('Billy Talent',self.file.album)
        self.assertEqual('Punk',self.file.genre)
        self.assertEqual('',self.file.comment)
        self.assertEqual(3364781,self.file.size)
        self.assertEqual(44100,self.file.sample_rate)
        self.assertEqual(207,self.file.duration)
        self.assertEqual(128,self.file.bitrate)
        self.assertEqual('2003',self.file.year)
        self.assertEqual(1,self.file.track)
        self.file.close() #See if there is something wrong happenning when calling close twice

    def test_cant_open(self):
        #Just make sure that no exception is going through. It is normal that
        #all the fields are blank
        del self.file
        fp = open(self.filepath('mp4/test1.m4a'),'r+b')
        file = mp4.File(self.filepath('mp4/test1.m4a'))

    def test_size(self):
        #mdat offset
        self.assertEqual(0x3357ad,self.file.size)
        self.assertEqual(0xc820,self.file.audio_offset)
        self.assertEqual(0x3357ad - 0xc820,self.file.audio_size)


class TCMp4Filezerofile(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('zerofile'))

    def test_find(self):
        self.assertEqual(None,self.file.find('moov'));
        self.assertEqual(None,self.file.find('bleh'));
        self.assertEqual(None,self.file.find('moov.udta.meta.ilst.gnre'));

    def test_valid(self):
        self.assertEqual(self.file.valid,False)

    def test_info(self):
        self.assertEqual('',self.file.title);
        self.assertEqual('',self.file.artist);
        self.assertEqual('',self.file.album);
        self.assertEqual('',self.file.genre);
        self.assertEqual('',self.file.comment);
        self.assertEqual(0,self.file.sample_rate);
        self.assertEqual(0,self.file.duration);
        self.assertEqual(0,self.file.bitrate);

    def test_atoms(self):
        self.assertEqual(0,len(self.file.atoms));

class TCMp4Filerandomfile(TCMp4Filezerofile):
    def setUp(self):
        self.file = mp4.File(self.filepath('randomfile'))

class TCMp4Filezerofill(TCMp4Filezerofile):
    def setUp(self):
        self.file = mp4.File(self.filepath('zerofill'))

class TCMp4Fileinvalid1(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('mp4/invalid1.m4a'))

    def test_find(self):
        self.assertEqual(self.file.atoms[0],self.file.find('mvhd'));

    def test_valid(self):
        self.assertEqual(self.file.valid,False)
        
    def test_track_is_int(self):
        self.assertEqual(0,self.file.track)

class TCMp4Filetest2(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('mp4/test2.m4a'))

    def test_info(self):
        self.assertEqual('Intro to Where It\'s At',self.file.title)
        self.assertEqual('Beck',self.file.artist)
        self.assertEqual('Odelay',self.file.album)
        self.assertEqual('Alternative',self.file.genre)
        self.assertEqual('This is a test',self.file.comment)
        self.assertEqual(754518,self.file.size)
        self.assertEqual(44100,self.file.sample_rate)
        self.assertEqual(11,self.file.duration)
        self.assertEqual(128,self.file.bitrate)

class TCMp4Filetest3(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test3.m4a')))

    def test_info(self):
        self.assert_(isinstance(self.file.title,str))
        self.assert_(isinstance(self.file.artist,str))
        self.assert_(isinstance(self.file.title,str))
        self.assertEqual('J\'ai oubli\u00e9',self.file.title)
        self.assert_(isinstance(self.file.artist,str))
        self.assertEqual('Capitaine R\u00e9volte',self.file.artist)
        self.assertEqual('Danse sociale',self.file.album)
        self.assertEqual('Punk',self.file.genre)
        self.assertEqual('',self.file.comment)
        self.assertEqual(3813888,self.file.size)
        self.assertEqual(44100,self.file.sample_rate)
        self.assertEqual(235,self.file.duration)
        self.assertEqual(128,self.file.bitrate)

class TCMp4Filetest4(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test4.m4a')))

    def test_info(self):
        self.assertEqual('2005',self.file.year)

class TCMp4Filetest5(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test5.m4a')))

    def test_info(self):
        self.assertEqual('Hip Hop/Rap',self.file.genre)
        self.assertEqual(128,self.file.bitrate)

class TCMp4Filetest6(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test6.m4p')))

    def test_info(self):
        """The type of this file in stsd is drms, which isn't present in th emp4 layout doc.
        the drms type also has 44 bytes before sub boxes.
        """
        self.assertEqual(128,self.file.bitrate)
        self.assertEqual(0x7b00b,self.file.audio_offset)
        self.assertEqual(0x279d23,self.file.audio_size)

class TCMp4Filetest7(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test7.m4a')))

    def test_info(self):
        """This file is a lossless aac file.
        """
        self.assertEqual('Coolio',self.file.artist)
        self.assertEqual('That\'s How It Is',self.file.title)
        self.assertEqual('Gangsta\'s Paradise',self.file.album)
        self.assertEqual('Hip Hop/Rap',self.file.genre)
        self.assertEqual(0,self.file.bitrate)
        self.assertEqual(60,self.file.duration)

class TCMp4File_non_ascii_genre(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('mp4/non_ascii_genre.m4a'))

    def test_genre(self):
        self.assertEqual('\xe9', self.file.genre)
    

class TCMp4File_genre_index_out_of_range(TestCase):
    # Don't crash when a file has a numerical genre that is out of range
    def setUp(self):
        self.file = mp4.File(self.filepath('mp4/genre_index_out_of_range.m4a'))
    
    def test_genre(self):
        self.assertEqual('', self.file.genre)
    

if __name__ == "__main__":
    unittest.main()