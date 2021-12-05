import setup
import calculations
import youtube

import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np


"""
Histogram 1
Summary of subscriber counts for top 10 artists by genre (only top 10)
"""

def histogram1(cur,conn):
    command = """
        SELECT SUM(Subscribers.subscriber_count), Genres.genre
        FROM Subscribers 
        JOIN NapsterTopArtists ON Subscribers.artistName = NapsterTopArtists.name
        JOIN Genres ON Genres.genre_id = NapsterTopArtists.genre
        GROUP BY Genres.genre;
        
    """
    # command = """
    #     SELECT ViewCount.view_count, Genres.genre
    #     FROM Subscribers 
    #     JOIN TopTracks
    #     ON Subscribers.artistName = TopTracks.name
    #     JOIN Genres
    #     ON Genres.genre_id = TopTracks.
    #     GROUP BY Genres.genre;

    # """  
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

    #fig.savefig("name.png")
    plt.show()

    pass




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
    
    #setup.setUp()
    #calculations.calculate()
    #histogram1()
    #histogram2()
    #scatterplot()
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'music.db')
    cur = conn.cursor()
    #histogram1(cur, conn)
    histogram1(cur,conn)

    return 0

if __name__ == "__main__":
    main()