================
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

valid
    Whether the file could correctly be read or not.

artist - album - title - genre - year - comment
    Tags present in the audio file. All strings, return an empty string if not present.

track
    The track tag in the audio file. Integer (zero if not present)

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

The ``mpeg.Mpeg`` and ``aiff.File`` classes are special cases where tags are contained in the ``tag`` attribute.

Available classes
=================

* :class:`hsaudiotag.mpeg.Mpeg` for mp3 files.
* :class:`hsaudiotag.mp4.File` for mp4 files.
* :class:`hsaudiotag.wma.WMADecoder` for wma files.
* :class:`hsaudiotag.ogg.Vorbis` for ogg files.
* :class:`hsaudiotag.flac.FLAC` for flac files.
* :class:`hsaudiotag.aiff.File` for aiff files.

auto.File
=========

Since v1.1, there's a new wrapper class, :class:`hsaudiotag.auto.File` which automatically detects the type of the
file and provides a unified interface to its attributes (something the different classes of
``hsaudiotag`` don't have). To use it, instantiate it like you would with any other class, that is
``auto.File(filename_or_file_object)``. All the attributes are in the wrapper, but if you want to
access the "original" class, use the ``original`` attribute. Example::

    >>> from hsaudiotag import auto
    >>> myfile = auto.File('foo.m4a')
    >>> myfile.artist
    'Built To Spill'
    >>> myfile.album
    'There Is No Enemy'
    >>> myfile.duration
    218
    >>>> myfile.original
    <mp4.File object>
