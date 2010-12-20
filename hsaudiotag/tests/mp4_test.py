# Created By: Virgil Dupras
# Created On: 2005/07/27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import io

from .. import mp4
from .squeeze import expand_mp4
from .testcase import TestCase, TestData, eq_

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
        eq_(atom.valid,False)
        eq_(atom.size,0)
        eq_(atom.type,'')
        eq_(atom.data,())

    def test_minimal(self):
        """A 8 bytes 'aaaa' atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x08aaaa')
        eq_(atom.valid,True)
        eq_(atom.size,8)
        eq_(atom.type,'aaaa')

    def test_wrong_size(self):
        """A 8 bytes 'aaaa' atom with a reported size of 12

        When this hapens, the size attribute is set to the actual
        size of the read data.
        """
        atom = self.CreateAtom(b'\x00\x00\x00\x0caaaa')
        eq_(atom.valid,True)
        eq_(atom.size,12)
        eq_(atom.type,'aaaa')

    def test_alphabet(self):
        """An 'alph' atom with the whole alphabet in it."""
        atom = self.CreateAtom(b'\x00\x00\x00\x22alphabcdefghijklmnopqrstuvwxyz')
        eq_(atom.valid,True)
        eq_(atom.size,34)
        eq_(atom.type,'alph')
        eq_(atom.read(0,10),b'abcdefghij')
        eq_(atom.read(0),b'abcdefghijklmnopqrstuvwxyz')

    def test_withinbox(self):
        """Test the attributes of an Atom that is within another atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz', mp4.AtomBox).atoms[3]
        eq_(atom.valid,True)
        eq_(atom.size,34)
        eq_(atom.type,'sub4')
        eq_(atom.read(0,10),b'abcdefghij')
        eq_(atom.read(0),b'abcdefghijklmnopqrstuvwxyz')
        eq_(atom.start_offset,24)
        assert isinstance(atom.parent,mp4.AtomBox)

    def test_data1(self):
        """Test the data of an atom. str field"""
        atom = self.CreateAtom(b'\x00\x00\x00\x22dataabcdefghijklmnopqrstuvwxyz')
        atom.cls_data_model = '*s'
        eq_(atom.data[0],b'abcdefghijklmnopqrstuvwxyz')

    def test_data2(self):
        """Test the data of an atom. int field"""
        atom = self.CreateAtom(b'\x00\x00\x00\x0cdata\x01\x02\x03\x04')
        atom.cls_data_model = 'i'
        eq_(atom.data[0],0x01020304)

    def test_data3(self):
        """Test the data of an atom. 2 short fields + str"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H*s'
        eq_(atom.data[0],0x0102)
        eq_(atom.data[1],0x0304)
        eq_(atom.data[2],b'aybabtu')

    def test_data4(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H7s'
        eq_(atom.data[0],0x0102)
        eq_(atom.data[1],0x0304)
        eq_(atom.data[2],b'aybabtu')

    def test_data5(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor that is not long enough"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H4s'
        eq_(atom.data[0],0x0102)
        eq_(atom.data[1],0x0304)
        eq_(atom.data[2],b'ayba')
        eq_(len(atom.data),3)

    def test_data6(self):
        """Test the data of an atom. a str field at the end, but with a len descriptor that is too long"""
        atom = self.CreateAtom(b'\x00\x00\x00\x13data\x01\x02\x03\x04aybabtu')
        atom.cls_data_model = '2H9s'
        eq_(atom.data[0],0x0102)
        eq_(atom.data[1],0x0304)
        eq_(atom.data[2],b'aybabtu  ')


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
        eq_(atom.atoms,())

    def test_minimal(self):
        """A 8 bytes 'aaaa' atom"""
        atom = self.CreateAtom(b'\x00\x00\x00\x08aaaa')
        eq_(atom.atoms,())

    def test_box1(self):
        """A 'box1' atom with 4 subatoms in it."""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz')
        eq_(len(atom.atoms),4)

    def test_box2(self):
        """A 'box2' atom with 3 subatoms in it and some data before."""
        atom = self.CreateAtom(b'\x00\x00\x00\x42box1\x00\x00\x00\x08sub1\x00\x00\x00\x08sub2\x00\x00\x00\x08sub3\x00\x00\x00\x22sub4abcdefghijklmnopqrstuvwxyz')
        atom.cls_data_model = '2H4s'
        eq_(len(atom.atoms),3)
        eq_(atom.data[0],0x0000)
        eq_(atom.data[1],0x0008)
        eq_(atom.data[2],b'sub1')
        eq_(atom.atoms[0].type,'sub2')

class TCMp4FileTest1(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test1.m4a')))

    def tearDown(self):
        if hasattr(self,'file'):
            self.file.close()

    def test_root(self):
        atom = self.file
        eq_(0x0   ,atom.start_offset)
        eq_(3364781  ,atom.size)
        eq_('root',atom.type)
        eq_(4,len(atom.atoms))

    def test_atom_1(self):
        atom = self.file.atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x20  ,atom.size)
        eq_('ftyp',atom.type)

    def test_atom_2(self):
        atom = self.file.atoms[1]
        eq_(0x20  ,atom.start_offset)
        eq_(0x9ddc,atom.size)
        eq_('moov',atom.type)
        eq_(3,len(atom.atoms))

    def test_atom_2_1(self):
        atom = self.file.atoms[1].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x6c  ,atom.size)
        eq_('mvhd',atom.type)

    def test_atom_2_2(self):
        atom = self.file.atoms[1].atoms[1]
        eq_(0x6c  ,atom.start_offset)
        eq_(0x93d1,atom.size)
        eq_('trak',atom.type)
        eq_(2,len(atom.atoms))

    def test_atom_2_2_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x5c  ,atom.size)
        eq_('tkhd',atom.type)


    def test_atom_2_2_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1]
        eq_(0x5c  ,atom.start_offset)
        eq_(0x936d,atom.size)
        eq_('mdia',atom.type)
        eq_(3,len(atom.atoms))
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x20,atom.size)
        eq_('mdhd',atom.type)

    def test_atom_2_2_2_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[1]
        eq_(0x20  ,atom.start_offset)
        eq_(0x22  ,atom.size)
        eq_('hdlr',atom.type)

    def test_atom_2_2_2_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2]
        eq_(0x42  ,atom.start_offset)
        eq_(0x9323,atom.size)
        eq_('minf',atom.type)
        eq_(3,len(atom.atoms))
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_3_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x10  ,atom.size)
        eq_('smhd',atom.type)

    def test_atom_2_2_2_3_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[1]
        eq_(0x10  ,atom.start_offset)
        eq_(0x24  ,atom.size)
        eq_('dinf',atom.type)

    def test_atom_2_2_2_3_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2]
        eq_(0x34  ,atom.start_offset)
        eq_(0x92e7,atom.size)
        eq_('stbl',atom.type)
        eq_(5,len(atom.atoms))
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_2_2_3_3_1(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x67  ,atom.size)
        eq_('stsd',atom.type)

    def test_atom_2_2_2_3_3_2(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[1]
        eq_(0x67  ,atom.start_offset)
        eq_(0x18  ,atom.size)
        eq_('stts',atom.type)

    def test_atom_2_2_2_3_3_3(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[2]
        eq_(0x7f  ,atom.start_offset)
        eq_(0x28  ,atom.size)
        eq_('stsc',atom.type)

    def test_atom_2_2_2_3_3_4(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[3]
        eq_(0xa7  ,atom.start_offset)
        eq_(0x8b84,atom.size)
        eq_('stsz',atom.type)

    def test_atom_2_2_2_3_3_5(self):
        atom = self.file.atoms[1].atoms[1].atoms[1].atoms[2].atoms[2].atoms[4]
        eq_(0x8c2b,atom.start_offset)
        eq_(0x6b4,atom.size)
        eq_('stco',atom.type)
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3(self):
        atom = self.file.atoms[1].atoms[2]
        eq_(0x943d,atom.start_offset)
        eq_(0x997 ,atom.size)
        eq_('udta',atom.type)
        eq_(1,len(atom.atoms))
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0]
        eq_(0x0   ,atom.start_offset)
        eq_(0x98f ,atom.size)
        eq_('meta',atom.type)
        eq_(3,len(atom.atoms))
        eq_(atom.start_offset + atom.size + mp4.HEADER_SIZE, atom.parent.size)

    def test_atom_2_3_1_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[0]
        eq_(0x4   ,atom.start_offset)
        eq_(0x22  ,atom.size)
        eq_('hdlr',atom.type)

    def test_atom_2_3_1_2(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1]
        eq_(0x26   ,atom.start_offset)
        eq_(0x203 ,atom.size)
        eq_('ilst',atom.type)

    def test_atom_2_3_1_2_1(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[0]
        eq_('\xa9nam',atom.type)
        eq_('This Is How It Goes',atom.attr_data)

    def test_atom_2_3_1_2_2(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[1]
        eq_('\xa9ART',atom.type)
        eq_('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_3(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[2]
        eq_('\xa9wrt',atom.type)
        eq_('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_4(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[3]
        eq_('\xa9alb',atom.type)
        eq_('Billy Talent',atom.attr_data)

    def test_atom_2_3_1_2_5(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[4]
        eq_('gnre',atom.type)
        eq_(0x2c,atom.attr_data)

    def test_atom_2_3_1_2_6(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[5]
        eq_('trkn',atom.type)
        eq_(0x1,atom.attr_data)

    def test_atom_2_3_1_2_7(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[6]
        eq_('\xa9day',atom.type)
        eq_('2003',atom.attr_data)

    def test_atom_2_3_1_2_8(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[7]
        eq_('cpil',atom.type)

    def test_atom_2_3_1_2_9(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[8]
        eq_('tmpo',atom.type)

    def test_atom_2_3_1_2_10(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[9]
        eq_('\xa9too',atom.type)
        eq_('iTunes v4.7.1.30, QuickTime 6.5.2',atom.attr_data)

    def test_atom_2_3_1_2_11(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[10]
        eq_('----',atom.type)

    def test_atom_2_3_1_3(self):
        atom = self.file.atoms[1].atoms[2].atoms[0].atoms[2]
        eq_(0x229 ,atom.start_offset)
        eq_(0x75e ,atom.size)
        eq_('free',atom.type)

    def test_atom_3(self):
        atom = self.file.atoms[2]
        eq_(0x9dfc,atom.start_offset)
        eq_(0x2a24,atom.size)
        eq_('free',atom.type)

    def test_atom_4(self):
        atom = self.file.atoms[3]
        eq_(0xc820  ,atom.start_offset)
        eq_(0x328f8d,atom.size)
        eq_('mdat'  ,atom.type)
        eq_(atom.start_offset + atom.size, atom.parent.size)

    def test_find(self):
        eq_(self.file.atoms[1],self.file.find('moov'));
        eq_(None,self.file.find('bleh'));
        eq_(self.file.atoms[1].atoms[2].atoms[0].atoms[1].atoms[4],self.file.find('moov.udta.meta.ilst.gnre'));

    def test_valid(self):
        eq_(self.file.valid,True)

    def test_info(self):
        eq_('This Is How It Goes',self.file.title)
        eq_('Billy Talent',self.file.artist)
        eq_('Billy Talent',self.file.album)
        eq_('Punk',self.file.genre)
        eq_('',self.file.comment)
        eq_(3364781,self.file.size)
        eq_(44100,self.file.sample_rate)
        eq_(207,self.file.duration)
        eq_(128,self.file.bitrate)
        eq_('2003',self.file.year)
        eq_(1,self.file.track)
        self.file.close() #See if there is something wrong happenning when calling close twice

    def test_cant_open(self):
        #Just make sure that no exception is going through. It is normal that
        #all the fields are blank
        del self.file
        fp = open(self.filepath('mp4/test1.m4a'),'r+b')
        file = mp4.File(self.filepath('mp4/test1.m4a'))

    def test_size(self):
        #mdat offset
        eq_(0x3357ad,self.file.size)
        eq_(0xc820,self.file.audio_offset)
        eq_(0x3357ad - 0xc820,self.file.audio_size)


class TCMp4Filezerofile(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('zerofile'))

    def test_find(self):
        eq_(None,self.file.find('moov'));
        eq_(None,self.file.find('bleh'));
        eq_(None,self.file.find('moov.udta.meta.ilst.gnre'));

    def test_valid(self):
        eq_(self.file.valid,False)

    def test_info(self):
        eq_('',self.file.title);
        eq_('',self.file.artist);
        eq_('',self.file.album);
        eq_('',self.file.genre);
        eq_('',self.file.comment);
        eq_(0,self.file.sample_rate);
        eq_(0,self.file.duration);
        eq_(0,self.file.bitrate);

    def test_atoms(self):
        eq_(0,len(self.file.atoms));

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
        eq_(self.file.atoms[0],self.file.find('mvhd'));

    def test_valid(self):
        eq_(self.file.valid,False)
        
    def test_track_is_int(self):
        eq_(0,self.file.track)

class TCMp4Filetest2(TestCase):
    def setUp(self):
        self.file = mp4.File(self.filepath('mp4/test2.m4a'))

    def test_info(self):
        eq_('Intro to Where It\'s At',self.file.title)
        eq_('Beck',self.file.artist)
        eq_('Odelay',self.file.album)
        eq_('Alternative',self.file.genre)
        eq_('This is a test',self.file.comment)
        eq_(754518,self.file.size)
        eq_(44100,self.file.sample_rate)
        eq_(11,self.file.duration)
        eq_(128,self.file.bitrate)

class TCMp4Filetest3(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test3.m4a')))

    def test_info(self):
        assert isinstance(self.file.title,str)
        assert isinstance(self.file.artist,str)
        assert isinstance(self.file.title,str)
        eq_('J\'ai oubli\u00e9',self.file.title)
        assert isinstance(self.file.artist,str)
        eq_('Capitaine R\u00e9volte',self.file.artist)
        eq_('Danse sociale',self.file.album)
        eq_('Punk',self.file.genre)
        eq_('',self.file.comment)
        eq_(3813888,self.file.size)
        eq_(44100,self.file.sample_rate)
        eq_(235,self.file.duration)
        eq_(128,self.file.bitrate)

class TCMp4Filetest4(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test4.m4a')))

    def test_info(self):
        eq_('2005',self.file.year)

class TCMp4Filetest5(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test5.m4a')))

    def test_info(self):
        eq_('Hip Hop/Rap',self.file.genre)
        eq_(128,self.file.bitrate)

class TCMp4Filetest6(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test6.m4p')))

    def test_info(self):
        """The type of this file in stsd is drms, which isn't present in th emp4 layout doc.
        the drms type also has 44 bytes before sub boxes.
        """
        eq_(128,self.file.bitrate)
        eq_(0x7b00b,self.file.audio_offset)
        eq_(0x279d23,self.file.audio_size)

class TCMp4Filetest7(TestCase):
    def setUp(self):
        self.file = mp4.File(expand_mp4(self.filepath('mp4/test7.m4a')))

    def test_info(self):
        """This file is a lossless aac file.
        """
        eq_('Coolio',self.file.artist)
        eq_('That\'s How It Is',self.file.title)
        eq_('Gangsta\'s Paradise',self.file.album)
        eq_('Hip Hop/Rap',self.file.genre)
        eq_(0,self.file.bitrate)
        eq_(60,self.file.duration)

def test_non_ascii_genre():
    fp = mp4.File(TestData.filepath('mp4/non_ascii_genre.m4a'))
    eq_(fp.genre, '\xe9')

def test_genre_index_out_of_range():
    # Don't crash when a file has a numerical genre that is out of range
    fp = mp4.File(TestData.filepath('mp4/genre_index_out_of_range.m4a'))
    eq_(fp.genre, '') # don't crash

def test_empty_attribute_atom():
    # Don't crash when an AttributeAtom has no data (rare, but can happen).
    # empty_attribute_atom.m4a has its title atom with no sub node.
    fp = mp4.File(TestData.filepath('mp4/empty_attribute_atom.m4a'))
    eq_(fp.title, '') # don't crash
