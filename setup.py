import sqlite3
import os
import json
import requests
import calculations
import random

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

    cur.execute("CREATE TABLE IF NOT EXISTS NapsterTopArtists(name TEXT, genre INTEGER, artist_id INTEGER)")
    base_url = 'https://api.napster.com/v2.0/genres/{}/artists/top?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm'
    
    for artist in range(0, 25):
        # obtain genre id
        genre_id = random.randint(1, 23)
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
        rand_artist = random.randint(0, 9)
        artist = data['artists'][rand_artist]
        cur.execute("INSERT OR IGNORE INTO NapsterTopArtists(name, genre, artist_id) VALUES (?, ?, ?)", (artist['name'], genre_id, artist['id']))
        conn.commit()

"""
Uses Apple Music API
From charts, get top 10 artists of selected genres
Genres come from the Genres table - store genre_id in table created here
"""
def load_topArtistsbyGenre(cur, conn):
    pass

"""
Uses Apple Music API
From selected artist, get top track including length of song
Add to previous table (do it in the same previous function?)
"""
def load_topTrackandSongLength(cur, conn):
    # use average_song_length function
    pass

"""
Uses Mixcloud API
From selected artist, get play counts (sum) for artist on its most popular track
Create new table for new API, join with Apple Music API
"""
def load_playCountInformation(cur, conn):
    # use sum_play_count function
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