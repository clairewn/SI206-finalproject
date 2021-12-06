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
- "AIzaSyA6izzamX571VKt-9ok6WONA5Y3vcIsOEY"
- "AIzaSyCGlIVEN7iVD5iN6RQ4ZEXuRxrPiUrcm9M"
- "AIzaSyCjL4AEScFAEb5648wstv4bf-z-w_GlPYk"
- "AIzaSyDdWPcix3qiQZVPg9Mx2GXwHkoIiewK9dE"

"""

# #getting artist names from TopTracks table (note: not from Top Artists!)
def get_artist_names(cur,conn): 
    command = "SELECT artist_id FROM TopTracks"
    cur.execute(command)
    list_of_name_tuples = cur.fetchall()
    top_artist_names = []
    for item in list_of_name_tuples:
        top_artist_names.append(item[0])
    top_artists = list(dict.fromkeys(top_artist_names))
    return top_artists


# #getting song names from TopTracks table (note: not from Top Artists!)
# def get_track_names(cur,conn):
#     command = "SELECT top_track FROM TopTracks"
#     cur.execute(command)
#     list_of_track_tuples = cur.fetchall()
#     top_track_names = []
#     for item in list_of_track_tuples:
#         top_track_names.append(item[0])
#     top_tracks = list(dict.fromkeys(top_track_names))
#     return top_tracks

def obtain_channelsubscriber(cur,conn):
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=channel&q={}&key={}"
    # youtube_key = "AIzaSyDdWPcix3qiQZVPg9Mx2GXwHkoIiewK9dE"
    youtube_key = "AIzaSyA6izzamX571VKt-9ok6WONA5Y3vcIsOEY"
    cur.execute("CREATE TABLE IF NOT EXISTS Subscribers (channel_id TEXT PRIMARY KEY, artist_id INTEGER, subscriber_count INTEGER)")
    conn.commit()

    all_artists = get_artist_names(cur,conn)
    #get the existing artists in the subscriber table so far.

    cur.execute('SELECT artist_id FROM Subscribers')
    existing_artist = cur.fetchall()
    existing_artists_in_youtube = []    
    #Gets existing song names from the Subscriber table, so that we know not to add them again.
    for artist_id in existing_artist:
        existing_artists_in_youtube.append(artist_id[0])

    name_retrieval_base = "SELECT name FROM NapsterTopArtists WHERE artist_id={}"

    for artist_id in all_artists:
        if artist_id not in existing_artists_in_youtube: #filter out those already in Subscriber table
            request_query = name_retrieval_base.format(str(artist_id))
            cur.execute(request_query)
            artist_name = cur.fetchone()[0]

            request_url = base_url.format(artist_name,youtube_key)
            r = requests.get(request_url)
            if not r.ok:
                print ("Exception1: Youtube first request error")                    
                print(r.text)
                return None
            
                #print(request_url)
            data = r.text
            json_data = json.loads(data)

            if json_data['pageInfo']['totalResults'] == 0:
                print("--------")
                print("Channel Not Found for: " + artist_name)
                print(request_url)
                print(json_data)
                print("--------")
                continue

            #use channelID to get subscriberCounts, call request again:
            channelID = json_data['items'][0]['id']['channelId']
            base_url2 = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id={}&key={}"
            request_url2 = base_url2.format(channelID,youtube_key)

            r2 = requests.get(request_url2)
            if not r.ok:
                print ("Exception2: Youtube second request error")
                return None
            data2 = r2.text
            json_data2 = json.loads(data2)

            if json_data2["items"][0]["statistics"]["hiddenSubscriberCount"] == True:
                print("hiddenSub")
                return None

            subscriberCount = int(json_data2["items"][0]["statistics"]["subscriberCount"])
            #print(artist_name + "subscriber count is " + str(subscriberCount))
            cur.execute("INSERT OR IGNORE INTO Subscribers (channel_id, artist_id, subscriber_count) VALUES (?, ?, ?)", (channelID,artist_id,subscriberCount))
            conn.commit()

#     conn.commit()

def subscribers_for_artist(artist):
    youtube_key = "AIzaSyA6izzamX571VKt-9ok6WONA5Y3vcIsOEY"
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=channel&q={}&key={}"
    request_url = base_url.format(artist,youtube_key)
    r = requests.get(request_url)
    if not r.ok:
        return None
    data = r.text
    json_data = json.loads(data)
    if json_data['pageInfo']['totalResults'] == 0:
        return None
    channelID = json_data['items'][0]['id']['channelId']
    base_url2 = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id={}&key={}"
    request_url2 = base_url2.format(channelID,youtube_key)
    r2 = requests.get(request_url2)
    if not r.ok:
        return None
    data2 = r2.text
    json_data2 = json.loads(data2)
    if json_data2["items"][0]["statistics"]["hiddenSubscriberCount"] == True:
        return None
    return int(json_data2["items"][0]["statistics"]["subscriberCount"])

def viewcount_for_track(songName):
    youtube_key = "AIzaSyCGlIVEN7iVD5iN6RQ4ZEXuRxrPiUrcm9M"
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