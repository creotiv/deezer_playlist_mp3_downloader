Deezer MP3 downloader
=====================


Requirements
------------
- ffmpeg


Instalation
-----------

.. code-block::

  pip install git+https://github.com/creotiv/deezer_playlist_mp3_downloader


Use
---
.. code-block::

  dzget -f aac -q 7 http://www.deezer.com/playlist/1447624935
  dzget https://www.deezer.com/us/album/6147987
  # assumed to be playlist if only id specified
  dzget 1447624935
  # also valid:
  dzget album/6147987 playlist/1447624935


Usage
-----
.. code-block::

  usage: dzget.py [-h] [-f format] [-d directory] [-q quality] urls [urls ...]

  DeezerMP3 downloader

  positional arguments:
    urls                  Playlist urls or ids

  optional arguments:
    -h, --help            show this help message and exit
    -f format, --audio-format format
                          Specify audio format: "best", "aac", "flac", "mp3",
                          "m4a", "opus", "vorbis", or "wav" (default "mp3")
    -d directory, --dir directory
                          Output directory
    -q quality, --audio-quality quality
                          Specify ffmpeg/avconv audio quality, insert a value
                          between 0 (better) and 9 (worse) for VBR or a specific
                          bitrate like 128K (default 5)
