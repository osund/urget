#!/usr/bin/env python3
import argparse
import requests
import json
import subprocess
from colorama import Fore

parser = argparse.ArgumentParser(description='UR Get')
parser.add_argument('url', help='URL')
parser.add_argument('--json', action='store_true')
parser.add_argument('--rawtitle', action='store_true')
parser.add_argument('--quality')
args = parser.parse_args()

print(Fore.MAGENTA + '------')
print(Fore.WHITE +   'UR Get')
print(Fore.MAGENTA + '------')

def getJS(html):
  return html.split('urPlayer.init(')[-1].split(');')

def setQuality(q):
  global quality, file_path, file_name
  quality = q
  file_path = json_data['file_' + q]
  file_name = file_path.split('/')[-1]

def print_info(desc, data):
  print(Fore.RED + desc + ': ' + Fore.RESET + data)

# Parse the JSON from the HTML file.
r = requests.get(args.url)
html = getJS(r.text)

if len(html) == 1:
  # "Programmet är inte tillgängligt på UR Play.
  #  Men UR:s egenproducerade program, inspelade efter 2007,
  #  finns tillgängliga under fem år på UR.se."
  print(Fore.RESET + 'Using ur.se instead of urplay.se...')
  r = requests.get(args.url.replace('urplay', 'www.ur'))
  html = getJS(r.text)

json_data = json.loads(html[0])

if args.json:
  # Pretty print JSON.
  print(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))
  exit()

setQuality('hd')

# If HD is not available, use flash quality instead.
if file_path == '':
  setQuality('flash')

if args.quality:
  setQuality(args.quality)

# print_info('ID', str(json_data['series_id']))
print_info('Title', json_data['title'])
print_info('Quality', quality)
print_info('Image', json_data['image'])

# Download video (.mp4).
streaming_config = json_data['streaming_config']
ip = streaming_config['streamer']['redirect']
hls_file = streaming_config['http_streaming']['hls_file']
file_path = 'ondemand/_definst_/mp4:' + file_path + '/' + hls_file
ffmpeg_flags = '-acodec copy -vcodec copy -absf aac_adtstoasc'
command = 'ffmpeg -i "http://' + ip + '/' + file_path + '" ' + ffmpeg_flags

title_file_name = json_data['title'].replace(' ', '_')

if args.rawtitle:
  command += ' ' + file_name
else:
  command += ' ' + title_file_name + '.mp4'

print_info('Downloading video (using ffmpeg)', Fore.MAGENTA + file_name)
print(Fore.WHITE)
subprocess.call(command, shell=True)
print(Fore.RESET)

# Download subtitles (.tt).
subtitle_labels = json_data['subtitle_labels'].split(',')
subtitle_urls = json_data['subtitles'].split(',')

for x in range(0, len(subtitle_labels)):
  subtitle_file_name = subtitle_urls[x].split('/')[-1]
  print_info('Downloading subtitle (using wget)', subtitle_labels[x] + ' - ' + Fore.MAGENTA + subtitle_file_name)
  if args.rawtitle:
    subprocess.call('wget ' + subtitle_urls[x], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  else:
    subtitle_file_name = title_file_name + '_' + subtitle_labels[x].replace(' ', '_').replace('(', '').replace(')', '') + '.tt'
    subprocess.call('wget ' + subtitle_urls[x] + ' -O ' + subtitle_file_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
