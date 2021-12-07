import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np
import json
import re


"""
Histogram 1
Average of subscriber counts per artist in each genre 
"""

def histogram1():
    
    genre_names = []
    subscribers_sum = []
    
    file_obj = open("subscribers.txt", 'r')

    # read in each line of the file to a list
    raw_data = file_obj.readlines()
    file_obj.close()

    for line in raw_data:
        
        genre_regex = list(re.findall("(^\w.*?)\d", line))
        count_regex = list(re.findall("\d+", line))
        genre = genre_regex[0].strip()
        count = int(count_regex[0])

        genre_names.append(genre)
        subscribers_sum.append(count)
        

    fig, ax = plt.subplots(figsize=(8,7))

    N = len(genre_names)
    width = 0.35
    ind = np.arange(N)
    p1 = ax.bar(ind, subscribers_sum, width, color='blue')
    ax.set_xticks(ind)
    ax.set_xticklabels(genre_names, fontsize=10, rotation='vertical')

    ax.autoscale_view()
    ax.set(xlabel='Genres', ylabel='Average Subscriber Count', \
        title='Average Subscriber Count of Top Artists per Genre')
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
Average of view counts per artist in each genre 
Joining ViewCount, TopTracks, NapsterTopArtist, Genre
"""

def youtube_extra():
    
    file_obj = open("viewcount.txt", 'r')
    genre_names = []
    viewcount_avg = []

    # read in each line of the file to a list
    raw_data = file_obj.readlines()
    file_obj.close()

    for line in raw_data:
        
        genre_regex = list(re.findall("(^\w.*?)\d", line))
        viewcount_regex = list(re.findall("\d+", line))
        genre = genre_regex[0].strip()
        viewcount = int(viewcount_regex[0])

        genre_names.append(genre)
        viewcount_avg.append(viewcount)


    fig, ax = plt.subplots(figsize=(8,7))

    N = len(genre_names)
    width = 0.35
    ind = np.arange(N)
    p1 = ax.bar(ind, viewcount_avg, width, color='blue')
    ax.set_xticks(ind)
    ax.set_xticklabels(genre_names, fontsize=10, rotation='vertical')

    ax.autoscale_view()
    ax.set(xlabel='Genres', ylabel='Average Play Counts', \
        title='Average of Play Counts of Top Songs in each Genre')
    ax.grid()
    fig.tight_layout()

    for i in range(len(viewcount_avg)):
        plt.text(i, viewcount_avg[i], viewcount_avg[i], fontsize = 5.5, ha = 'center')

    #fig.savefig("name.png") - for saving the image
    plt.show()

"""
Piechart (extra visualization): 
Shows the percentage of artists with subscribers 
above a value of 500,000 versus below it. 
Visualizes the % of top artists who have a notable
number of Youtube channel subs. 
"""
def percentageOfPopularChannels():

    path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(path, 'piechart_data.json')
    
    #define parameters for piechart 
    sizes = []
    with open(full_path, 'r') as infile:
        data = json.load(infile)
        sizes.append(data['percentageAbove'])
        sizes.append(data['percentageBelow'])
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
Histogram 
Average song length for top 10 artists by genre (only top 10)
**use either track price or trackmilliseconds in itunes API
**write in calculations
"""
def histogram2():
    pass






"""
Scatterplot
Subscribers vs. View Count of Top Video for each artist
"""
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
    ax.set(xlabel='View Count', ylabel='Subscribers', \
        title='View Count vs. Subscribers')
    fig.tight_layout()

    fig.savefig("scatterplot.png")
    plt.show()


def visualizations():

    histogram1()
    youtube_extra()
    # percentageOfPopularChannels()
    # scatterplot()

visualizations()
