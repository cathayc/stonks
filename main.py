from os import close
import sys
import yfinance as yf

import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from scipy.signal import argrelextrema

#Visualization
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')


#For reading stock data 
import pandas_datareader as pdr
from pandas_datareader import data, wb

#For time stamps 
from datetime import datetime, timedelta

NYT_API = 'bKgOSmaa4IIJZdC0DE1G5ticaqGh6Qns'

class Stock:
    stock_name = ""
    df = pd.DataFrame()
    date_from = '1/12/2021'
    date_to = '30/12/2022'
    stock_close_values = pd.DataFrame()
    
    """ Initialize stock. Default dates are from:
                        1/1/2021
                        1/1/2023
        User can choose to initialize form dataframe file (Pickle) by providing dataframe URL.
    """
    def __init__(self, name, from_date='2021-01-01', to_date='2022-01-01', df_file = None):
        self.stock_name = name
        self.date_from = from_date
        self.date_to = to_date
        self.initialize_stock_data(df_file)
        
    def initialize_stock_data(self, df_file):
        if not df_file:
            try:
                self.df = self.get_stock_data()
                print(self.df.head())
                self.stock_close_values = self.df['Close']
            except:
                print("Error retrieving initial stock data from yfinance.")
                sys.exit(1)
        else:
            try:
                self.df = pd.read_pickle(df_file)
                self.stock_close_values = self.df['Close']
            except:
                print("Error loading pandas DataFrame from file.")
                sys.exit(1)

    #### GET ####
    def get_stock_data(self):
        self.df = yf.download(self.stock_name, start=self.date_from, end=self.date_to)
        print(self.df.head)
        return self.df

    def get_moving_avg(self, range):
        mavg = self.stock_close_values.rolling(window=range).mean()
        return mavg
    
    def get_min_max(self, values):
        min = (np.diff(np.sign(np.diff(values))) > 0).nonzero()[0] + 1        # local min
        max = (np.diff(np.sign(np.diff(values))) < 0).nonzero()[0] + 1         # local max
        return min, max
    
    def get_gaussian_values(self, fwhm):
        sigma = fwhm / np.sqrt(8 * np.log(2))
        x_vals = np.arange(self.df.shape[0])
        y_vals = self.stock_close_values
        smoothed_vals = np.zeros(y_vals.shape)
        for x_position in x_vals:
            kernel = np.exp(-(x_vals - x_position) ** 2 / (2 * sigma ** 2))
            kernel = kernel / sum(kernel)
            smoothed_vals[x_position] = sum(y_vals * kernel)
        return smoothed_vals
    
    #### PLOT ####
    def show_plot(self):
        plt.legend()
        plt.show()
        
    def plot_stock(self):
        plt.plot(self.df.index, self.stock_close_values, label="Close")
    
    def plot_moving_avg(self, range):
        mavg = self.get_moving_avg(range)
        plt.plot(self.df.index, mavg, label="Mavg-%d" % (range))

    """ Plots min and max of a set of data points against the dates.
        values = data points to plot min/max. Default is close values, but can be Gaussian, for example."""
    def plot_min_max(self, values = None):
        if values is None: 
            values = self.stock_close_values
            print("Plotting close values")
        min, max = self.get_min_max(values)
        x = self.df.index
        plt.plot(x, values, color='grey')
        plt.plot(x[min], values[min], "o", markersize =6, label="min", color='r')
        plt.plot(x[max], values[max], "o", markersize =6, label="max", color='b')
    
    def plot_gaussian(self, fwhm):
        gaussian = self.get_gaussian_values(fwhm)
        plt.plot(self.df.index, gaussian, label="Gaussian-%d" %(fwhm))
        
    ### SAVES ###
    """ Saves stock data in pandas dataframe."""
    def save_data(self, file_path=None):
        if file_path:
            self.df.to_pickle(file_path)
        else:
            self.df.to_pickle("./{}.pkl".format(self.stock_name))