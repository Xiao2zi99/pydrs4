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

def welcomemsg(f):
    print("Welcome!")
    totalboards = f.num_boards
    board_channels = getboardchannel(f)
    print("You have connected ", totalboards, 
          "Board(s) with Channel(s)", board_channels )
    return None
    

def getboardID(f):
    boardID_list = f.board_ids
    
    ###this is only valid for the use of 1 Board only
    boardID = boardID_list[0]
    return boardID


def getboardchannel(f):
    boardID = getboardID(f)
    board_channels = f.channels[boardID]
    return board_channels
    

def extractdata(f):    
    i = 1
    boardID = getboardID(f)
    board_channels = f.channels[boardID]
    
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
    
    tcell1 = []
    tcell2 = []
    tcell3 = []
    tcell4 = []
    
    range1 = []
    range2 = []
    range3 = []
    range4 = []
    
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
            
            """
            scalers don't work but for now are also not relevant
            """
            
            #scalers = event.scalers[boardID]
            
            for i, channel in enumerate(board_channels):
                if channel == 1:
                    tempdata_list1.append(event.adc_data[boardID][channel]) 
                    list_length = len(tempdata_list1)
                    data_ID1.append(event.event_id)
                    data_time1.append(event.timestamp)                        
                    
                    #scaler1 = scalers[channel]
                    tcell1.append(event.trigger_cells[boardID])
                    range1.append(event.range_center)
                    
                    data_ch1 = {
                        "data": tempdata_list1, 
                        "identity": data_ID1, 
                        "time": data_time1,
                         "range center": range1,
                         "triggercell": tcell1
                        } 
                    
                elif channel == 2:
                    tempdata_list2.append(event.adc_data[boardID][channel]) 
                    list_length = len(tempdata_list2)
                    data_ID2.append(event.event_id)
                    data_time2.append(event.timestamp)                        
                    
                    #scaler2 = scalers[channel]
                    tcell2.append(event.trigger_cells[boardID])
                    range2.append(event.range_center)
                    
                    data_ch2 = {
                        "data": tempdata_list2, 
                        "identity": data_ID2, 
                        "time": data_time2,
                        "range center": range2,
                        "triggercell": tcell2
                        } 
                """
                Uncomment the followin lines if more than  2 channels are used
                """
                # elif channel == 3:
                #     tempdata_list3.append(event.adc_data[boardID][channel]) 
                #     list_length = len(tempdata_list3)
                #     data_ID3.append(event.event_id)
                #     data_time3.append(event.timestamp)  

                #     tcell3  = event.trigger_cells[boardID]
                #     range3 = event.range_center   
                    
                #     data_ch3 = {
                #         "data": tempdata_list3, 
                #         "identity": data_ID3, 
                #         "time": data_time3,
                #         "range center": range3,
                #         "scaler": scaler3,
                #         "triggercell": tcell3
                #         }                 
                    
                # elif channel == 4:
                #     tempdata_list4.append(event.adc_data[boardID][channel])
                #     list_length = len(tempdata_list4)
                #     data_ID4.append(event.event_id)
                #     data_time4.append(event.timestamp) 
                    
                #     tcell4  = event.trigger_cells[boardID]
                #     range4 = event.range_center                        
                    
                #     data_ch4 = {
                #         "data": tempdata_list4, 
                #         "identity": data_ID4, 
                #         "time": data_time4,
                #         "range center": range4,
                #         "scaler": scaler4,
                #         "triggercell": tcell4
                #         }                 
                    
            #Saving the data of all 4 channels into one dictionary                
            data = {
                "ch1": data_ch1, 
                "ch2": data_ch2, 
                "ch3": data_ch3, 
                "ch4": data_ch4
                }         
               
    return data
            

