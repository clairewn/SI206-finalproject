import sqlite3
import os
import math
import json

from numpy.lib.function_base import average

"""
Takes the database cursor as an input. 
Selects the desired data from the database and  
writes the results of the average number of 
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
        SELECT AVG(view_count)
        FROM TopTracks
        JOIN NapsterTopArtists 
        ON NapsterTopArtists.artist_id = TopTracks.artist_id
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))

        
        avg_count = cur.fetchall()
        average = math.ceil(avg_count)

        write = genre[1] + " " + str(average) + "\n"
        outfile.write(write)

    outfile.close()

"""
Takes in database cursor. Output is a JSON file displaying
the average price of the top songs for each genre. 
"""

def average_price_per_genre(cur):

    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'songprice.txt')
    outfile = open(full_path,'w', encoding='utf-8')

    #calculate data by selecting genres first
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()

    #iterate through to get the average of track_price column
    for genre in genres:
        cur.execute("""
        SELECT AVG(track_price)
        FROM TopTracks
        JOIN NapsterTopArtists 
        ON NapsterTopArtists.artist_id = TopTracks.artist_id
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))

        #write results to .txt file
        average = cur.fetchall()
        
        for x in average:
            x = x[0]
            x = round(x, 2)

        write = genre[1] + " " + "$" + str(x) + "\n"
        outfile.write(write)

    outfile.close()

"""
Takes in database cursor. Output is a JSON file displaying
the average length of the top songs for each genre. 
"""

def average_length_per_genre(cur):

    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'songlength.txt')
    outfile = open(full_path,'w', encoding='utf-8')

    #calculate data by selecting genres first
    cur.execute("SELECT table_id, genre FROM Genres")
    genres = cur.fetchall()

    #iterate through to get the average of track_length column
    for genre in genres:
        cur.execute("""
        SELECT AVG(track_length)
        FROM TopTracks
        JOIN NapsterTopArtists 
        ON NapsterTopArtists.artist_id = TopTracks.artist_id
        WHERE NapsterTopArtists.genre_id = ?
        """, (genre[0],))

        #write results to .txt file
        average = cur.fetchall()
        
        for x in average:
            x = x[0]
            x = round(x, 2)

        #values are in milliseconds 
        write = genre[1] + " " + str(x) + "\n"
        outfile.write(write)

    outfile.close()


"""
Calculates percentages for pie charts and then groups 
artists by their number of subscribers. Results written
to a .json file displaying the % of artists with above
500k Youtube subscribers. 
"""

def piechart_data(cur):
    piechart_data = {}
    #initialize data
    total_artists = 0
    cur.execute("SELECT name FROM NapsterTopArtists")

    #fetch all artist names & loop through it
    artist_info = cur.fetchall()
    for i in artist_info:
        total_artists += 1
    
    #initialize data 
    percentageAboveValue = 0 
    cur.execute("SELECT subscribers FROM NapsterTopArtists WHERE subscribers >=?", (500000,))
    subscriber_data = cur.fetchall()

    for x in subscriber_data:
        percentageAboveValue += 1

    percentageBelowValue = total_artists - percentageAboveValue

    piechart_data['percentageAbove'] = percentageAboveValue
    piechart_data['percentageBelow'] = percentageBelowValue 
    

    # file to store calculated data
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'piechart_data.json')
    with open(full_path, 'w') as outfile:
        json.dump(piechart_data, outfile)


"""
Collects data points for the Scatterplot. 
Gets view count and subscriber count for each artist
and compares the data results. 
"""

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
Main function for this file, calls all functions to calculate data and store into database.
"""
def calculate():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    
    #average_subscribers_per_genre(cur)
    #average_viewcount_per_genre(cur)
    average_price_per_genre(cur)
    average_length_per_genre(cur)
    #piechart_data(cur) **need Youtube data!! ASAP 
    #scatterplot_data(cur)

calculate()
    