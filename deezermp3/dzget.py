import argparse
import os
import re

import requests
from youtube_dl import YoutubeDL


API_URL = "https://api.deezer.com/playlist/"


class DeezerMP3(object):
    def __init__(self, dirout=None, quality=5, format="best"):
        self.dirout = os.path.realpath(dirout or os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.quality = quality
        self.format = format

    def log(self, data):
        print(data)

    def download_playlist(self, url):
        plid = url.strip().split('/')[-1]
        url = API_URL + plid

        res = requests.get(url)
        data = res.json()

        pl_name = data['title']
        dir_path = os.path.join(self.dirout, pl_name)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        regexp_video = re.compile(r'(/watch\?[^\"]+)', re.I | re.M | re.U)

        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': self.format,
            'preferredquality': self.quality,
            'nopostoverwrites': False,
        }]

        options = {
            'postprocessors': postprocessors,
            'outtmpl': '%s/%%(title)s.%%(ext)s' % dir_path,
            'format': 'bestaudio/best',
        }

        with YoutubeDL(options) as ydl:
            for item in data['tracks']['data']:
                name = '%s - %s' % (item['artist']['name'], item['title'])

                self.log("\n## Parsing: %s" % name)
                yres = requests.get('https://m.youtube.com/results?search_query=%s' % name)
                data = yres.content.decode('utf-8')
                videos = regexp_video.findall(data)
                if not videos:
                    self.log(' > Not found')
                    continue
                self.log(' > Url: %s' % videos[0])
                ydl.download(["http://www.youtube.com%s" % videos[0]])


def get_args():
    parser = argparse.ArgumentParser(description="DeezerMP3 downloader")
    parser.add_argument('-p',
                        '--playlist',
                        action='store_true',
                        help='Download by playlist url.')

    parser.add_argument('-f',
                        '--audio-format',
                        metavar='format',
                        default='best',
                        type=str,
                        help='Specify audio format: "best", "aac", "flac", "mp3", '
                             '"m4a", "opus", "vorbis", or "wav" (default "best")')

    parser.add_argument('-d',
                        '--dir',
                        metavar='directory',
                        default='./',
                        type=str,
                        help='Output directory')

    parser.add_argument('-q',
                        '--audio-quality',
                        metavar='quality',
                        default='5',
                        type=str,
                        help='Specify ffmpeg/avconv audio quality, insert a value '
                             'between 0 (better) and 9 (worse) for VBR or a specific '
                             'bitrate like 128K (default 5)')

    parser.add_argument('url', metavar='url', type=str,
                        help='Playlist urls or ids')

    args = parser.parse_args()

    if args.audio_format:
        formats = ['best', 'aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav']
        if args.audio_format not in formats:
            formatted = '\n'.join(map(lambda x: ' - ' + x, formats))
            parser.error('Invalid audio format specified. Should be one from list:\n%s' % formatted)
    if args.audio_quality:
        args.quality = args.audio_quality.strip('k').strip('K')
        if not args.audio_quality.isdigit():
            parser.error('Invalid audio quality specified.')
    return args


def main():
    args = get_args()

    dmp3 = DeezerMP3(
        dirout=args.dir,
        quality=args.audio_quality,
        format=args.audio_format)

    dmp3.download_playlist(args.url)


if __name__ == "__main__":
    main()
