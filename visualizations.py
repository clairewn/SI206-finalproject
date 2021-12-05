import setup
import calculations

import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np


"""
Helper function: return a dictionary with Genres as the key and a list of artist subscription count under them

"""


"""
Histogram
Summary of play counts for top 10 artists by genre (only top 10)
"""
def histogram1(cur, conn):


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
    histogram1(cur, conn)

    return 0

if __name__ == "__main__":
    main()