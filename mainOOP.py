# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:51:44 2022

@author: Vicky Chen
This program is based on pydrs by TU Dortmund
and used read_binary.ccp of DRS_507 by Steffan Ritt as reference

The Purpose of this program is to read out the binary file that you get from
the DRS4 Board through the digital oscilloscope in order to calculate the
lifetime of positrons.
This programm only works for the use of two detectors connected to input
channels 1 and 2!
"""

import matplotlib.pyplot as plt
from drs4 import DRS4BinaryFile
import numpy as np
from scipy.signal import find_peaks
import sys
import os
import csv
import pandas as pd


class PALS_Event:
    def __init__(self, pulse, identity, timestamp, triggercell, maximum, 
                 maxindex):
        self.pulse = pulse
        self.identity = identity
        self.timestamp = timestamp
        self.triggercell = triggercell
        self.maximum = maximum
        self.maxindex = maxindex
        
    def show_waveform(self, labels):
        
        plt.plot(self.pulse)
        plt.legend(labels)
        
        plt.title('Unedited Pulses')
        plt.xlabel('Number of Sample Cell []')
        
#---------------------------Functions------------------------------------------
        

#---------------------------reading binary file--------------------------------

def getboardID(f):
    boardID_list = f.board_ids
    
    ###this is only valid for the use of 1 Board only
    boardID = boardID_list[0]
    return boardID


def extractdata(f, slope1, slope2, intercept1, intercept2):    
    i = 1
    boardID = getboardID(f)
    board_channels = f.channels[boardID]
    ch1_list = []
    ch2_list = []
        
    while i == 1:      
        #Iterates through the lines of the binary file, Adds "stop" as default
        #value to stop the iteration at the end of the binary file
        event = next(f, "stop")      
              
        if event == "stop":
            break
        
        else:
            #Getting the Datapoint of input 1 and 2 for the current line of
            #the binary file
                     
            for i, channel in enumerate(board_channels):
                if channel == 1:
                    eventi = create_event(boardID, channel, event, slope1, 
                                          slope2, intercept1, intercept2)
                    ch1_list.append(eventi)
                    
                elif channel == 2:
                    eventi = create_event(boardID, channel, event, slope1, 
                                          slope2, intercept1, intercept2)
                    ch2_list.append(eventi)
                                          
            
    return ch1_list, ch2_list


def create_event(boardID, channel, event, slope1, slope2, intercept1, 
                 intercept2):
    pulse = event.adc_data[boardID][channel]
    identity = event.event_id
    timestamp = event.timestamp                   
    triggercell = event.trigger_cells[boardID]
    
    maximum = get_maxvalue(pulse, channel, slope1, slope2, intercept1, 
                           intercept2)
    maxindex = get_index_maxvalue(pulse)                   
    #rangectr = event.range_center
    eventi = PALS_Event(pulse, identity, timestamp, triggercell, 
                      maximum, maxindex)
       
    return eventi


def get_maxvalue(pulse, channel, slope1, slope2, intercept1, 
                       intercept2):
    #inverts the pulse of the board
    baseline = 33400
    pulse_corr = -pulse +1*baseline
    maximum = np.amax(pulse_corr)
    
    # plt.plot(pulse_corr)
    # plt.ylim(-300, maximum+200)
    # plt.show()
    
    #returns max value of the pulse
    
    if channel == 1:
        maxvalue_keV = maximum*slope1 + intercept1
        
    elif channel == 2:
        maxvalue_keV = maximum*slope2 + intercept2

    
    #converts max value to represent keV
    # slope = 759/13538.32
    # intercept = -5634.612
    # maxvalue_keV = maximum*slope + intercept
    
    return maxvalue_keV

                  
def get_index_maxvalue(pulse):
    index = np.where(pulse == np.amax(pulse))
    index = index[0]
    index = index[0]
    return index

#---------------------------Start-Stop-Signals---------------------------------

def frequency_discriminator(channel_list):
    start = []
    stop = []
    maxima = []
    for i in range(len(channel_list)):
        maxima.append(channel_list[i].maximum)
        if channel_list[i].maximum>1265 and channel_list[i].maximum<1285:
            start.append(channel_list[i])
            
        elif channel_list[i].maximum>501 and channel_list[i].maximum<521:
            stop.append(channel_list[i])
            
    return start, stop

def getcelltime(Event, channel, index):
    
    if channel == 1:    
        timewidths = f.time_widths
        t_binwidth = timewidths[3059]
        t_binwidth = t_binwidth[1]
        t_binwidth = t_binwidth[0]
        
    elif channel == 2:
        timewidths = f.time_widths
        t_binwidth = timewidths[3059]
        t_binwidth = t_binwidth[2]
        t_binwidth = t_binwidth[0]
        
     
    i = index
    j = 0    
    tch_i = 0
    
    while j < i:
        
        #Equation 5.1 in Masterthesis
        tch_i = tch_i + t_binwidth*((j + Event.triggercell)%1024)
        
        j += 1
    
    return tch_i

def allignchannels(Event, channel):
    
    #Equation 5.2 in Masterthesis
    index = (1024 - Event.triggercell)%1024
    tch_0  = getcelltime(Event, channel, index)
    
    #alligning the channels: Euation 5.3 in Masterthesis
    
    
    pass

def get_pair_candidates(startlist, stoplist):
    candidate_pairs = []
    
    for i in range(len(startlist)):
        
        
        starttime = startlist[i].timestamp
        startindex = startlist[i].maxindex
        
        for j in range(len(stoplist)):
             stoptime = stoplist[j].timestamp
             stopindex = stoplist[j].maxindex
             
             if starttime == stoptime and stopindex>startindex:
                 pair = [startlist[i], stoplist[j]]
                 candidate_pairs.append(pair)
    
    return candidate_pairs
    
def create_histogram(Event_list, title):
    maxima = []
    for i in range(len(Event_list)):
        maxima.append(Event_list[i].maximum)
        
    histogram_peaks(maxima, title)    
    
    pass
        
#--------------------keV-CALLIBRATION------------------------------------------

def extractdata_init(f):    
    i = 1
    boardID = getboardID(f)
    board_channels = f.channels[boardID]
    ch1_list = []
    ch2_list = []
        
    while i == 1:      
        #Iterates through the lines of the binary file, Adds "stop" as default
        #value to stop the iteration at the end of the binary file
        event = next(f, "stop")      
              
        if event == "stop":
            break
        
        else:
            #Getting the Datapoint of input 1 and 2 for the current line of
            #the binary file
                     
            for i, channel in enumerate(board_channels):
                if channel == 1:
                    eventi = create_event_init(boardID, channel, event)
                    ch1_list.append(eventi)
                    
                elif channel == 2:
                    eventi = create_event_init(boardID, channel, event)
                    ch2_list.append(eventi)
                                          
            
    return ch1_list, ch2_list    
   
   
def create_event_init(boardID, channel, event):
    pulse = event.adc_data[boardID][channel]
    identity = event.event_id
    timestamp = event.timestamp                   
    triggercell = event.trigger_cells[boardID]
    
    maximum = get_maxvalue_init(pulse, channel)
    maxindex = get_index_maxvalue(pulse)                   
    #rangectr = event.range_center
    eventi = PALS_Event(pulse, identity, timestamp, triggercell, 
                      maximum, maxindex)
       
    return eventi   


def get_maxvalue_init(pulse, channel):
    #inverts the pulse of the board
    baseline = 34000
    pulse_corr = -pulse +2*baseline
    maximum = np.amax(pulse_corr)
    
    # plt.plot(pulse_corr)
    # plt.ylim(-300, maximum+200)
    # plt.show()
    
    #returns max value of the pulse
    

    
    #converts max value to represent keV
    # slope = 759/13538.32
    # intercept = -5634.612
    # maxvalue_keV = maximum*slope + intercept
    
    return maximum


def configure_keV_conversion_ch1(data):
    maxcounts = []

    
    for i in range(len(data[0])):
        maxcounts.append(data[0][i].maximum)
        
    peaks = histogram_peaks(maxcounts, "Channel 1")
    
    return peaks 


def configure_keV_conversion_ch2(data):
    maxcounts = []
    for i in range(len(data[1])):
        maxcounts.append(data[1][i].maximum) 
        
    peaks = histogram_peaks(maxcounts, "Channel 2")
    
    return peaks
        
   
def histogram_peaks(maxcounts, title):
    
    plt.hist(maxcounts[::-1],bins=300)
    ax = plt.gca()
    p = ax.patches
    plt.yscale('log')
    
    energy = [patch.get_xy() for patch in p]
    for i in range(len(energy)):
        temp_tuple = energy[i]
        temp_float = temp_tuple[0]
        
        energy[i] = temp_float
        
    arr_energy = np.array(energy)    
    counts = [patch.get_height() for patch in p]
    arr_counts = np.array(counts)
    hist_data = {"energy": arr_energy, "counts": arr_counts}

    plt.show()
    
    peaks, _ = find_peaks(arr_counts, prominence=40)
    plt.plot(arr_energy[peaks], arr_counts[peaks], "xr")
    plt.hist(maxcounts[::-1],bins=300)
    plt.yscale('log')
    
    plt.title(title)
    
    plt.xlabel("'Energy' as 2-Byte integers []")
    plt.ylabel("Counts []")
    plt.show()
    
    return peaks, arr_energy


def get_keV_conversion_ch1(data):
    
    tuple_peaks = configure_keV_conversion_ch1(data)
    peaks = tuple_peaks[0]
    arr_energy = tuple_peaks[1]
    #returns in which binary the 511 keV peak is
    #adjust the number of peak according to your current histogram!
    binary = peaks[4]
    #gives the corresponding integer of the 511 peak
    peak_511 = arr_energy[binary]
    
    #returns in which binary the 1274 keV peak is
    #adjust the number of peak according to your current histogram!
    binary = peaks[7]
    #gives the corresponding integer of the 511 peak
    peak_1274 = arr_energy[binary]
    
    parameters = get_conversion_parameters(peak_511, peak_1274)
    return parameters
    

def get_keV_conversion_ch2(data):
    
    tuple_peaks = configure_keV_conversion_ch2(data)
    peaks = tuple_peaks[0]
    arr_energy = tuple_peaks[1]
    #returns in which binary the 511 keV peak is
    #adjust the number of peak according to your current histogram!
    binary = peaks[3]
    #gives the corresponding integer of the 511 peak
    peak_511 = arr_energy[binary]
    
    #returns in which binary the 1274 keV peak is
    #adjust the number of peak according to your current histogram!
    binary = peaks[6]
    #gives the corresponding integer of the 511 peak
    peak_1274 = arr_energy[binary]
    parameters = get_conversion_parameters(peak_511, peak_1274)
    return parameters
    
    
def get_conversion_parameters(peak_511, peak_1274):
    
    delta_E_keV = 1274 - 511 
    delta_E_int = peak_1274 - peak_511
    slope = delta_E_keV/delta_E_int
    
    intersect_511 = 511 - slope*peak_511
    intersect_1274 = 1274 - slope*peak_1274
    
    intersect = (intersect_1274+intersect_511)/2
    
    return slope, intersect

#--------------------End of Funtions------------------------------------------

filepath = 'C:/Users/Vicky/Desktop/PALS-DRS4-Pydrs-main/tests/2ch100k.bin'

#the filepath will be printed so you can check that the registered filepath
#is correct
print(filepath)

##############################################################################
#Opening the file
with DRS4BinaryFile(filepath) as f:
    
    
    
    """
    calibrate slope and intercept to your needs by calling these functions
    for the callibration the line data = extractdata(f) must be put in front
    of this part!!!
    """
    
    # data = extractdata_init(f)
    # parameters1 = get_keV_conversion_ch1(data)
    # parameters2 = get_keV_conversion_ch2(data)
    
    ##########adjust the parameters here#######################################
    slope1 = 0.05689266151774411
    intercept1 = -29.975819500388752
    slope2 = 0.034948443030831576
    intercept2 = 109.33754424665267
    """
    end of callibration
    """
    data = extractdata(f, slope1, slope2, intercept1, intercept2)
    
    
    create_histogram(data[0], "channel1")
    create_histogram(data[1], "channel2")
    ch1_signals = frequency_discriminator(data[0])
    ch1_start = ch1_signals[0]
    ch1_stop = ch1_signals[1]
    del ch1_signals
    
    ch2_signals = frequency_discriminator(data[1])
    ch2_start = ch2_signals[0]
    ch2_stop = ch2_signals[1]
    del ch2_signals
    
    celltime = getcelltime(ch1_start[0], 1, ch1_start[0].maxindex)
    
    candidates1 = get_pair_candidates(ch1_start, ch2_stop)
    candidates2 = get_pair_candidates(ch2_start, ch1_stop)
    
    # labels = ["Start 1", "Stop 1", "Start 2", "Stop 2"]
    # ch1_start[0].show_waveform(labels)
    # ch1_stop[0].show_waveform(labels)
    # ch1_start[37].show_waveform(labels)
    # ch1_stop[37].show_waveform(labels)
    