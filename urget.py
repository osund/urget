#!/usr/bin/env python3
import argparse
import requests
import json
import subprocess
from colorama import Fore

parser = argparse.ArgumentParser(description='UR Get')
parser.add_argument('url', help='URL')
parser.add_argument('--json', action='store_true')
args = parser.parse_args()

# Parse the JSON from the HTML file.
r = requests.get(args.url)
html = r.text.split('urPlayer.init(')[-1].split(');')[0]
json_data = json.loads(html)

if args.json:
  # Pretty print JSON.
  print(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))
  exit()

def setQuality(q):
  global quality, file_path, file_name
  quality = q
  file_path = json_data['file_' + q]
  file_name = file_path.split('/')[-1]

setQuality('hd')

# If HD is not available, use flash quality instead.
if file_path == '':
  setQuality('flash')

print(Fore.MAGENTA + '------')
print(Fore.WHITE +   'UR Get')
print(Fore.MAGENTA + '------')
print(Fore.RED + 'ID: '   + Fore.RESET + str(json_data['series_id']))
print(Fore.RED + 'Title: '   + Fore.RESET + json_data['title'])
print(Fore.RED + 'Quality: ' + Fore.RESET + quality)
print(Fore.RED + 'Image: '   + Fore.RESET + json_data['image'])

# Download video (.mp4).
streaming_config = json_data['streaming_config']
ip = streaming_config['streamer']['redirect']
hls_file = streaming_config['http_streaming']['hls_file']
file_path = 'ondemand/_definst_/mp4:' + file_path + '/' + hls_file
ffmpeg_flags = '-acodec copy -vcodec copy -absf aac_adtstoasc'
command = 'ffmpeg -i "http://' + ip + '/' + file_path + '" ' + ffmpeg_flags + ' "' + file_name + '"'

print(Fore.RED + 'Downloading video (using ffmpeg): ' + Fore.MAGENTA + file_name)
print(Fore.WHITE)
subprocess.call(command, shell=True)
print(Fore.RESET)

# Download subtitles (.tt).
subtitle_labels = json_data['subtitle_labels'].split(',')
subtitle_urls = json_data['subtitles'].split(',')

for x in range(0, len(subtitle_labels)):
  subtitle_file_name = subtitle_urls[x].split('/')[-1]
  print(Fore.RED + 'Downloading subtitle (using wget): ' + Fore.RESET + subtitle_labels[x] + ' - ' + Fore.MAGENTA + subtitle_file_name)
  subprocess.call('wget ' + subtitle_urls[x], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
