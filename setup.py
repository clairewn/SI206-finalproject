import sqlite3
import os
import json
import requests

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
def obtain_artists(cur, conn):
    cur.execute("SELECT COUNT(*) FROM Genres")
    total_genres = cur.fetchone()[0]

    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='NapsterTopArtists'")
    
    if cur.fetchone()[0]==0: 
        cur.execute("CREATE TABLE NapsterTopArtists(name TEXT, genre INTEGER, artist_id INTEGER)")

    base_url = 'https://api.napster.com/v2.0/genres/{}/artists/top?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm'
    
    # API already limits to 10 artists per request for top artists per genre
    for genre_id in range(0, total_genres):
        # obtain genre id
        request_str = "SELECT genre_id from Genres where table_id={}"
        format_str = request_str.format(str(genre_id+1))
        cur.execute(format_str)
        genre_id = cur.fetchone()[0]

        # get data
        request_url = base_url.format(genre_id)
        response = requests.get(request_url)
        r = response.text
        data = json.loads(r)

        # add to table
        for item in data['artists']:
            cur.execute("INSERT INTO NapsterTopArtists(name, genre, artist_id) VALUES (?, ?, ?)", (item['name'], genre_id, item['id']))
    conn.commit()

"""
Uses Apple Music API
From charts, get top 10 artists of selected genres
"""
def load_topArtistsbyGenre(genre):
    pass

"""
Uses Apple Music API
From selected artist, get top tracks including length of song
Join with table from topArtistsbyGenre
"""
def load_topTracksbyArtistSongLength(artist):
    pass

"""
Uses Mixcloud API
From selected artist, use previous table to find the tracks and get the play counts
Add into same table
"""
def load_topTracksbyArtistPlayCounts():
    pass


"""
Main function for this file, calls all function to collect data and store into databases
"""
def setUp():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()

    obtain_genres(cur, conn)
    obtain_artists(cur, conn)