import requests
import re
import os
import sys
import subprocess

API_URL = "https://api.deezer.com/playlist/" 

def log(data):
    print(data)

def download_playlist(url):

    cur_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    
    plid = url.strip().split('/')[-1]
    url = API_URL + plid
    
    res = requests.get(url)
    data = res.json()
    
    pl_name = data['title']
    dir_path = os.path.join(cur_dir, pl_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    regexp_video = re.compile(r'(\/watch\?[^\"]+)', re.I | re.M | re.U)
    
    for item in data['tracks']['data']:
        name = '%s - %s' % (item['artist']['name'], item['title'])
                
        log("\n## Parsing: %s" % name)
        yres = requests.get('https://m.youtube.com/results?search_query=%s' % name)
        data = yres.content
        videos = regexp_video.findall(data)
        if not videos:
            log(' > Not found')
            continue
        log(' > Url: %s' % videos[0])
        log(" > Running: youtube-dl -x --audio-format mp3 -o '%s/%%(title)s.%%(ext)s' http://www.youtube.com%s" % (dir_path,videos[0]))
        subprocess.call("youtube-dl -x --audio-format mp3 -o '%s/%%(title)s.%%(ext)s' http://www.youtube.com%s" % (dir_path,videos[0]), shell=True)

if __name__ == "__main__":
    download_playlist(sys.argv[1])
