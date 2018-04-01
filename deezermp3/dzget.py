import argparse
import os
import re

import requests
from youtube_dl import YoutubeDL


API_URL = "https://api.deezer.com"


class DeezerMP3(object):
    def __init__(self, dirout=None, quality=5, format="best"):
        self.dirout = os.path.realpath(dirout or os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.quality = quality
        self.format = format
        self.regexp_video = re.compile(r'(/watch\?[^\"]+)', re.I | re.M | re.U)

    def log(self, data):
        print(data)

    def urls_gen(self, data):
        self.log('## Fetching video urls...')
        for item in data['tracks']['data']:
            name = '%s - %s' % (item['artist']['name'], item['title'])
            self.log("## Searching for %s" % name)
            yres = requests.get('https://m.youtube.com/results?search_query=%s' % name)
            search_res = yres.content.decode('utf-8')
            videos = self.regexp_video.findall(search_res)
            if not videos:
                self.log(' > Not found')
                continue
            url = "http://www.youtube.com%s" % videos[0]
            self.log(' > Url: %s' % url)
            yield url

    def download_playlist(self, url):
        parts = url.strip().split('/')
        list_type, playlist_id = parts[-2:]

        url = os.path.join(API_URL, list_type, playlist_id)

        res = requests.get(url)
        data = res.json()
        pl_name = data['title']
        dir_path = os.path.join(self.dirout, pl_name)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

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
            ydl.download(list(self.urls_gen(data)))


def get_args():
    parser = argparse.ArgumentParser(description="DeezerMP3 downloader")

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

    parser.add_argument('urls', metavar='urls', type=str, nargs='+',
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

    for url in args.urls:
        dmp3.download_playlist(url)


if __name__ == "__main__":
    main()
