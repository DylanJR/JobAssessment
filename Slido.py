import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
from scipy.optimize import curve_fit
import sys
import h5py
from datetime import datetime
import re
"""
Author: Dylan Robson

A pipeline to search available data sources for restaurant open and close times.

Currently it prioritises source_1 as this has more info in general and then checks if the user
wants to search source_2. I could very easily change this to search both however I preferred source_1 as
it provides more information for each restaurant!


Further Ideas:
-Build a gui and package this up so it can be run outside of python
    -A gui could have buttons for each unique cuisine
    -clicking a restaurant could give you more details
    -I'm not as experienced on front end stuff so I don't know if I can pull this off

-I'd like a better way of parsing strings such that more unexpected formats could be dealt with

-Currently prints out restaurants ordered by rating high to low. Would be good to
 let user choose to order by rating or price but I'm cautious of too many questions.
 This is why a GUI would be nice.
"""

days = {
    'Mon':0,
    'Tue':1,
    'Wed':2,
    'Thu':3,
    'Fri':4,
    'Sat':5,
    'Sun':6,
        }
price_ratings = ['very low', 'low', 'middling', 'high', 'very high']
def pathfinder(Input):
    """
    Function to check if the path input ends in .csv
    Obviously not fool proof operates at least as a cursory check.
    """
    while True:
        if Input[-4::] == '.csv':
            return Input
        else:
            Input = input('Please enter a valid csv file: ')
def CSV_reader(path):
    df      = pd.read_csv(path)
    columns = df.columns
    values  = df.values
    return df, columns, values

def weekday():
    #Very basic function to return present weekday in string
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    now     = datetime.now()
    day     = days[now.weekday()]
    hour    = now.hour
    min     = now.minute
    time = int(hour)+int(min)/60
    return day, time
def twelve_hour(string):
    '''
    Parameters : string representing time in the 11:30 am or 9 pm format
    Returns   : t value for numerical comparison to other times

    Turns a time string of form 9 pm into float of 21.
    '''
    if ':' in string:
        time = string.split(' ')
        num  = time[0].split(':')

        if time[1] == 'am':
            t = int(num[0]) + int(num[1])/60
        elif time[1] == 'pm':
            t = int(num[0]) + int(num[1])/60 +12
        return t
    elif '.' in string:
        time = string.split(' ')
        num  = time[0].split('.')

        if time[1] == 'am':
            t = int(num[0]) + int(num[1])/60
        elif time[1] == 'pm':
            t = int(num[0]) + int(num[1])/60 +12
        return t
    else:
        time = string.split(' ')
        if time[1] == 'am':
            t = int(time[0])
        elif time[1] == 'pm':
            t = int(time[0])+12
        return t
def twentyfour_hour(string):
    '''
    Parameters: string representing time in the 12:00:00 format
    Returns   : t value for numerical comparison to other times

    code takes a time string e.g 21:00 and converts it to a float i.e 21.

    '''
    t = int(string.split(':')[0]) + int(string.split(':')[1])/60
    return t
def time_format(time_string):
    #I'm somewhat hardcoding to the sources here, I would use a regex operation to make this more general
    if '-' in time_string:
        open_close = time_string.split(' - ')
        open = twelve_hour(open_close[0])
        close= twelve_hour(open_close[1])
        print('Returning [open,close] list')
        return [open, close]
    elif ':' in time_string:
        t_s = time_string.split(':')
        t   = int(t_s[0]) + int(t_s[1])/60
        print('Returning single time')
        return t

