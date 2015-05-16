'''
Created on March, 21 2014

@author: Keith Dyer
'''


import itertools
import time

from multiprocessing import Queue
import multiprocessing

from Daily_Evaluation import daily_evaluator
from Update_Data import update_data


def main():
    
    #Update the data base with fresh data before doing the daily calculations
    start_time = time.time()
    print 'Updating the Data Base'
    
    
    updater = update_data()
    updater.update_process()
    
    
    print '\tComplete:\t'+str(time.time()-start_time)
    
    
    start_time = time.time()
    print 'Calculating Daily Processes'
        
    #strategy = binseq(8)
    #strategy = ['00000000y']
    strategy = ['00000100']
    
    num_process = min(len(strategy), multiprocessing.cpu_count())
    processes = []
    
    queue = Queue()
    
    for x in xrange(1):
        for j in strategy:
            queue.put(j)
        
    for i in xrange(8):
        worker = daily_evaluator(queue)
        worker.daemon = True
        processes.append(worker)
        worker.start()
        time.sleep(1)
        
    for x in xrange(num_process):
        queue.put(None)
    
    
    for proc in processes:
        proc.join()
    
    print '\tComplete:\t'+str(time.time()-start_time)
    

def binseq(k):
    return [''.join(x) for x in itertools.product('01', repeat=k)]


    
if  __name__ == '__main__':
    main()