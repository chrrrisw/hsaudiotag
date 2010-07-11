Using hsaudiotag
================

To read a file's metadata with ``hsaudiotag``, pick a class corresponding to the file you want to read, create an instance of it with the a file object or a filename as an argument, and fetch the attributes from it. For example, if you want to fetch attributes from a mp4 file, you'd do::

    >>> from hsaudiotag import mp4
    >>> myfile = mp4.File('foo.m4a')
    >>> myfile.artist
    'Built To Spill'
    >>> myfile.album
    'There Is No Enemy'
    >>> myfile.duration
    218

Available attributes
====================

artist - album - title - genre - year - track - comment
    Tags present in the audio file. All strings, return an empty string is not present.

duration
    Duration of the audio file, in seconds (always as integer).

bitrate
    The bitrate of the audio file.

sample_rate
    The sample rate of the audio file.

size
    The size of the file, in bytes.

audio_size
    The size of the audio part of the file, that is, with metadata removed. In bytes.

audio_offset
    The offset, in bytes, at which audio data starts in the file.

The ``Mpeg`` class is a special case where tags are contained in the ``tag`` attribute.

Available classes
=================

* ``mpeg.Mpeg`` for mp3 files.
* ``mp4.File`` for mp4 files.
* ``wma.WMADecoder`` for wma files.
* ``ogg.Vorbis`` for ogg files.
* ``flac.FLAC`` for flac files.
* ``aiff.File`` for aiff files.