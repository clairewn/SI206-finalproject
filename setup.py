import sqlite3
import os
import json

"""
Connect to Apple API
"""
def appleAPI():
    pass

"""
Connect to Napster API
"""
def napsterAPI():
    pass

"""
Connect to Mixcloud API
"""
def mixcloudAPI():
    pass

"""
Uses Napster API
Get genres and set up a table of genres with a corresponding integer
"""
def obtain_genres():
    pass

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