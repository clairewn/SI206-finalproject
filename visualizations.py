import setup
import calculations
import youtube

import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np


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
Histogram extra (also youtube)
Summary of view counts for top 10 music from each genre 
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
Histogram
Average song length for top 10 artists by genre (only top 10)
"""
def histogram2():
    pass

"""
Scatterplot
Average song length vs. sum of play count for each artist
Top 100 artists
"""
def scatterplot():
    pass


def main():
    # (Ceciel: I commented out these below when I was testing my graphs,
        # since I was trying to slow down the processing time (only using the existing data)
        # please edit if you are using them! Thanks :)
    
    # setup.setUp() 
    calculations.calculate()
    #histogram1()
    #histogram2()
    #scatterplot()

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    #histogram1(cur, conn)
    # youtube_extra(cur,conn)



    return 0

if __name__ == "__main__":
    main()