def mon_to_sun(string):
    '''
    Parameters: string representing the \' Mon-Sun 11:30 am - 9 pm \' format represented in source_1
    Returns   : open_times, a list of opening times ordered by day from mon-sun
                close_times, a list of closing times ordered by day from mon-sun

    code parses strings of a certain form to gather days open and assign corresponding times

    '''
    first = string.split(' / ')
    days = {
    'Mon':0,
    'Tue':1,
    'Wed':2,
    'Thu':3,
    'Fri':4,
    'Sat':5,
    'Sun':6,
        }
    open_times= np.zeros(7)
    close_times = np.zeros(7)
    for i in first:
        j = i.strip()
        k = j.split(' ')
        if k[0][-1] ==',':
            init    = k[0].strip(',')
            second  = k[1]
            if '-' in init:
                open_days = np.arange(days[init.split('-')[0]],days[init.split('-')[1]]+1)
                open_days = np.append(open_days, days[second])
            else:
                open_days = np.arange(days[second.split('-')[0]],days[second.split('-')[1]]+1)
                open_days = np.append(open_days,days[init])
            open_time = twelve_hour(k[2] +' '+k[3])
            close_time= twelve_hour(k[5] + ' '+ k[6])
            for i in open_days:
                open_times[i]=open_time
                close_times[i]=close_time
        else:
            init    =k[0]
            if '-' in init:
                open_days = np.arange(days[init.split('-')[0]],days[init.split('-')[1]]+1)
            else:
                open_days = [days[init]]
            open_time = twelve_hour(k[1]+' '+ k[2])
            close_time= twelve_hour(k[4]+' '+k[5])
            for i in open_days:
                open_times[i]=open_time
                close_times[i]=close_time
    return [open_times, close_times]
def source_2(df, day, time):
    '''
    Parameters: df (pandas datafram)
                    day in the form Mon,Tue Wed etc
                    time in the form 21.5 for 21:30 etc
    Returns   :

    Prints out all restaurants open on the input day and time
    '''
    for i in df.values:
        current = mon_to_sun(i[1])
        if current[0][day] < time < current[1][day]:
            print(i[0] + f' : Closes {current[1][day]}')
def columns(df, day, time):
    '''
    Parameters: df (pandas datafram)
                    day in the form Mon,Tue Wed etc
                    time in the form 21.5 for 21:30 etc
    Returns   :

    Prints out all restaurants open on the input day and time
    '''
    rating = 5

    while rating > 0:
        for i in df.values:
            open = twentyfour_hour(i[3])
            close= twentyfour_hour(i[4])
            days = i[5].strip()
            if ((day[0:2] in days)&(open<time<close)&(i[7] == rating)):
                print(f'{i[0].strip()} closes at {i[4][0:-3]} and serves {i[2].strip()}. Rating: {i[7]}, Price: {price_ratings[int(i[6])-1]}\n')
        rating -=1

def source_check(df, day, time):
    '''
    Parameters: df (pandas datafram)
                day in the form Mon,Tue Wed etc
                time in the form 21.5 for 21:30 etc
    Returns   :

    Function to collate the two separate functions that parse and print relevant properties
    of the two separate source files.
    '''
    Day = days[day]
    if len(df.columns) == 2:
        source_2(df, Day, time)
    elif len(df.columns)==10:
        columns(df, day, time)
def check_availability(Input,df):
    '''
    Receives an input from the user requesting a specific day and time and checks which restaurants
    are available

    Initial check checks to see if string is in the right form
    '''
    while True:

        x = re.search('^(mon|tue|wed|thu|fri|sat|sun)([a-zA-Z])*\s*(([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9])',Input.lower())
        if x:
            temp   = Input.split(' ')
            day     = temp[0][0:3].capitalize()
            Day     = days[day]
            Time    = twentyfour_hour(temp[1])

            '''
            for i in df.values:
                current = mon_to_sun(i[1])
                if current[0][Day] < Time < current[1][Day]:
                    print(i[0] + f' : Closes {current[1][Day]}')
            '''
            source_check(df, day, Time)
            '''
            if len(df.columns) == 2:
                source_2(df, Day, Time)
            elif len(df.columns)==10:
                columns(df, day, Time)
            '''
            #restaurants = [i[0] for i in df.values if (mon_to_sun(i[1])[0][Day] < Time < mon_to_sun(i[1])[1][Day])]

            return
        else:
            Input = input('Please enter desired day and time in form: Day HH:MM: ')
            if Input =='':
                'No input entered'
                break

