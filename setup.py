import sqlite3
import os
import json
import requests
import calculations

"""
Uses Napster API
Get genres and set up a table of genres with a corresponding integer
Should be 23 genres
"""
def obtain_genres(cur, conn):
    response = requests.get('https://api.napster.com/v2.0/genres?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm')
    r = response.text
    data = json.loads(r)

    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Genres'")
    
    if cur.fetchone()[0]==1: 
        return

    cur.execute("CREATE TABLE Genres(table_id INTEGER PRIMARY KEY, genre TEXT, genre_id INTEGER)")
    
    count = 1
    for item in data['genres']:
        cur.execute("INSERT INTO Genres (table_id, genre, genre_id) VALUES (?, ?, ?)", (count, item['name'], item['id']))
        count += 1
    conn.commit()

    
"""
Uses Napster API
Get top artists 
"""
def obtain_artists(cur, conn, round):
    cur.execute("SELECT COUNT(*) FROM Genres")
    total_genres = cur.fetchone()[0]

    cur.execute("CREATE TABLE IF NOT EXISTS NapsterTopArtists(name TEXT, genre INTEGER, artist_id INTEGER)")
    base_url = 'https://api.napster.com/v2.2/genres/{}/artists/top?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm'
    
    for artist in range(0, total_genres):
        # obtain genre id
        genre_id = artist + 1
        request_str = "SELECT genre_id from Genres where table_id={}"
        format_str = request_str.format(str(genre_id))
        cur.execute(format_str)
        genre_id = cur.fetchone()[0]

        # get data
        request_url = base_url.format(genre_id)
        response = requests.get(request_url)
        r = response.text
        data = json.loads(r)

        # select artist
        # rand_artist = random.randint(0, 9)
        artist = data['artists'][int(round)]

        cur.execute("INSERT OR IGNORE INTO NapsterTopArtists(name, genre, artist_id) VALUES (?, ?, ?)", (artist['name'], genre_id, artist['id']))
        conn.commit()

"""Uses Itunes API
Uses the top artist names from NapsterTopArtists table above
to search through Itunes API 
and obtain their top song. 
"""
    
def topTrackForArtist(cur, conn):
    
    #uses names from table for searching purposes
    cur.execute("SELECT name FROM NapsterTopArtists")
    all_artists = cur.fetchall()

    #adds new column "top_track" to existing table to match top artists for the 23 genres 
    # cur.execute("ALTER TABLE NapsterTopArtists ADD COLUMN top_track char(50)")
    cur.execute("CREATE TABLE IF NOT EXISTS TopTracks(name TEXT, top_track TEXT)")

    for name in all_artists:
        #replaces the spaces in names with '+' for Itunes API term
        dude = name[0].replace(" ", "+")
        #search for the content with full URL w/ correct parameter keys (escapes & character in artist name)
        request_url = 'https://itunes.apple.com/search?term={}&entity=musicArtist&limit=10'.format(dude.replace("&", "%26"))
        print(request_url)
        #get data from API 
        response = requests.get(request_url)
        r = response.text
        data = json.loads(r)
        
        
        artistid = None
        unavailable = False
        print(name[0])
        for i in data["results"]:
            if i["artistName"].lower() == name[0].lower():
                print(i)
                if ("amgArtistId" not in i):
                    unavailable = True
                else:
                    artistid = i["amgArtistId"]
                break
        if unavailable:
            continue
        
        request_url = 'https://itunes.apple.com/lookup?amgArtistId={}&entity=song&limit=5'.format(artistid)
        print(request_url)
        response = requests.get(request_url)
        if response.status_code != 200:
            # TODO: delete from original table?
            continue
        r = response.text
        data = json.loads(r)

        for i in data["results"]:
            if i["wrapperType"] == "track":
                track = i['trackName']
                break

        cur.execute("INSERT OR IGNORE INTO TopTracks(name, top_track) VALUES (?, ?)", (name[0], track))
        # cur.execute("UPDATE NapsterTopArtists SET top_track=? WHERE name=?", (track, name[0]))
        conn.commit()


""" Youtube
Getting subscriber count based on the name of the artist 
Create two new tables Subscribers, 
Two helper functions: get_artist_names gets all of the current artist so far; get_track_names gets all of the song names.
    When calling this portion we can also comment out the request calls to other apis
"""

