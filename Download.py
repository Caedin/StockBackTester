'''
Created on Aug 1, 2014

@author: Keith
'''
import os
from pandas.io.data import DataReader
from datetime import datetime
from multiprocessing import Queue
from threading import Thread
import threading


queue = Queue()
today = datetime.today()
last_year = datetime(today.year-2, today.month, today.day)
folder = 'stocks_old'

def download_data(symbols):

    for symbol in symbols:
        queue.put(symbol)
  
    threads = []
    while(queue.qsize()>0):
        while(len(threading.enumerate())<100):
            if queue.empty()==False:
                func = download_url
                thread = Thread(target= func)
                thread.daemon =True
                thread.start()
                threads.append(thread)
            else:
                break

    
    for thread in threads:
        thread.join()

def download_url():
    symbol = queue.get()
    try:
        data = DataReader(symbol, "yahoo", last_year, today)
    except:
        print 'Yahoo has no data for ' + symbol
        return
    try:
        os.mkdir('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+folder+'/'+symbol)
    except:
        print 'Unable to create folder for ' + symbol
        return
    try:
        data.to_csv('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+folder+'/'+symbol+'/'+symbol+'.csv')
    except:
        print 'Unable to download data for ' + symbol
        return

    return




if __name__ == '__main__':
    download_data()
    
    