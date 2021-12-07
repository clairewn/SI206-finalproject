import sqlite3
import os

def average_subscribers_per_genre(cur):
    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'subscribers.txt')
    outfile = open(full_path,'w', encoding='utf-8')
    
    # calculate data
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()
    data = []
    for genre in genres:
        cur.execute("""
        SELECT SUM(subscribers), COUNT(subscribers)
        FROM NapsterTopArtists
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))
        sum_count = cur.fetchall()
        average = sum_count[0][0] / sum_count[0][1]
        write = genre[1] + " " + str(average) + "\n"
        outfile.write(write)
    outfile.close()

def average_viewcount_per_genre(cur):
    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'viewcount.txt')
    outfile = open(full_path,'w', encoding='utf-8')
    
    # calculate data
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()
    data = []
    for genre in genres:
        cur.execute("""
        SELECT SUM(view_count), COUNT(view_count)
        FROM TopTracks
        JOIN NapsterTopArtists
        ON NapsterTopArtists.artist_id = TopTracks.artist_id
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))
        sum_count = cur.fetchall()
        average = sum_count[0][0] / sum_count[0][1]
        write = genre[1] + " " + str(average) + "\n"
        outfile.write(write)
    outfile.close()

"""
Main function for this file, calls all function to calculate data and store into database
"""
def calculate():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    
    average_subscribers_per_genre(cur)
    average_viewcount_per_genre(cur)
    
    