def getcelltime(data):
    
    
    ref_maxima = maxvalue(data, 'ch1')
    
    #getting the index of teh maxima for each datapoint
    
    n_maxima_ch1 = maxvalue_index(data, 'ch1')
    n_maxima_ch2 = maxvalue_index(data, 'ch2')
    
    arr_tcell = data['ch1']
    arr_tcell = arr_tcell['triggercell']

    
    timewidths = f.time_widths
    
    t_binwidth = timewidths[3059]
    t_binwidth1 = t_binwidth[1]
    t_binwidth1 = t_binwidth1[0]
    
    t_binwidth2 = t_binwidth[2]
    t_binwidth2 = t_binwidth2[0]
    
    #value correlates to time in nanoseconds
    arr_t_ch_i1 = []
    arr_t_ch_i2 = []
    
    for n,maximum in enumerate(n_maxima_ch1):
        
        maximum = 0
        j = 0
        t_ch_i1 = 0
        t_ch_i2 = 0
        
        while j < n_maxima_ch1[n]:
            
            t_ch_i1 =  t_ch_i1 + t_binwidth1 * ((j + arr_tcell[n])%1024)
            j += 1
            
        k = 0
        while k < n_maxima_ch2[n]:
            
            t_ch_i2 =  t_ch_i2 + t_binwidth2 * ((k + arr_tcell[n])%1024)
            k += 1
            
        arr_t_ch_i1.append(t_ch_i1)
        arr_t_ch_i2.append(t_ch_i2)
    #     n = 0
        
    pass
    
    
    #channel 1 will be used as the reference channel
    #t_max_reference = 
    
    #for count, maxim
    
    
def getstart(data):
    
    maxima_ch1 = maxvalue(data, 'ch1') 
    maxima_ch1 = keVconversion(maxima_ch1)
    maxima_ch2 = maxvalue(data, 'ch2')
    maxima_ch2 = keVconversion(maxima_ch2)
    
    # ch1 = get_temp_data(data, 'ch1')
    # ch2 = get_temp_data(data, 'ch2')
    
    startsignal_ch1 = frequencydiscriminator(maxima_ch1, 'start')
    startsignal_ch2 = frequencydiscriminator(maxima_ch2, 'start')

    
    
    return startsignal_ch1, startsignal_ch2


def getstop(data):
    
    maxima_ch1 = maxvalue(data, 'ch1') 
    maxima_ch1 = keVconversion(maxima_ch1)
    maxima_ch2 = maxvalue(data, 'ch2')
    maxima_ch2 = keVconversion(maxima_ch2)
    
    # ch1 = get_temp_data(data, 'ch1')
    # ch2 = get_temp_data(data, 'ch2')
    
    stopsignal_ch1 = frequencydiscriminator(maxima_ch1, 'stop')
    stopsignal_ch2 = frequencydiscriminator(maxima_ch2, 'stop')

    
    
    return stopsignal_ch1, stopsignal_ch2


def frequencydiscriminator(channel, typ):
    
    signal = []
    
    if typ == 'start':
        for index, value in enumerate(channel):
            
            if value>1260 and value<1280:
                signal.append(index)
                
    if typ == 'stop':  
        for index, value in enumerate(channel):
            
            if value>500 and value<520:
                signal.append(index)
                
    return signal


def datareduction(data):
    
    startsignals = getstart(data)
    
    stopsignals = getstop(data)
    
    ch1_start = getreduced_list(data, startsignals[0], 'ch1')
    ch1_stop = getreduced_list(data, stopsignals[0], 'ch1')
    ch2_start = getreduced_list(data, startsignals[1], 'ch2')
    ch2_stop = ch1_stop = getreduced_list(data, stopsignals[1], 'ch2')
    
    
    
    reduced_data =  {
        "ch1_start": ch1_start,
        "ch1_stop": ch1_stop,
        "ch2_start": ch2_start,
        "ch2_stop": ch2_stop        
        }
    
    return reduced_data
    
