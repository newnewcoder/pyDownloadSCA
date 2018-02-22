from bs4 import BeautifulSoup
from urllib.request import urlopen
import re, datetime, subprocess

url = 'http://w2.goodtv.org/studio_classroom/'
page = urlopen(url)

bs = BeautifulSoup(page, "html.parser")

src = bs.findAll('source', attrs={'src': re.compile('^((?!m4a).)*$')})[0]['src']

# print(src)

playlist_all = urlopen(src)

file_root = 'http://sc.streamingfast.net'

resolution = '500k'

playlist = [file_root + line for line in [line.decode('utf-8').strip() for line in playlist_all] if '#' not in line and '\r\n' != line and resolution in line][0]

ffmpeg_command = 'ffmpeg -i {} -c copy -bsf:a aac_adtstoasc {}.mp4'.format(playlist, datetime.datetime.today().strftime('%Y-%m-%d'))

process = subprocess.Popen(ffmpeg_command, shell=True)
process.wait()
