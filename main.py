# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 19:05:20 2021
@author: Vicky Chen
This Code appl
"""

import matplotlib.pyplot as plt
from drs4 import DRS4BinaryFile
import numpy as np
from scipy.signal import find_peaks
import sys
import os
import csv

def extractdata(f, channel_list):    
    i = 1
    tempdata_list1 = []  
    tempdata_list2 = [] 
    tempdata_list3 = [] 
    tempdata_list4 = [] 
    
    data_ID1 = []
    data_ID2 = []
    data_ID3 = []
    data_ID4 = []
    
    data_time1 = []
    data_time2 = []
    data_time3 = []
    data_time4 = []
    
    data = []
    data_ch1 = []   
    data_ch2 = [] 
    data_ch3 = [] 
    data_ch4 = [] 
    
    while i == 1:      
        #Iterates through the lines of the binary file, Adds "stop" as default
        #value to stop the iteration at the end of the binary file
        event = next(f, "stop")
       
        if event == "stop":
            break
        
        else:
            #Getting the Datapoint of all 4 channels for the current line of
            #the binary file
            for i, channel in enumerate(channel_list):
                if channel == 1:
                    tempdata_list1.append(event.adc_data[boardID][channel]) 
                    list_length = len(tempdata_list1)
                    data_ID1.append(event.event_id)
                    data_time1.append(event.timestamp)                        
                    
                    data_ch1 = {
                        "data": tempdata_list1, 
                        "identity": data_ID1, 
                        "time": data_time1
                        } 
                    
                elif channel == 2:
                    tempdata_list2.append(event.adc_data[boardID][channel]) 
                    list_length = len(tempdata_list2)
                    data_ID2.append(event.event_id)
                    data_time2.append(event.timestamp)                        
                    
                    data_ch2 = {
                        "data": tempdata_list2, 
                        "identity": data_ID2, 
                        "time": data_time2
                        } 
                    
                elif channel == 3:
                    tempdata_list3.append(event.adc_data[boardID][channel]) 
                    list_length = len(tempdata_list3)
                    data_ID3.append(event.event_id)
                    data_time3.append(event.timestamp)                        
                    
                    data_ch3 = {
                        "data": tempdata_list3, 
                        "identity": data_ID3, 
                        "time": data_time3
                        }                 
                    
                elif channel == 4:
                    tempdata_list4.append(event.adc_data[boardID][channel])
                    list_length = len(tempdata_list4)
                    data_ID4.append(event.event_id)
                    data_time4.append(event.timestamp)                        
                    
                    data_ch4 = {
                        "data": tempdata_list4, 
                        "identity": data_ID4, 
                        "time": data_time4
                        }                 
                    
            #Saving the data of all 4 channels into one dictionary                
            data = {
                "ch1": data_ch1, 
                "ch2": data_ch2, 
                "ch3": data_ch3, 
                "ch4": data_ch4
                }         
               
    return data
            

#This function finds the maximum of the 1024 cells of each data point
def maxvalue(tempdata):
    maxima = []
    for i in range(len(tempdata)):
        maxvalue = np.amax(tempdata[i])
        maxima.append(maxvalue)
    return maxima


#This scales the x-axis to display the Energy in keV
#I recommend calibrating your board and adjusting the values in this function 
#STILL UNDER CONSTRUCTION!
def scaleaxis(x): 
    channel = x
    maxenergy = []
    for i in range(len(channel)):
        
        energy = (434/7563)* channel[i] - 5501.59
        maxenergy.append(energy)
    return maxenergy


#Finding the peaks of the histogram, This will be used to scale the x-axis
#UNDER CONSTRUCTION!!!
def peakposition(x): 
    peaks, _ = find_peaks(x, prominence=10)
    
    plt.plot(peaks, x[peaks], "xr"); plt.plot(x)
    plt.yscale('log')
    plt.show()
    return peaks


#Plots the data into a histogram with the option to save the plot and
#data of the histogram
def histogram(maxima, bins, title, xtitle):
    
    #step 2: saving the histogram data
    save = input("Do you want to save the plot and data of the histogram? "
                 + "'yes' or 'no': ")
    
    if save == 'yes':
        
        #Asks filepath from user
        dir_input = input("Enter the desired directory for your file: ")
        filename = input("enter a filename (without .*) ")
        pngfile = filename + '.png'
        filepathpng = "{}{}{}".format(dir_input, os.sep, pngfile)
        filepathpng = os.sep.join([dir_input, pngfile])
        
        textfile = filename + '.txt'
        filepathtext = "{}{}{}".format(dir_input, os.sep, textfile)
        filepathtext = os.sep.join([dir_input, textfile])
        
        #Plotting the histogram
        plt.title(title)
        plt.xlabel(xtitle)
        plt.ylabel("Counts")
        plt.hist(maxima[::-1],bins=bins)
        
        ax = plt.gca()
        p = ax.patches
        energy = [patch.get_xy() for patch in p]
        counts = [patch.get_height() for patch in p]    
        hist_data = {"energy": energy, "counts": counts}
        
        plt.yscale('log')
        
        #Saving the Plot as a .png
        plt.savefig(filepathpng)
        plt.show()
        
        
        #Saving the histogram data to a text file       
        tupleenergy = hist_data["energy"]
        energy =[]
        
        for i in range(len(tupleenergy)):
            energy.append(tupleenergy[i][0])
            
        hist_data["energy"] = energy
        width = 20
        delim='\t'
        column1 = '-'
        order = ['energy', 'counts']
        
        with open( filepathtext, 'w' ) as f:
            writer, w = csv.writer(f, delimiter=delim), []
            head = ['{!s:{}}'.format(column1,width)]
            
            for i in order:    
                head.append('{!s:{}}'.format(i,width))
                
            writer.writerow(head)            
            
            for i in range(len(tupleenergy)):
                row = ['{!s:{}}'.format(i,width)]
                for k in order:
                    temp = hist_data[k][i]
                    row.append('{!s:{}}'.format(temp,width))
        
                writer.writerow(row)
        
        print("your data has been saved! ")
        
    else:
        plt.title(title)
        plt.xlabel(xtitle)
        plt.ylabel("Counts")
        plt.hist(maxima[::-1],bins=bins)
        
        ax = plt.gca()
        p = ax.patches
        energy = [patch.get_xy() for patch in p]
        counts = [patch.get_height() for patch in p]    
        hist_data = {"energy": energy, "counts": counts}
        
        plt.yscale('log')
        plt.show()
        
        
    return hist_data


#Saving the data of one channel into a text file
#instead of saving all 1024 count of each data point only the maximum will 
#be saved for each data point
def save_data(data, maxima, channel):
    
    dir_input = input("Enter the desired directory for your file: ")
    filename = input("enter a filename (without .*)")    
    textfile = filename + '.txt'
    filepathtext = "{}{}{}".format(dir_input, os.sep, textfile)
    filepathtext = os.sep.join([dir_input, textfile])
    
    
    data = data[channel]
    
    temp =  {
        "maxima":
        "identity"
        "timestamp"
        }
    data["data"] = maxima
    
    temp["maxima"] = data["data"]
    temp["identity"] = data["identity"]
    temp["timestamp"] = data["time"]
    
    data = temp
    
    width = 20
    delim='\t'
    column1 = channel
    order = ['maxima', 'identity', 'timestamp']
    
    with open( filepathtext, 'w' ) as f:
        writer, w = csv.writer(f, delimiter=delim), []
        head = ['{!s:{}}'.format(column1,width)]
        
        for i in order:    
            head.append('{!s:{}}'.format(i,width))
            
        writer.writerow(head)            
        
        for i in range(len(data["identity"])):
            row = ['{!s:{}}'.format(i,width)]
            for k in order:
                temp = data[k][i]
                row.append('{!s:{}}'.format(temp,width))
    
            writer.writerow(row)
    
    print("your data has been saved! ")
    
##############################################################################    
#End of function definition
##############################################################################

#If getting the directory through console input is desired, uncomment the
#following lines. Note: This has only been tested on windows
# dir_input = input("Enter the directory of your File: ")
# filename = input("Enter the name of the file (with .bin): ")
# filepath = "{}{}{}".format(dir_input, os.sep, filename)
# filepath = os.sep.join([dir_input, filename])


#Alternatively you can directly input your filepath in the following line
#Make sure to comment out this line if you wish to input your filepath
#through the console. The following line will otherwise overwrite the
#input filepath: NOTE: use / as seperators
filepath = 'C:/Users/vicky/Desktop/PALS-DRS4-Pydrs-main/tests/2channels.bin'

#the filepath will be printed so you can check that the registered filepath
#is correct
print(filepath)

##############################################################################
#Opening the file
with DRS4BinaryFile(filepath) as f:
    
    print(f.board_ids)
    print(f.channels)
    boardID_list = f.board_ids
    boardID = boardID_list[0]
    totalBoards = len(boardID_list)
    boardID = boardID_list[0]
    boardCH = f.channels[boardID]
    data = extractdata(f, boardCH) 
    i = 1
    
    while i == 1:
        print("You have connected ", totalBoards, 
              "Board(s) with Channel(s)", boardCH )

        ch_opt = []
        channel = input("Choose between 'ch1','ch2','ch3','ch4': ")
        print("You have selected channel: ", channel)
        temp_data = data[channel]
        
        x=1
        while x == 1:
            operations = ['histogram', 'save data', 'select channel', 'finish']
            print("Caution: If next_channel or finish are selected current "
                  + "data can be overwritten and data might be lost!")
            print("Available operations: ", operations)
            command = input("choose an operation: ")
            
            if command == 'select channel':
                print('you chose select channel')   
                break     
            
            elif command == 'histogram':
                print('you chose histogram')
                title = input("choose a title for your plot: ")
                bins = int(input("choose the number of binaries: "))

                
                baseline = 34000
                
                data_corr = -np.array(temp_data['data'])+2*baseline
                maxcounts = maxvalue(data_corr)
                
                hist_data = histogram(maxcounts, bins, title, 'channel')
                

                    
            elif command == 'save data':
                print('you chose save_data')
                baseline = 34000
                data_corr = -np.array(temp_data['data'])+2*baseline
                maxcounts = maxvalue(data_corr)
                save_data(data, maxcounts, channel)
                
            elif command == 'finish':
                print('the program will be closed')   
                break
                
            else:
                print("invalid syntax")

                    
        if command == 'finish':
            break       
    
    



