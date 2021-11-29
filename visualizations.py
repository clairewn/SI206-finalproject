import setup
import calculations

"""
Histogram
Summary of play counts for top 10 artists by genre (only top 10)
"""
def histogram1():
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
    setup.setUp()
    calculations.calculate()
    histogram1()
    histogram2()
    scatterplot()
    return 0

if __name__ == "__main__":
    main()