import sqlite3
import os
import json
import requests

"""
Connect to Apple API
"""
def appleAPI():
    pass

"""
Connect to Napster API
"""
def napsterAPI():
    napsterAPI = 'https://api.napter.com'
    napster_APIkey = 'OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm'


"""
Connect to Mixcloud API
"""
def mixcloudAPI():
    pass

"""
Uses Napster API
Get genres and set up a table of genres with a corresponding integer
Should be 23 genres
"""
def obtain_genres():
    response = requests.get('https://https://api.napster.com/v2.0/genres?apikey=OGU2ZWQxNjEtZTI5Yi00MzM1LWE0YTgtNDg5ODZhMjhhZDJm')
    data = response.text

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music')
    cur = conn.cursor()

    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Genres'")
    
    if cur.fetchone()[0]==0: 
        return

    cur.execute("CREATE TABLE Genres(genre_id INTEGER PRIMARY KEY, genre TEXT")
    
    count = 1
    for item in data["genres"]:
        cur.execute("INSERT INTO Genres (genre_id, genre) VALUES (?, ?)", (count, item['name']))
        count += 1

    
"""
Uses Napster API
Get top artists and join with genre table
"""
def obtain_artists():
    pass

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
    pass