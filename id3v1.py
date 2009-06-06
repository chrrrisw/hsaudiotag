#!/usr/bin/env python
# Unit Name: hs.media.id3v1
# Created By: Virgil Dupras
# Created On: 2004/12/07
# Last modified by:$Author: virgil $
# Last modified on:$Date: 2009-05-28 16:37:45 +0200 (Thu, 28 May 2009) $
#                  $Revision: 4394 $
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import struct

from hsutil.files import FileOrPath
from .genres import MUSIC_GENRES

TAG_VERSION_1_0 = 1
TAG_VERSION_1_1 = 2

#id3v1 specs
#0-2:"TAG"
#3-32:Title
#33-62:Artist
#63-92:Album
#93-96:Year
#97-126:Comment
#127:Genre

def _arrange_id3_field(raw_field):
    """Format the read field properly
    
    This function takes only the part of the string before the first \0 char.
    After this, it checks if the string has to be converted to unicode and convert it if it indeed does.
    """
    result = raw_field.split('\0')
    if len(result) > 0:
        result = result[0].rstrip().replace('\n', ' ').replace('\r', ' ')
    else:
        result = ''
    result = unicode(result, 'iso8859-1')
    return result

class Id3v1(object):
    def __init__(self, infile):
        self.version = 0
        self.size = 0
        self.title = ''
        self.artist = ''
        self.album = ''
        self.year = ''
        self.genre = ''
        self.comment = ''
        self.track = 0
        with FileOrPath(infile) as fp:
            self._read_file(fp)
    
    def _read_file(self, fp):
        fp.seek(0, 2)
        position = fp.tell()
        if position and position >= 128:
            fp.seek(-128, 2)
            self._read_tag(fp.read(128))
    
    def _read_tag(self, data):
        if data[0:3] != 'TAG':
            return
        #check if the comment field contains track info
        if ((data[125] == '\0') and (data[126] != '\0')) or ((data[125] == '\x20') and (data[126] != '\x20')):
            #We have a v1.1
            self.version = TAG_VERSION_1_1
            self.track = min(ord(data[126]), 99)
            self.comment = _arrange_id3_field(data[97:125])
        else:
            self.version = TAG_VERSION_1_0
            self.track = 0
            self.comment = _arrange_id3_field(data[97:127])
        self.title = _arrange_id3_field(data[3:33])
        self.artist = _arrange_id3_field(data[33:63])
        self.album = _arrange_id3_field(data[63:93])
        self.year = _arrange_id3_field(data[93:97])
        genre = ord(data[127])
        self.genre = MUSIC_GENRES[genre] if genre < len(MUSIC_GENRES) else ''
        self.size = 128
    
    @property
    def exists(self):
        return self.size > 0
    
