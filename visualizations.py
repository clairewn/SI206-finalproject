import setup
import calculations
import youtube

import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np
import json


"""
Histogram 1
Summary of subscriber counts for top 10 artists by genre 
"""

def histogram1(cur,conn):
    command = """
        SELECT SUM(Subscribers.subscriber_count), Genres.genre
        FROM Subscribers 
        JOIN NapsterTopArtists ON Subscribers.artistName = NapsterTopArtists.name
        JOIN Genres ON Genres.genre_id = NapsterTopArtists.genre
        GROUP BY Genres.genre;
        
    """
    
    cur.execute(command)
    list_of_genre_tuples = cur.fetchall()
    genre_names = []
    subscribers_sum = []
    for item in list_of_genre_tuples:
        genre_names.append(item[1]) #these are the keys
        subscribers_sum.append(item[0])

    fig, ax = plt.subplots(figsize=(8,7))

    N = len(genre_names)
    width = 0.35
    ind = np.arange(N)
    p1 = ax.bar(ind, subscribers_sum, width, color='blue')
    ax.set_xticks(ind)
    ax.set_xticklabels(genre_names, fontsize=10, rotation='vertical')

    ax.autoscale_view()
    ax.set(xlabel='Genres', ylabel='Sum of Subscriber Counts of Top 10 Artists ', \
        title='Number of subscribers for top artists in each genre')
    ax.grid()
    fig.tight_layout()

    for i in range(len(subscribers_sum)):
        #if (subscribers_sum[i] > 10000000 or subscribers_sum[i] < 1000):
            #plt.text(i, subscribers_sum[i], subscribers_sum[i], ha = 'center')
        plt.text(i, subscribers_sum[i], subscribers_sum[i], fontsize = 5.5, ha = 'center')

    #fig.savefig("name.png") - for saving the image
    plt.show()


"""
Histogram (extra visualization)
Summary of view counts for top 10 music videos from each genre 
Joining ViewCount, TopTracks, NapsterTopArtist, Genre
"""

def youtube_extra(cur,conn):
    #first - get a list of unique tuples (artistName, trackName)

    command = "SELECT DISTINCT name, top_track FROM TopTracks"
    cur.execute(command)
    list_of_artist_songs = cur.fetchall()
    #print(list_of_artist_songs)

    #next - get the genre of this track (artistName, trackName)
    d = {}
    command2 = "SELECT Genres.genre FROM Genres JOIN NapsterTopArtists ON Genres.genre_id = NapsterTopArtists.genre WHERE NapsterTopArtists.name = (?)"
    #command2 = "SELECT genre FROM NapsterTopArtists WHERE name = '{}'"
    

    for pair in list_of_artist_songs:
        artistName = pair[0]
        command_two = command2.format(artistName)
        print(command_two)
        cur.execute(command2,(artistName,))
        result = cur.fetchone()[0] #- this would be the genre ID

        print(result)

        songName = pair[1]
        #command_three = "SELECT view_count FROM ViewCount WHERE song_name = ("%s")" %(songName)
        cur.execute('SELECT view_count FROM ViewCount WHERE song_name = \"{}\"'.format(songName))
        this_song_count = int(cur.fetchone()[0]) #- this would be the view count

        if result not in d:
            d[result] = this_song_count
        else:
            d[result] = d[result] + this_song_count
    
    genres = list(d.keys())
    view_count_sum = list(d.values())

    fig, ax = plt.subplots(figsize=(8,7))

    N = len(genres)
    width = 0.35
    ind = np.arange(N)
    p1 = ax.bar(ind, view_count_sum, width, color='blue')
    ax.set_xticks(ind)
    ax.set_xticklabels(genres, fontsize=10, rotation='vertical')

    ax.autoscale_view()
    ax.set(xlabel='Genres', ylabel='Sum Play Counts of Top 10 Songs', \
        title='Sum of Play Counts of Top Songs in each Genre')
    ax.grid()
    fig.tight_layout()

    for i in range(len(view_count_sum)):
        plt.text(i, view_count_sum[i], view_count_sum[i], fontsize = 5.5, ha = 'center')

    #fig.savefig("name.png") - for saving the image
    plt.show()

"""
Piechart (extra visualization): 
Shows the percentage of artists with subscribers 
above a value of 500,000 versus below it. 
Visualizes the % of top artists who have a notable
number of Youtube channel subs. 
"""
def percentageOfPopularChannels(cur, conn):

    #initialize data
    total_artists = 0
    cur.execute("SELECT name FROM NapsterTopArtists")

    #fetch all artist names & loop through it
    artist_info = cur.fetchall()
    for i in artist_info:
        total_artists += 1
    
    #initialize data to 0 and get sub numbers above 500k
    percentageAboveValue = 0 
    cur.execute("SELECT subscribers FROM NapsterTopArtists WHERE subscribers >=?", (500000,))
    subscriber_data = cur.fetchall()

    for x in subscriber_data:
        percentageAboveValue += 1

    percentageBelowValue = total_artists - percentageAboveValue 

    #define parameters for piechart 
    sizes = [percentageAboveValue, percentageBelowValue] 
    labels = ["Above 500k subs", "Below 500k subs"]
    colors = ["blue", "red"]

    fig1, ax1 = plt.subplots()
    ax1.set(title="Percentage of Top Artists with over 500k Youtube Subscribers")
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.legend(title="Key:")
    #equal aspect ratio makes sure pie is drawn as a circle 
    ax1.axis('equal') 
    
    plt.show()

"""
Scatterplot
Subscribers vs. View Count of Top Video for each artist
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

def scatterplot():
    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'scatterplot_data.json')
    data = {}
    with open(full_path, 'r') as infile:
        data = json.load(infile)
    
    colormap = ['black', 'rosybrown', 'red', 'sienna', 'darkorange', 'goldenrod', 'gold', 'olive', 'yellow', 'greenyellow', 'palegreen', 'lime', 'teal', 'cyan', 'deepskyblue', 'slategray', 'blue', 'blueviolet', 'mediumorchid', 'violet', 'purple', 'deeppink', 'lightpink']

    fig, ax = plt.subplots()
    count = 0
    for key in data:
        x = data[key]["view_count"]
        y = data[key]["subscribers"]
        ax.scatter(x, y, c=colormap[count], label=key, alpha=0.5)
        count += 1
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
    fig.tight_layout()
    plt.show()


def main():
    # (Ceciel: I commented out these below when I was testing my graphs,
        # since I was trying to slow down the processing time (only using the existing data)
        # please edit if you are using them! Thanks :)
    
    # setup.setUp() 
    # calculations.calculate()

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    #histogram1(cur, conn)
    # youtube_extra(cur,conn)
    # scatterplot_data(cur)
    scatterplot()
    # scatterplot_without_pop()
    #percentageOfPopularChannels()

    return 0

    

if __name__ == "__main__":
    main()

