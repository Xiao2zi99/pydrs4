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


class Ereignis:
    def __init__(self, pulse, identity, timestamp, triggercell, maximum, maxindex):
        self.pulse = pulse
        self.identity = identity
        self.timestamp = timestamp
        self.triggercell = triggercell
        self.maximum = maximum
        self.maxindex = maxindex
        
    def show_waveform(self):
        plt.plot(self.pulse)
        
def getboardID(f):
    boardID_list = f.board_ids
    
    ###this is only valid for the use of 1 Board only
    boardID = boardID_list[0]
    return boardID
      
def extractdata(f):    
    i = 1
    boardID = getboardID(f)
    board_channels = f.channels[boardID]
    
    ch1_list = []
    ch2_list = []
    ch3_list = []
    ch4_list = []
        
    while i == 1:      
        #Iterates through the lines of the binary file, Adds "stop" as default
        #value to stop the iteration at the end of the binary file
        event = next(f, "stop")      
              
        if event == "stop":
            break
        
        else:
            #Getting the Datapoint of all 4 channels for the current line of
            #the binary file
            """
            scalers don't work but for now are also not relevant
            """             
            #scalers = event.scalers[boardID]
            
            for i, channel in enumerate(board_channels):
                if channel == 1:
                    eventi = create_event(boardID, channel, event)
                    ch1_list.append(eventi)
                    
                elif channel == 2:
                    eventi = create_event(boardID, channel, event)
                    ch2_list.append(eventi)
                """
                Uncomment the followin lines if more than  2 channels are used
                and adjust the dataframe accordingly
                """
                # elif channel == 3:
                #     eventi = create_event(boardID, channel, event)
                #     ch3_list.append(eventi)                
                    
                # elif channel == 4:
                #     eventi = create_event(boardID, channel, event)
                #     ch4_list.append(eventi)                
                    
            #Saving the data of all 4 channels into one dictionary                
    
        
            
    return ch1_list, ch2_list

def create_event(boardID, channel, event):
    pulse = event.adc_data[boardID][channel]
    identity = event.event_id
    timestamp = event.timestamp                   
    triggercell = event.trigger_cells[boardID]
    
    maximum = get_maxvalue(pulse)
    maxindex = get_index_maxvalue(pulse)
    #scaler1 = scalers[channel]                    
    #rangectr = event.range_center
    
    eventi = Ereignis(pulse, identity, timestamp, triggercell, maximum, maxindex)
       
    return eventi

def get_maxvalue(pulse):
    #inverts the pulse of the board
    baseline = 34000
    pulse_corr = -pulse +2*baseline
    
    #returns max value of the pulse
    maximum = np.amax(pulse_corr)
    
    #converts max value to represent keV
    slope = 759/13538.32
    intercept = -5634.612
    maxvalue_keV = maximum*slope + intercept
    
    return maxvalue_keV
                  
def get_index_maxvalue(pulse):
    index = np.where(pulse == np.amax(pulse))
    index = index[0]
    index = index[0]
    return index

def frequency_discriminator(channel_list):
    start = []
    stop = []
    
    for i in range(len(channel_list)):
        if channel_list[i].maximum>1260 and channel_list[i].maximum<1280:
            start.append(channel_list[i])
            
        elif channel_list[i].maximum>500 and channel_list[i].maximum<520:
            stop.append(channel_list[i])
            
    return start, stop

filepath = 'C:/Users/Vicky/Desktop/PALS-DRS4-Pydrs-main/tests/2ch100k.bin'

#the filepath will be printed so you can check that the registered filepath
#is correct
print(filepath)

##############################################################################
#Opening the file
with DRS4BinaryFile(filepath) as f:
    
    data = extractdata(f)
    ch1_signals = frequency_discriminator(data[0])
    ch1_start = ch1_signals[0]
    ch1_stop = ch1_signals[1]
    del ch1_signals
    
    ch2_signals = frequency_discriminator(data[1])
    ch2_start = ch2_signals[0]
    ch2_stop = ch2_signals[1]
    del ch2_signals
    
    ch1_start[0].show_waveform()
    ch1_stop[0].show_waveform()
    ch1_start[37].show_waveform()
    ch1_stop[37].show_waveform()
    