def get_artist_names(cur,conn):
    command = "SELECT name FROM NapsterTopArtists"
    cur.execute(command)
    list_of_name_tuples = cur.fetchall()
    top_artist_names = []
    for item in list_of_name_tuples:
        top_artist_names.append(item[0])
    return top_artist_names

def get_track_names(cur,conn):
    command = "SELECT top_track FROM NapsterTopArtists"
    cur.execute(command)
    list_of_track_tuples = cur.fetchall()
    top_track_names = []
    for item in list_of_track_tuples:
        top_track_names.append(item[0])
    return top_track_names

def obtain_channelsubscriber(cur,conn):
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=channel&q={}&key={}"
    youtube_key = "AIzaSyCGlIVEN7iVD5iN6RQ4ZEXuRxrPiUrcm9M"
    cur.execute("CREATE TABLE IF NOT EXISTS Subscribers (channel_id TEXT PRIMARY KEY, artistName TEXT, subscriber_count INTEGER)")
    conn.commit()

    all_artists = get_artist_names(cur,conn)

    for i in range(len(all_artists)):
        artist_name = all_artists[i]
        request_url = base_url.format(artist_name,youtube_key)
        r = requests.get(request_url)
        if not r.ok:
            print ("Exception1: Youtube first request error")
            print(r)
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
        cur.execute("INSERT OR IGNORE INTO Subscribers (channel_id, artistName, subscriber_count) VALUES (?, ?, ?)", (channelID,artist_name,subscriberCount))
        conn.commit()

def obtain_viewcount(cur, conn):
    youtube_key = "AIzaSyCGlIVEN7iVD5iN6RQ4ZEXuRxrPiUrcm9M"
    base_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelType=any&eventType=none&maxResults=5&type=video&q={}&key={}"
    cur.execute("CREATE TABLE IF NOT EXISTS ViewCount (video_id TEXT PRIMARY KEY,  song_name TEXT, view_count INTEGER)")
    conn.commit()

    all_songs = get_track_names(cur,conn)

    for i in range(len(all_songs)):
        songName = all_songs[i]
        request_url = base_url.format(songName,youtube_key)
        r = requests.get(request_url)
        if not r.ok:
            print ("Exception1: Youtube first request error")
            print(r)
            return None
        
        #print(request_url)
        data = r.text
        json_data = json.loads(data)

        if json_data['pageInfo']['totalResults'] == 0:
            print("--------")
            print("Song Not Found for: " + songName)
            print(request_url)
            print(json_data)
            print("--------")
            continue

        #use channelID to get subscriberCounts, call request again:
        videoID = json_data['items'][0]['id']['videoId']
        base_url2 = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails,statistics&id={}&key={}"
        request_url2 = base_url2.format(videoID,youtube_key)
        #print(channelID)

        r2 = requests.get(request_url2)
        if not r.ok:
            print ("Exception2: Youtube second request error")
            return None
        data2 = r2.text
        json_data2 = json.loads(data2)

        viewCount = int(json_data2['items'][0]['statistics']['viewCount'])

        #print(artist_name + "subscriber count is " + str(subscriberCount))
        cur.execute("INSERT OR IGNORE INTO ViewCount (video_id, song_name, view_count) VALUES (?, ?, ?)", (videoID,songName,viewCount))
        conn.commit()


"""
Main function for this file, calls all function to collect data and store into databases
"""
def setUp():
    path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(path, 'round.txt')
    infile = open(full_path,'r', encoding='utf-8')
    round = infile.readline()
    infile.close()

    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()

    # cur.execute("DROP TABLE IF EXISTS NapsterTopArtists")
    #cur.execute("DROP TABLE IF EXISTS Subscribers")
    #cur.execute("DROP TABLE IF EXISTS ViewCount")

    obtain_genres(cur, conn)
    obtain_artists(cur, conn, round)
    topTrackForArtist(cur, conn)
    #obtain_channelsubscriber(cur,conn)
    #obtain_viewcount(cur, conn)

    outfile = open(full_path,'w', encoding='utf-8')
    round = int(round) + 1
    num = str(round)
    outfile.write(num)
    outfile.close()

#setUp() - if just run this setup.py to test 