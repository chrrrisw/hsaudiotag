# Created By: Virgil Dupras
# Created On: 2010-12-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

from . import mpeg, mp4, wma, ogg, flac, aiff

ALL_CLASSES = [mp4.File, mpeg.Mpeg, wma.WMADecoder, ogg.Vorbis, flac.FLAC, aiff.File]

EXT2CLASS = {
    'mp3': mpeg.Mpeg,
    'wma': wma.WMADecoder,
    'm4a': mp4.File,
    'm4p': mp4.File,
    'ogg': ogg.Vorbis,
    'flac': flac.FLAC,
    'aif': aiff.File,
    'aiff': aiff.File,
    'aifc': aiff.File,
}

AUDIO_ATTRS = {'size', 'duration', 'bitrate', 'sample_rate', 'audio_offset', 'audio_size'}
TAG_ATTRS = {'artist', 'album', 'title', 'genre', 'year', 'track', 'comment'}


class File:
    """
    Automatically determine a file type and decode it accordingly,
    providing a unified interface to all file types.

    :param str infile: The file to process.
    :ivar str ~auto.File.album: The name of the album.
    :ivar str ~auto.File.artist: The name(s) of the artist(s).
    :ivar str ~auto.File.comment: The comment in the audio file.
    :ivar str ~auto.File.genre: The genre of the audio file.
    :ivar ~auto.File.original: The instance of the specific audio file class.
    :ivar str ~auto.File.title: The title of the audio file.
    :ivar int ~auto.File.track: The track number associated with the audio file.
    :ivar bool ~auto.File.valid: Whether the file is a valid audio file.
    :ivar str ~auto.File.year: The year the audio file was recorded.
    """

    def __init__(self, infile):
        self._set_invalid_attrs()
        f = self._guess_class(infile)
        if f is not None:
            self._set_attrs(f)
        if hasattr(f, 'close'):
            f.close()

    @staticmethod
    def _guess_class(infile):
        """Return an instance of the appropriate audio file class, or None."""
        if isinstance(infile, str):
            # Try a fast path to the right class instead of trying all classes sequentially.
            ext = op.splitext(infile)[1][1:]
            if ext in EXT2CLASS:
                f = EXT2CLASS[ext](infile)
                if f.valid:
                    return f
        for class_ in ALL_CLASSES:
            # Now try all classes sequentially.
            f = class_(infile)
            if f.valid:
                return f
        else:
            # Return nothing, we've failed.
            return None

    def _set_attrs(self, f):
        """Set the auto class attributes from the original file."""
        self.valid = True
        self.original = f
        for attrname in AUDIO_ATTRS:
            setattr(self, attrname, getattr(f, attrname))
        tag = f.tag if hasattr(f, 'tag') else f
        if tag is not None:
            for attrname in TAG_ATTRS:
                setattr(self, attrname, getattr(tag, attrname))

    def _set_invalid_attrs(self):
        """Set the auto class attributes to their defaults."""
        self.valid = False
        self.original = None
        for attrname in AUDIO_ATTRS:
            setattr(self, attrname, 0)
        for attrname in TAG_ATTRS:
            default = '' if attrname != 'track' else 0
            setattr(self, attrname, default)
