import sqlite3
import os
import json
import requests
import youtube

#TESTING FILE
"""
Takes in the database cursor and connection as inputs.
Returns: None
Creates the Genres Table we will utilize to obtain more data.
Uses Napster API to get 23 total genres.
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
Takes in the database cursor and connection as inputs.
Returns: None
Creates & adds to the NapsterTopArtists Table.
Uses Napster API to get reoccuring top artists for genres 
previously found.
Uses Youtube API to get # of subscribers for each artist name found. 
"""

def obtain_artists(cur, conn, round):
    cur.execute("SELECT COUNT(*) FROM Genres")
    total_genres = cur.fetchone()[0]
    

    cur.execute("CREATE TABLE IF NOT EXISTS NapsterTopArtists(artist_id INTEGER PRIMARY KEY, name TEXT, genre_id INTEGER, subscribers INTEGER)")
    
    cur.execute("SELECT COUNT (*) FROM NapsterTopArtists")
    total_artists = cur.fetchone()[0]
    base_url = 'https://api.napster.com/v2.2/genres/{}/artists/top?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm'
    
    for g in range(0, 25):
        genre = total_artists % total_genres  
        
        genre_id = genre + 1

        request_str = "SELECT genre_id from Genres where table_id={}"
        format_str = request_str.format(str(genre_id))
        cur.execute(format_str)
        genre_id = cur.fetchone()[0]

        

        # get desired data from API using genre 
        request_url = base_url.format(genre_id)
        response = requests.get(request_url)
        r = response.text
        data = json.loads(r)


        # select artist
        temp = total_artists
        count = 0
        while temp > 22:
            temp = temp - 23
            count = count + 1

        artist = data['artists'][int(count)]

        

        table_genre_id = genre + 1

        subscribers = youtube.subscribers_for_artist(artist['name'])
        if subscribers is None:
            print("no subscribers")
            continue

        print(subscribers)
        
        cur.execute("INSERT OR IGNORE INTO NapsterTopArtists(artist_id, name, genre_id, subscribers) VALUES (?, ?, ?, ?)", (total_artists, artist['name'], table_genre_id, subscribers))
        total_artists = total_artists + 1

        

        conn.commit()


"""
Takes in the database cursor and connection as inputs. 
Creates & adds to the TopTracks Table in .db.
Uses ITunes API to search for top artist
names from NapsterTopArtists and retrieves their top song,
music video view count, song price, and length of song. 
"""
    
def topTrackForArtist(cur, conn):
    
    #uses names from table for searching purposes
    cur.execute("SELECT name, artist_id FROM NapsterTopArtists")
    all_artists = cur.fetchall()

    cur.execute("CREATE TABLE IF NOT EXISTS TopTracks(artist_id INTEGER, top_track TEXT, view_count INTEGER, track_price INTEGER, track_length INTEGER)")

    cur.execute("SELECT COUNT (*) FROM TopTracks")
    total_tracks = cur.fetchone()[0]
    check_artists = all_artists[total_tracks:]

    
    for name in check_artists:
        check_url = "SELECT COUNT(*) from TopTracks WHERE artist_id={}"
        format_check = check_url.format(name[1])
        cur.execute(format_check)
        if cur.fetchone()[0] != 0:
            continue
        #replaces the spaces in names with '+' for Itunes API term
        person = name[0].replace(" ", "+")
        #search for the content with full URL w/ correct parameter keys (escapes '&' character in artist name)
        request_url = 'https://itunes.apple.com/search?term={}&entity=musicArtist&limit=10'.format(person.replace("&", "%26"))
        #get data from API 
        response = requests.get(request_url)
        if not response.ok:
            return None
            
        r = response.text
        data = json.loads(r)
        
        
        artistid = None
        unavailable = False
        
        for i in data["results"]:
            if i["artistName"].lower() == name[0].lower():
                
                if ("amgArtistId" not in i):
                    unavailable = True
                else:
                    artistid = i["amgArtistId"]
                break
        if unavailable:
            continue
        
        request_url = 'https://itunes.apple.com/lookup?amgArtistId={}&entity=song&limit=5'.format(artistid)
        
        response = requests.get(request_url)
        if not response.ok:
            return None
        r = response.text
        data = json.loads(r)

        found = False
        for i in data["results"]:
            if i["wrapperType"] == "track":
                track = i['trackName']
                found = True
                break
        if not found:
            continue

 
        request_url = 'https://itunes.apple.com/lookup?amgArtistId={}&entity=song&limit=5'.format(artistid)

        response = requests.get(request_url)
        if not response.ok:
            return None
        r = response.text
        data = json.loads(r)

        found = False
        for i in data["results"]:
            if i["wrapperType"] == "track":
                price = i['trackPrice']
                found = True
                break
        if not found:
            price = 0 # CHANGED THIS


        request_url = 'https://itunes.apple.com/lookup?amgArtistId={}&entity=song&limit=5'.format(artistid)

        response = requests.get(request_url)
        if not response.ok: 
            return None
        r = response.text 
        data = json.loads(r)

        found = False
        for i in data["results"]:
            if i["wrapperType"] == "track":
                length = i['trackTimeMillis']
                found = True
        if not found:
            length = 0 # CHANGED THIS

        viewCount = youtube.viewcount_for_track(track)
        if viewCount == None:
            print("no viewcount")
            continue
        print(viewCount)

        cur.execute("INSERT OR IGNORE INTO TopTracks(artist_id, top_track, view_count, track_price, track_length) VALUES (?, ?, ?, ?, ?)", (name[1], track, viewCount, price, length))
        conn.commit()


"""
Main function for this file, calls all functions to collect data and store into the music database.
"""
def setUp():
    path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(path, 'round.txt')
    infile = open(full_path,'r', encoding='utf-8')
    round = infile.readline()
    infile.close()

    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()

    obtain_genres(cur, conn)
    obtain_artists(cur, conn, round)
    topTrackForArtist(cur, conn)

    outfile = open(full_path,'w', encoding='utf-8')

    num = str(round)
    outfile.write(num)
    outfile.close()

setUp() 