def learn_more(df):
    '''
    Parameters  : df a pandas dataframe in the form of source_1
    Returns     : info_check to check whether the function should be continuously run

    Code parses the info from the source_1 dataframe and presents it in a easier to read format

    '''
    restaurant_name = input('Please enter a restaurant name!: ')
    while True:
        for i in df.values:
            if (i[0].strip()).lower() == restaurant_name.lower():
                name    = i[0].strip()
                id      = i[1]
                cuisine = i[2].capitalize()
                open    = i[3].strip()[0:-3]
                close   = i[4].strip()[0:-3]
                days    = i[5].strip()
                price   = i[6]
                rating  = i[7]
                location= i[8]
                Desc    = i[9]
                print(f' {name}: \n ----------- \n Social ID: {id} \n Cuisine: {cuisine}\n' \
                f' Open:{days} {open} to {close} \n Price: {price_ratings[price -1]}\n'\
                f' Rating: {rating}\n Address: {location} \n'\
                f' Description: \n ----------- \n {Desc}')
                info_check= input('Would you like more info on any other restaurants? y/n ').lower()
                return info_check
        restaurant_name = input(' Restaurant info not found!\n Please enter a restaurant name!: ')



def late(df, late_check):
    '''
    Parameters  : df, a pandas dataframe to be searched
                  late_check, a string that tells the function whether or not to keep running
    returns     :

    Code to search through a dataset and return info depending on if it's in the form of source_1 or source_2

    '''
    check = True

    while check:
        if late_check[0] == 'y':
            check_availability(input('Please enter a day and time in the format: Day HH:MM: '),df)
            late_check = input('Would you like to search other times? Y/N: ').lower()
        elif late_check[0] =='n':

            check = False
        else:
            late_check = input('Entry not recognised \n Would you like to search other times? Y/N: ').lower()
def info(df):
    '''
    Parameters  : df, a pandas dataframe to be searched
                  late_check, a string that tells the function whether or not to keep running
    returns     :

    Code to search through a dataset and return verbose info for source_1 style datasets

    '''
    check = True
    info_check = input('Would you like any more info on any of these restaurants? y/n ').lower()
    while check:
        if info_check[0] =='y':
            info_check = learn_more(df)
        elif info_check[0]=='n':
            check = False
        else:
            info_check = input('Entry not recognised \n Would you like any more info on any of these restaurants? y/n ').lower()
def further(df):
    '''
    Parameters  : df, a pandas dataframe to be searched
                  late_check, a string that tells the function whether or not to keep running
    returns     :

    Code to search through a dataset and return info depending on if it's in the form of source_1 or source_2

    '''
    check = True

    while check:
        if further_check[0] =='y':
            check_availability(input('Please enter a day and time in the format: Day HH:MM: '),df)
            furter_check = input('Would you like to search other times? Y/N: ').lower()

def main():
    '''
    Code collates the above functions into a single running script to read through available dataframes

    '''
    path = pathfinder(input('Enter path to csv file: '))
    df,c,v = CSV_reader(path)
    df_1,c,v    = CSV_reader('Downloads/data/restaurants-hours-source-2.csv')
    day, time = weekday()

    #The below code returns restaurants that are CURRENTLY open in the source_2 file
    print('The following restaurants are currently open: ')
    source_check(df, day, time)
    late(df, input('Would you like to search other times? ').lower())
    info(df)
    late(df_1,input('Would you like to search the secondary catalogue? y/n ').lower())
    print('Thank you for using this service!')




    #restaurant = [i[0] for i in df.values if (mon_to_sun(i[1])[0][day] < time < mon_to_sun(i[1])[1][day]) ]

    #The below code asks for input from user and returns all restaurants open at specific day and time



    #restaurant = [i[0] for i in df.values if (day[0:2] in i[5].strip())]

    #temp = CSV_to_HDF5(path, df)
