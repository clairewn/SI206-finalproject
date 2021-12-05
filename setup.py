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
        if response.status_code != 200:
            # TODO: delete from original table?
            continue
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

        found = False
        for i in data["results"]:
            if i["wrapperType"] == "track":
                track = i['trackName']
                found = True
                break
        if not found:
            continue

        cur.execute("INSERT OR IGNORE INTO TopTracks(name, top_track) VALUES (?, ?)", (name[0], track))
        # cur.execute("UPDATE NapsterTopArtists SET top_track=? WHERE name=?", (track, name[0]))
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

    #cur.execute("DROP TABLE IF EXISTS NapsterTopArtists")
    #cur.execute("DROP TABLE IF EXISTS Subscribers")
    #cur.execute("DROP TABLE IF EXISTS ViewCount")

    obtain_genres(cur, conn)
    obtain_artists(cur, conn, round)
    topTrackForArtist(cur, conn)
    

    outfile = open(full_path,'w', encoding='utf-8')
    round = int(round) + 1
    num = str(round)
    outfile.write(num)
    outfile.close()

#setUp() - if just run this setup.py to test 