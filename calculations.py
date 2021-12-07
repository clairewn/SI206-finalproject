import sqlite3
import os
import math

from numpy.lib.function_base import average

"""
Takes the database cursor as an input. 
Selects the desired data from the database and  
writes the results of average number of 
subscribers for each genre to a .txt file.
"""

def average_subscribers_per_genre(cur):
    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'subscribers.txt')
    outfile = open(full_path,'w', encoding='utf-8')
    
    # calculate data
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()
    
    for genre in genres:
        cur.execute("""
        SELECT SUM(subscribers), COUNT(subscribers)
        FROM NapsterTopArtists
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))
        sum_count = cur.fetchall()
        #round total average to whole integer
    
        average = sum_count[0][0] / sum_count[0][1]
        average = math.ceil(average)
        
        write = genre[1] + " " + str(average) + "\n" 
        outfile.write(write)
        
    outfile.close()
    
"""
Takes the database cursor as an input. 
Selects the desired data from the database and  
writes the results of average number of 
view counts for each genre to a .txt file.
"""

def average_viewcount_per_genre(cur):
    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'viewcount.txt')
    outfile = open(full_path,'w', encoding='utf-8')
    
    # calculate data
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()
    
    for genre in genres:
        cur.execute("""
        SELECT SUM(subscribers), COUNT(subscribers), AVG(subscribers)
        FROM TopTracks
        JOIN NapsterTopArtists 
        ON NapsterTopArtists.artist_id = TopTracks.artist_id
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))

        sum_count = cur.fetchall()
        average = sum_count[0][0] / sum_count[0][1]
        average = math.ceil(average)

        write = genre[1] + " " + str(average) + "\n"
        outfile.write(write)

    outfile.close()

"""
Main function for this file, calls all functions to calculate data and store into database
"""
def calculate():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    
    average_subscribers_per_genre(cur)
    average_viewcount_per_genre(cur)

calculate()
    