def getreduced_list(data, signal, selected_channel):
    
    maxima = maxvalue(data, selected_channel)
    maxima = keVconversion(maxima)
    
    reduced_list = {}
    
    channel_data = data[selected_channel]
    
    tempdata = channel_data['data']
    length = len(tempdata)
    identity = channel_data['identity']
    rangecenter = channel_data['range center']
    time = channel_data['time']
    triggercell = channel_data['triggercell']
    i = 0
    n = 0
    
    for i in range(length):
        if i == signal[n]:

            i += 1
            
            if n < len(signal)-1 :
                n += 1
            
        else:
            del tempdata[n]
            del identity[n]
            del rangecenter[n]
            del time[n]
            del triggercell[n]
            del maxima[n]
            i += 1
            
 
    reduced_list =  {
        "maxima": maxima, 
        "identity": identity, 
        "time": time,
        "range center": rangecenter,
        "triggercell": triggercell       
        }
    
    return reduced_list

def get_temp_data(data, selected_channel):
    temp_data = data[selected_channel]
    
    baseline = 34000
    temp_data_int = temp_data['data']
    data_corr = -np.array(temp_data_int)+2*baseline
    
    return data_corr

#This function finds the maximum of the 1024 cells of each data point
def maxvalue(data, selected_channel):
    
    temp_data = get_temp_data(data, selected_channel)

    maxcounts = []
    for i in range(len(temp_data)):
        maxvalue = np.amax(temp_data[i])
        maxcounts.append(maxvalue)
        
    
    return maxcounts

def maxvalue_index(data, selected_channel):
    
    temp_data = get_temp_data(data, selected_channel)
    
    index_maxima = []
    
    for i, temp_index in enumerate(temp_data):
        temp_index = np.where(temp_data[i] == np.amax(temp_data[i]))
        temp_index = temp_index[0]
        index_maxima.append(temp_index[0])
        
    return index_maxima


def maxvalue2(data):
    
    maxcounts = []
    for i in range(len(data)):
        maxvalue = np.amax(data[i])
        maxcounts.append(maxvalue)
        
    #maxcounts_keV = keVconversion(maxcounts)
    
    return maxcounts

def keVconversion (maxcounts):
    slope = 759/13538.32
    intercept = -5634.612
    maxcounts_keV = [(maxcounts[i]*slope + intercept) 
                     for i in range(len(maxcounts))]
    
    return maxcounts_keV
    
#finds the peaks of the historam so you can match it with te spectrum
#of your source and calculate the conversion to keV

def findpeaks(maxcounts): 
    
    plt.xlabel("Energy")
    plt.ylabel("Counts")
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

    #plt.show()
    
    peaks, _ = find_peaks(arr_counts, prominence=40)
    plt.plot(arr_energy[peaks], arr_counts[peaks], "xr")
    plt.hist(maxcounts[::-1],bins=300)
    plt.yscale('log')
    #plt.show()
    
    return peaks


def histogramtotxt(hist_data, filepath):
    width = 20
    delim='\t'
    column1 = '-'
    order = ['energy', 'counts']
    len_data = len(hist_data["counts"])
    with open( filepath, 'w' ) as f:
        writer, w = csv.writer(f, delimiter=delim), []
        head = ['{!s:{}}'.format(column1,width)]
        
        for i in order:    
            head.append('{!s:{}}'.format(i,width))
            
        writer.writerow(head)            
        
        for i in range(len_data):
            row = ['{!s:{}}'.format(i,width)]
            for k in order:
                temp = hist_data[k][i]
                row.append('{!s:{}}'.format(temp,width))
    
            writer.writerow(row)
    
    print("your data has been saved! ")
    
 

#Plots the data into a histogram with the option to save the plot and
#data of the histogram

