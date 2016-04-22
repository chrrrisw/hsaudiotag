# Created By: Virgil Dupras
# Created On: 2008-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

# http://www.cnpbagwell.com/aiff-c.txt

import logging
import struct
from io import BytesIO

from .id3v2 import Id3v2
from .util import FileOrPath

HEADER_SIZE = 8


class NotAChunk(Exception):
    pass

# based on stdlib's aifc
_HUGE_VAL = 1.79769313486231e+308


def read_float(s):  # 10 bytes
    expon, himant, lomant = struct.unpack('>hLL', s)
    sign = 1
    if expon < 0:
        sign = -1
        expon = expon + 0x8000
    if expon == himant == lomant == 0:
        f = 0.0
    elif expon == 0x7FFF:
        f = _HUGE_VAL
    else:
        expon = expon - 16383
        f = (himant * 0x100000000 + lomant) * pow(2.0, expon - 63)
    return sign * f


class Chunk:
    '''Parent class for File.

    :param file fp: The file object to process.
    :ivar int ~aiff.Chunk.position: The position of the Chunk within the file.
    :raises NotAChunk: If not a Chunk.
    '''
    def __init__(self, fp):
        self._fp = fp
        self.position = fp.tell()
        header = fp.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            raise NotAChunk()
        self.type, self.size = struct.unpack('>4si', header)
        if self.size <= 0:
            raise NotAChunk()
        self.data = None

    def read(self):
        self._fp.seek(self.position + HEADER_SIZE)
        self.data = self._fp.read(self.size)


class File(Chunk):
    '''The class used to hold the metadata for an AIFF file.

    :param str infile: The file to process.

    :ivar int ~aiff.File.audio_offset: The offset, in bytes, at which audio data starts in the file.
    :ivar int ~aiff.File.audio_size: The size of the audio part of the file in bytes.
    :ivar int ~aiff.File.bitrate: The bitrate of the audio file.
    :ivar int ~aiff.File.duration: The duration of the audio file (in whole seconds).
    :ivar int ~aiff.File.sample_rate: The sample rate of the audio file.
    :ivar ~aiff.File.tag: The metadata object.
    :vartype tag: :class:`hsaudiotag.id3v2.Id3v2`
    :ivar bool ~aiff.File.valid: Whether the file could correctly be read or not.
    '''
    def __init__(self, infile):
        self.valid = False
        self.tag = None
        self.duration = self.bitrate = self.sample_rate = self.audio_offset = self.audio_size = 0
        with FileOrPath(infile) as fp:
            try:
                Chunk.__init__(self, fp)
                self.read()
                self.valid = self.duration > 0
            except NotAChunk:
                return

    def read(self):
        '''Read and interpret each Chunk in the File. Called internally on construction.'''
        # the FORM chunk (the main chunk) has 4 bytes for the type, then the subchunks
        self._fp.seek(4, 1)
        while True:
            try:
                chunk = Chunk(self._fp)
            except NotAChunk:
                break
            if chunk.type == b'ID3 ':
                chunk.read()
                self.tag = Id3v2(BytesIO(chunk.data))
            elif chunk.type == b'COMM':
                chunk.read()
                try:
                    channels, frame_count, sample_size, sample_rate = struct.unpack('>hLh10s', chunk.data[:18])
                except struct.error:
                    logging.warning('Could not unpack the COMM field %r' % chunk.data)
                    raise
                self.sample_rate = int(read_float(sample_rate))
                self.bitrate = channels * sample_size * self.sample_rate
                self.duration = frame_count // self.sample_rate
            elif chunk.type == b'SSND':
                self.audio_offset = chunk.position + HEADER_SIZE
                self.audio_size = chunk.size
            self._fp.seek(chunk.position + HEADER_SIZE + chunk.size)
