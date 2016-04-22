# Created By: Virgil Dupras
# Created On: 2005/12/17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from struct import unpack

from .util import FileOrPath
from . import ogg

STREAMINFO = 0
PADDING = 1
APPLICATION = 2
SEEKTABLE = 3
VORBIS_COMMENT = 4
CUESHEET = 5


class InvalidFileError(Exception):
    pass


class MetaDataBlockHeader(object):
    HEADER_SIZE = 4

    def __init__(self, infile):
        self.file = infile
        self.offset = infile.tell()
        data = infile.read(self.HEADER_SIZE)
        unpacked = unpack('!I', data)[0]
        self.last_before_audio = bool(unpacked >> 31)
        self.type = (unpacked >> 24) & 0x7f
        self.size = unpacked & 0xffffff
        self.valid = self.type != 0x7f  # invalid type

    def data(self):
        self.file.seek(self.offset + self.HEADER_SIZE)
        return BLOCK_CLASSES.get(self.type, MetaDataBlock)(self.file, self)

    def __next__(self):
        self.file.seek(self.offset + self.HEADER_SIZE + self.size)
        return MetaDataBlockHeader(self.file)


class MetaDataBlock(object):
    def __init__(self, infile, header):
        self.data = infile.read(header.size)


class StreamInfo(MetaDataBlock):
    def __init__(self, infile, header):
        MetaDataBlock.__init__(self, infile, header)
        block_size, frame_size1, frame_size2, sample1, sample2, md5 = unpack('!2IH2I16s', self.data)
        self.sample_rate = sample1 >> 12
        self.sample_count = sample2 + ((sample1 & 0xf) << 32)


class VorbisComment(MetaDataBlock):
    def __init__(self, infile, header):
        MetaDataBlock.__init__(self, infile, header)
        self.comment = ogg.VorbisComment(self.data)


BLOCK_CLASSES = {
    STREAMINFO: StreamInfo,
    VORBIS_COMMENT: VorbisComment,
}


class FLAC(object):
    '''The class used to hold the metadata for a FLAC file.

    :param infile: The file object or path to process.

    :ivar str ~flac.FLAC.album: The album on which the audio appears.
    :ivar str ~flac.FLAC.artist: The artist associated with the audio.
    :ivar int ~flac.FLAC.audio_offset: The offset, in bytes, at which audio data starts in the file.
    :ivar int ~flac.FLAC.audio_size: The size of the audio part of the file in bytes.
    :ivar int ~flac.FLAC.bitrate: The bitrate of the audio file.
    :ivar str ~flac.FLAC.comment: A comment in the audio file.
    :ivar int ~flac.FLAC.duration: The duration of the audio file (in whole seconds).
    :ivar str ~flac.FLAC.genre: The genre associated with the audio.
    :ivar int ~flac.FLAC.sample_count:
    :ivar int ~flac.FLAC.sample_rate: The sample rate of the audio file.
    :ivar int ~flac.FLAC.size: The size of the file, in bytes.
    :ivar str ~flac.FLAC.title: The title associated with the audio.
    :ivar int ~flac.FLAC.track: The track number associated with the audio.
    :ivar bool ~flac.FLAC.valid: Whether the file could correctly be read or not.
    :ivar str ~flac.FLAC.year: The year in which the audio was recorded.
    '''
    ID = b'fLaC'

    def __init__(self, infile):
        with FileOrPath(infile) as fp:
            fp.seek(0, 2)
            self.size = fp.tell()
            fp.seek(0, 0)
            try:
                self._read(fp)
            except Exception:  # The unpack error doesn't seem to have a class. I have to catch all here
                self._empty()

    def _empty(self):
        self.valid = False
        self.bitrate = 0
        self.artist = ''
        self.album = ''
        self.title = ''
        self.genre = ''
        self.year = ''
        self.comment = ''
        self.track = 0
        self.sample_rate = 0
        self.sample_count = 0
        self.duration = 0
        self.audio_offset = 0
        self.audio_size = 0

    def _read(self, fp):
        id = fp.read(len(self.ID))
        if id != self.ID:
            raise InvalidFileError()
        self.first_header = MetaDataBlockHeader(fp)
        info = self.get_first_block(STREAMINFO)
        self.sample_rate = info.sample_rate
        if self.sample_rate > 0:
            self.duration = info.sample_count // self.sample_rate
        else:
            self.duration = 0
        self.bitrate = 0
        info = self.get_first_block(VORBIS_COMMENT)
        comment = info.comment
        self.artist = comment.artist
        self.album = comment.album
        self.title = comment.title
        self.track = comment.track
        self.year = comment.year
        self.genre = comment.genre
        self.comment = comment.comment

        last = self.get_last_block()
        self.audio_offset = last.offset + last.HEADER_SIZE + last.size
        self.audio_size = self.size - self.audio_offset
        self.valid = True

    def get_first_block(self, type):
        header = self.first_header
        while header.valid:
            if header.type == type:
                return header.data()
            header = next(header)

    def get_last_block(self):
        header = self.first_header
        while header.valid:
            if header.last_before_audio:
                return header
            header = next(header)
