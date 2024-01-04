# This file will be dedicated to get songs detail from a playlist then get all the ID's of the song

#%% Import Library
from configparser import ConfigParser
import requests
import json
import re
import csv
import pandas as pd

#%% Get Token

parser = ConfigParser()
_ = parser.read('notebook.cfg')

# Retrieve the Credentials
client_id, client_secret = parser.get('app_test', 'client_id'), parser.get('app_test', 'client_secret')

url = "https://accounts.spotify.com/api/token"

payload=f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

AccessToken = json.loads(response.text)['access_token']

#%% ### Runner V2.0

main_data = []
id_list = []

def getArtistGenre(artist_id):
  url_artistDetail = f'https://api.spotify.com/v1/artists/{artist_id}'

  payload = {}
  headers = {
    'Authorization': f'Bearer {AccessToken}'
  }

  genreFetch = requests.get(url_artistDetail, headers=headers, data=payload).json()
  return genreFetch['genres']
  
formatted = []
idChecker = []

def getSongDatas(id):
  formatted = []

  url_audioFeature = f"https://api.spotify.com/v1/audio-features/{id}"
  url_trackFeature = f"https://api.spotify.com/v1/tracks/{id}"

  payload={}
  headers = {
    'Authorization': f'Bearer {AccessToken}'
  }
  track_feature = requests.get(url_trackFeature, headers=headers, data=payload).json()
  audio_features = requests.get(url_audioFeature, headers=headers, data=payload).json()

  # Get ID
  formatted.append(id)

  # Song Title
  formatted.append(track_feature['name'])

  # Artist List 
  temp_a = []
  temp_artist = [getArtistGenre(artist['id']) for artist in track_feature['artists']]
  for _i in temp_artist:
    for __i in _i:
      if __i in temp_a:
        pass
      else:
        temp_a.append(__i)

  formatted.append(temp_a)

  # Popularity
  formatted.append(track_feature['popularity'])

  # Audio Features
  for _ in audio_features:
    formatted.append(audio_features[_])

  return formatted

def playlistExtract(playlist_url):
  playlist_id = re.search(r'(?<=playlist/)\w+', playlist_url).group()

  url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

  payload={}
  headers = {
    'Authorization': f'Bearer {AccessToken}'
  }

  response = requests.get(url, headers=headers, data=payload).json()
  _data = [getSongDatas(song['track']['id']) for song in response['items'] if song['track']['id'] not in idChecker]
  idChecker.extend(song['track']['id'] for song in response['items'] if song['track']['id'] not in idChecker)

  for _singular in _data:
    main_data.append(_singular)
#%% Read data from JSON file

with open("playlist_list.json", "r") as file:
    plistData = json.load(file)

playlistCounter = 0

for _playlist in plistData['origin']:
  playlistExtract(_playlist)
  
  # Counter
  playlistCounter += 1

  plistLen = len(plistData['origin'])
  print(f'Extracting {playlistCounter}/{plistLen}')

#%% Saving the entire scrapping in CSV

# Specify the file path for the CSV file
csv_file_path = 'database/output.csv'

# Open the CSV file in write mode
with open(csv_file_path, 'w', newline='') as file:
  writer = csv.writer(file)
  writer.writerow(['songID', 'songTitle', 'SongArtistTitle', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature'])
  
  iterator = 0
  # Iterate over each list in abc and write it as a row in the CSV file
  for row in main_data:
    writer.writerow(row)
    iterator += 1
    
print(f"CSV file '{csv_file_path}' created successfully.")