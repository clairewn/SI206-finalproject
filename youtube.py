import sqlite3
import os
import json
import requests

""" Youtube
Getting subscriber count based on the name of the artist (25 at a time).
Getting the viewcount (playcount) of a song based on its name. (25 at a time).

Create two new tables: Subscribers, ViewCount

Two helper functions: 
    (1)get_artist_names gets all of the artist names in the Napster TopArtists table. 
    (2) get_track_names gets all of the song names in the TopTracks table.

Call two API at the same time

Usable API keys (each can only populate 100 rows (whether for the artist subscriber or song viewcount))
    because of quota limitation
- Used: "AIzaSyA6izzamX571VKt-9ok6WONA5Y3vcIsOEY"
- Used: "AIzaSyCGlIVEN7iVD5iN6RQ4ZEXuRxrPiUrcm9M"
- "AIzaSyCjL4AEScFAEb5648wstv4bf-z-w_GlPYk"
- "AIzaSyDdWPcix3qiQZVPg9Mx2GXwHkoIiewK9dE"
- "AIzaSyDQ7NWSHSPiOxPUaVymeEyyzDsKW77ZszQ"
- "AIzaSyC0r1-0UY3BE7R8aMj2QdQKq0f6WZG3UGs"
- "AIzaSyBZIcPo1Y8-WO12MmXGXGU9i7AL7aU_0H0"
- "AIzaSyAiboHaXZEj7R6WlSb34Wit70-5oZKQUt8"

"""

def subscribers_for_artist(artist):
    youtube_key = "AIzaSyCjL4AEScFAEb5648wstv4bf-z-w_GlPYk"
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=channel&q={}&key={}"
    request_url = base_url.format(artist,youtube_key)
    r = requests.get(request_url)
    if not r.ok:
        print("r is not okay")
        return None
    data = r.text
    json_data = json.loads(data)
    if json_data['pageInfo']['totalResults'] == 0:
        print("no results")
        return None
    channelID = json_data['items'][0]['id']['channelId']
    base_url2 = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id={}&key={}"
    request_url2 = base_url2.format(channelID,youtube_key)
    r2 = requests.get(request_url2)
    if not r.ok:
        print("r2 is not okay")
        return None
    print(request_url2)
    data2 = r2.text
    json_data2 = json.loads(data2)
    if json_data2["items"][0]["statistics"]["hiddenSubscriberCount"] == True:
        print("hiddenSubscriberCount")
        #print(r2.text)
        return None
    return int(json_data2["items"][0]["statistics"]["subscriberCount"])

def viewcount_for_track(songName):
    youtube_key = "AIzaSyCjL4AEScFAEb5648wstv4bf-z-w_GlPYk"
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=video&q={}&key={}"
    request_url = base_url.format(songName, youtube_key)
    r = requests.get(request_url)
    if not r.ok:
        return None
    data = r.text
    json_data = json.loads(data)
    if json_data['pageInfo']['totalResults'] == 0:
        return None
    videoID = json_data['items'][0]['id']['videoId']
    base_url2 = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails,statistics&id={}&key={}"
    request_url2 = base_url2.format(videoID,youtube_key)
    r2 = requests.get(request_url2)
    if not r.ok:
        return None
    data2 = r2.text
    json_data2 = json.loads(data2)
    return int(json_data2['items'][0]['statistics']['viewCount'])