def histogram(data, selected_channel):
    maxcounts = maxvalue(data, selected_channel)
    maxcounts_keV = keVconversion(maxcounts)
    title = input("choose a title for your plot: ")
    bins = int(input("choose the number of binaries: "))
    
    save = input("Do you want to save the plot and data of the histogram? "
                 + "'yes' or 'no': ")

    
    if save == 'yes':
        filepath = getfilepath()

        
    
    #creating histogram
    plt.title(title)
    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    #plt.hist(maxcounts_keV[::-1],bins=bins)
    plt.hist(maxcounts_keV,bins=bins)

    ax = plt.gca()
    p = ax.patches
    plt.yscale('log')
    
    #extracting data from histogram
    energy = [patch.get_xy() for patch in p]
    for i in range(len(energy)):
        temp_tuple = energy[i]
        temp_float = temp_tuple[0]
        
        energy[i] = temp_float
        
    arr_energy = np.array(energy)    
    counts = [patch.get_height() for patch in p]
    arr_counts = np.array(counts)    
    
    hist_data = {"energy": arr_energy, "counts": arr_counts}
    
    if save == 'yes':  
        
        #Saving the Plot as a .png
        path_png = filepath + ".png"
        plt.savefig(path_png)
        plt.show()
        
    
        #Saving the histogram data to a text file  
        path_txt = filepath + ".txt"
        histogramtotxt(hist_data, path_txt)
        
    else: plt.show();

        
        
    return hist_data


#Saving the data of one channel into a text file
#instead of saving all 1024 count of each data point only the maximum will 
#be saved for each data point

def save_data(data, selected_channel):
    
    filepath = getfilepath()  
    path_txt = filepath + ".txt"
    
    maxcounts = maxvalue(data, selected_channel)
    maxcounts_keV = keVconversion(maxcounts)
    data = data[selected_channel]
    
    temp =  {
        "maxcounts":
        "identity"
        "timestamp"
        }
    data["data"] = maxcounts_keV
    
    temp["maxcounts"] = data["data"]
    temp["identity"] = data["identity"]
    temp["timestamp"] = data["time"]
    
    data = temp
    
    width = 20
    delim='\t'
    column1 = selected_channel
    order = ['maxcounts', 'identity', 'timestamp']
    
    with open( path_txt, 'w' ) as f:
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
    return None


def select_channel():

    selected_channel = input("Choose between 'ch1','ch2','ch3','ch4': ")
    print("You have selected channel: ", selected_channel)
    
    if selected_channel == 'ch1' or selected_channel == 'ch2' or selected_channel == 'ch3' or selected_channel == 'ch4':
        return selected_channel
    
    else:
        print("Invalid input. Please check your spelling!")
        select_channel()
        

def select_operation():
    selected_channel = select_channel()
    x=1
    while x == 1:
        operations = ['histogram', 'save data', 'select channel', 'finish']
        print("Caution: If next_channel or finish are selected current "
              + "data can be overwritten and data might be lost!")
        print("Available operations: ", operations)
        command = input("choose an operation: ")
        
        if command == 'select channel':
            print('you chose select channel')
            select_channel()
            break     
        
        elif command == 'histogram':
            print('you chose histogram')
            histogram(data, selected_channel)
            
        elif command == 'save data':
            print('you chose save_data')
            save_data(data, selected_channel)
            
        elif command == 'finish':
            print('the program will be closed')   
            break
            
        else:
            print("invalid syntax")

def getfilepath(): 
    dir_input = input("Enter the directory of your File: ")
    filename = input("Enter the name of the file (with .*): ")
    filepath = "{}{}{}".format(dir_input, os.sep, filename)
    filepath = os.sep.join([dir_input, filename])      
    return filepath
    
##############################################################################    
#End of function definition
##############################################################################

#If getting the directory through console input is desired, uncomment the
#following lines. Note: This has only been tested on windows 10
#filepath = getfilepath()

#Alternatively you can directly input your filepath in the following line
#Make sure to comment out this line if you wish to input your filepath
#through the console. The following line will otherwise overwrite the
#input filepath: NOTE: use / as seperators
filepath = 'C:/Users/Vicky/Desktop/PALS-DRS4-Pydrs-main/tests/2ch100k.bin'

#the filepath will be printed so you can check that the registered filepath
#is correct
print(filepath)

##############################################################################
#Opening the file
with DRS4BinaryFile(filepath) as f:
    
    
    peeksize = f.peek()
    # timewidths = f.time_widths
   
    
   
 

    
    welcomemsg(f)
    binwidth = f.time_widths
    data = extractdata(f)   
    
    reduced_data = datareduction(data)
    
    del data
    
    #getcelltime(data)   
  
    
        
    #select_operation()
    
    
    



