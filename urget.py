#!/usr/bin/env python3
import argparse
import requests
import json
import subprocess
from colorama import Fore, Back, Style

parser = argparse.ArgumentParser(description='UR Get')
parser.add_argument('url', help='URL')
parser.add_argument('--json', action='store_true')
args = parser.parse_args()

r = requests.get(args.url)
html = r.text.split('urPlayer.init(')[-1].split(');')[0]
json_data = json.loads(html)

if args.json:
  # Pretty print
  print(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))
  exit()

quality = 'hd'
file_path = json_data['file_' + quality]
file_name = file_path.split('/')[-1]
ip = json_data['streaming_config']['streamer']['redirect']
hls_file = json_data['streaming_config']['http_streaming']['hls_file']

# If HD is not available, use flash quality instead.
if file_path == '':
  file_path = json_data['file_flash']
  file_name = file_path.split('/')[-1]
  quality = 'flash'

file_path = 'ondemand/_definst_/mp4:' + file_path + '/' + hls_file

print(Fore.MAGENTA + '------')
print(Fore.WHITE +   'UR Get')
print(Fore.MAGENTA + '------')
print(Fore.RED + 'Title: '   + Fore.RESET + json_data['title'])
print(Fore.RED + 'Quality: ' + Fore.RESET + quality)

# Subtitles
subtitle_labels = json_data['subtitle_labels'].split(',')
subtitles = json_data['subtitles'].split(',')

# Download subtitles
for x in range(0, len(subtitle_labels)):
  print(Fore.RED + 'Downloading subtitle (using wget): ' + Fore.RESET + subtitle_labels[x] + ' - ' + Fore.MAGENTA + subtitles[x].split('/')[-1])
  subprocess.call('wget ' + subtitles[x], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Download video
print(Fore.RED + 'Downloading video (using ffmpeg): ' + Fore.MAGENTA + file_name)
print(Fore.WHITE)
ffmpeg_settings = '-acodec copy -vcodec copy -absf aac_adtstoasc'
command = 'ffmpeg -i "http://' + ip + '/' + file_path + '" ' + ffmpeg_settings + ' "' + file_name + '"'
subprocess.call(command, shell=True)
print(Fore.RESET)
