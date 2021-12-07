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

#def histogram_data using new info from itunes API either trackprice or milliseconds













def scatterplot_data(cur):
    cur.execute("""
    SELECT artist_id, view_count
    FROM TopTracks
    """)
    tracks = cur.fetchall()

    scatterplot_data = {}

    for track in tracks:
        cur.execute("""
        SELECT subscribers, genre_id
        FROM NapsterTopArtists
        WHERE artist_id = ?
        """, (track[0],))
        subscribers_num = cur.fetchone()

        view_count = (track[1])
        subscribers = (subscribers_num[0])
        
        cur.execute("""
        SELECT genre
        FROM Genres
        WHERE table_id = ?
        """, (subscribers_num[1],))
        genre_id = cur.fetchone()[0]

        if genre_id not in scatterplot_data:
            scatterplot_data[genre_id] = {"view_count": [], "subscribers": []}
        scatterplot_data[genre_id]["view_count"].append(view_count)
        scatterplot_data[genre_id]["subscribers"].append(subscribers)
    
    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'scatterplot_data.json')
    with open(full_path, 'w') as outfile:
        json.dump(scatterplot_data, outfile)

"""
Main function for this file, calls all functions to calculate data and store into database
"""
def calculate():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    
    average_subscribers_per_genre(cur)
    average_viewcount_per_genre(cur)
    scatterplot_data(cur)

# calculate()
    