'''
Created on Jul 18, 2014

@author: Keith
'''

import os
import urllib
import csv
import shutil
import math
import time
from collections import deque
from multiprocessing import Process, Queue
import multiprocessing
import Download


class update_data():
    
    asset_type = 'stocks'
    folder = 'stocks_old'
    
    def update_process(self):
        if self.asset_type == 'stocks':
            startTime = time.time()
            print '\tReading in Stock List'
            
            temp = []
            
            with open('NYSE.csv', 'r') as f:
                for line in f:
                    line = line.replace('"',"").strip()
                    line = line.replace(' ',"").strip()
                    spl =line.split(',')
                    temp.append(spl[0])
            with open('NASDAQ.csv', 'r') as f:
                for line in f:
                    line = line.replace('"',"").strip()
                    line = line.replace(' ',"").strip()
                    spl =line.split(',')
                    temp.append(spl[0])
            with open('AMEX.csv', 'r') as f:
                for line in f:
                    line = line.replace('"',"").strip()
                    line = line.replace(' ',"").strip()
                    spl =line.split(',')
                    temp.append(spl[0])
            '''
            with open('ETF_STOCKS.txt', 'r') as f:
                for line in f:
                    line = line.replace('"',"").strip()
                    line = line.replace(' ',"").strip()
                    spl =line.split(',')
                    temp.append(spl[0])
			'''
                
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            symbols = set(temp)
            
            if os.path.isfile('exceptionFile.csv'):
                with open('exceptionFile.csv','rb') as exception_file:
                    for line in exception_file:
                        line = line.strip()
                        if line in symbols:
                            symbols.remove(line)
        
            
            startTime = time.time()
            print '\tDownloading Data'
            
            try:
                shutil.rmtree('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder)
            except:
                print '\t\t\tUnable to delete old stock data!'
                pass
            time.sleep(1)
            try:
                os.mkdir('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'')
            except:
                print '\t\t\tUnable to create stocks_old folder!'
                pass
            
            Download.download_data(symbols)
           
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            #Update data
            startTime = time.time()
            print '\tProcessing Data'
            
            num_cpus = multiprocessing.cpu_count()
            threads = []
            self.update_queue = Queue()
            for k in symbols:
                self.update_queue.put(k)
            
            for k in xrange(num_cpus):
                try:
                    p = Process(target=self.process_updates, args=(self.update_queue, ))
                    threads.append(p)
                except IOError:
                    pass
                
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()     
            
            
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            startTime = time.time()
            print '\tDeriving New Data'
            
            num_cpus = multiprocessing.cpu_count()
            
            threads = []
            self.derive_queue = Queue()
            for k in symbols:
                self.derive_queue.put(k)
            
            for k in xrange(num_cpus):
                p = Process(target=self.derive, args=(self.derive_queue, ))
                threads.append(p)
                    
                
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()     
            
        
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            startTime = time.time()
            print '\tCreating Exceptions List'
            
            '''
            self.symbol_queue = []
            self.exceptions_queue = []
            for k in symbols:
                self.symbol_queue.append(k)
            
            self.find_exceptions(self.symbol_queue, self.exceptions_queue)
            
            suspicious_companies = []
            with open('suspicious_companies.csv', 'wb') as output:
                while len(self.exceptions_queue)>0:
                    line = str(self.exceptions_queue.pop())
                    line = line.replace("'",'')
                    line = line.replace("(",'')
                    line = line.replace(")",'')
                    suspicious_companies.append(line.split(',')[0])
                    output.write(str(line)+'\n')
                    
            for k in suspicious_companies:
                shutil.rmtree('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+k)
            '''
        
            
            print '\t\tComplete:\t' + str(time.time()-startTime)
        
        if self.asset_type=='etf':
            startTime = time.time()
            print '\tReading in ETF List'
            
            temp = []
            with open('./ETF/ETF_STOCKS.txt', 'r') as f:
                for line in f:
                    temp.append(line.strip())
                
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            symbols = set(temp)
            
            startTime = time.time()
            print '\tDownloading Data'
            
            try:
                shutil.rmtree('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/ETF/ETF_old')
            except:
                print '\t\t\tUnable to delete old ETF data!'
                pass
            time.sleep(1)
            try:
                os.mkdir('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/ETF/ETF_old')
            except:
                print '\t\t\tUnable to create ETF_old folder!'
                pass
            
            Download.folder = 'ETF/ETF_old'
            Download.download_data(symbols)
           
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            #Update data
            startTime = time.time()
            print '\tProcessing Data'
            
            num_cpus = multiprocessing.cpu_count()
            threads = []
            self.update_queue = Queue()
            for k in symbols:
                self.update_queue.put(k)
            
            for k in xrange(num_cpus):
                try:
                    p = Process(target=self.process_updates, args=(self.update_queue, ))
                    threads.append(p)
                except IOError:
                    pass
                
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()     
            
            
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            startTime = time.time()
            print '\tDeriving New Data'
            
            num_cpus = multiprocessing.cpu_count()
            
            threads = []
            self.derive_queue = Queue()
            for k in symbols:
                self.derive_queue.put(k)
            
            for k in xrange(num_cpus):
                p = Process(target=self.derive, args=(self.derive_queue, ))
                threads.append(p)
                    
                
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()     
            
        
            print '\t\tComplete:\t' + str(time.time()-startTime)
            
            
            startTime = time.time()
            print '\tCreating Exceptions List'
            
            '''
            self.symbol_queue = []
            self.exceptions_queue = []
            for k in symbols:
                self.symbol_queue.append(k)
            
            self.find_exceptions(self.symbol_queue, self.exceptions_queue)
            
            suspicious_companies = []
            with open('suspicious_companies.csv', 'wb') as output:
                while len(self.exceptions_queue)>0:
                    line = str(self.exceptions_queue.pop())
                    line = line.replace("'",'')
                    line = line.replace("(",'')
                    line = line.replace(")",'')
                    suspicious_companies.append(line.split(',')[0])
                    output.write(str(line)+'\n')
                    
            for k in suspicious_companies:
                shutil.rmtree('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+k)
            '''
        
            
            print '\t\tComplete:\t' + str(time.time()-startTime)
        
                    
    def process_updates(self, update_queue):
        while update_queue.qsize()>0:
            filename = update_queue.get()
            symbol = filename.replace('_update.csv','')
            new_file = []
            header = ''
            
            if os.path.isfile('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+str(symbol)+'/'+str(symbol)+'.csv')==True:
                with open('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+str(symbol)+'/'+str(symbol)+'.csv','rb') as stock_file:
                    count = 0
                    for line in stock_file:
                        count+=1
                        if count==1:
                            header = line
                            continue
                        
                        check = line.strip()
                        check = check.split(',')
                        check[0] = self.date_to_int(check[0])
                        
                        line = str(check)
                        line = line.replace(']','')
                        line = line.replace('[','')
                        line = line.replace("'",'')
                        line = line.replace(" ",'')
                        line = line + '\n'
                        
                        new_file.append(line)
                        
                new_file.sort()
                new_file.reverse()
                
                with open('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+str(symbol)+'/'+str(symbol)+'.csv', 'wb') as new_stock_file:
                    count = 0
                    new_stock_file.write(header)
                    for k in new_file:
                        new_stock_file.write(k)
                        count+=1
                        #if count>200: break
        return True
            
            
    def find_exceptions(self, symbols_queue, exception_queue):   
        while len(symbols_queue)>0:
            symbol = symbols_queue.pop()
            try:
                with open('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+symbol+'/'+symbol+'.csv') as input_file:
                    daily_change = []
                    old = 0.0
                    temp = []
                    for k in input_file: temp.append(k)
                    temp.reverse()
                    
                    for k in temp:
                        line = k.strip()
                        line = line.split(',')
                        close = None
                        try:
                            close = float(line[1])
                        except:
                            continue
                        if old==0.0:
                            old = close
                            continue
                        
                        daily_change.append((close-old)/old)
                        old = close
                    
                    for k in xrange(len(daily_change)):
                        if daily_change[k] < 0:
                            temp = daily_change[k] + 1.0
                            temp = 1 / temp
                            temp = -temp
                            daily_change[k] = temp
                        if daily_change[k]>=0: daily_change[k]+=1
                            
                    
                    daily_change = list(set(daily_change))
                    daily_change.sort()
                    
                    max_val = max(daily_change)
                    min_val = min(daily_change)
                    spread_1 = math.fabs(max_val-min_val)
                    
                    if max_val>1.75:
                        exception_queue.append((symbol, max_val))
                        continue
                    if min_val<-1.75:
                        exception_queue.append((symbol, min_val))
                        continue
                    
                    
                    
                    daily_change.pop()
                    daily_change.pop(0)
                    
                    max_val = max(daily_change)
                    min_val = min(daily_change)
                    spread_2 = math.fabs(max_val-min_val)
                    
                    spread_diff = math.fabs(spread_1-spread_2)
                    if spread_diff>5:
                        exception_queue.append((symbol, spread_diff))
            except:
                continue
        return True
                    
                    

        
    def get_url(self):
        url = self.download_urls.get()
        if os.path.isfile('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/temp_data/'+str(url[0])+'_update.csv') == False:
            try:
                urllib.urlretrieve(url[1], 'C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/temp_data/'+str(url[0])+'_update.csv')
            except IOError:
                with open('exceptionsFile.csv','ab') as exception_file:
                    exception_file.write(str(url[0])+'\n')
        return True

    
    
    
    def date_to_int(self, date):
        if '/' in date:
            date = date.replace('/',',').replace('-',',').replace('\\',',')
            date = date.split(',')
            try:
                if len(date[0])<2:
                    date[0] = '0'+date[0]
                if len(date[1])<2:
                    date[1] = '0'+date[1]
                date = str(date[2])+str(date[0])+str(date[1])
                return int(date)
            except:
                pass
        if '-' in date:
            date = date.replace('/',',').replace('-',',').replace('\\',',')
            date = date.split(',')
            try:
                if len(date[1])<2:
                    date[1] = '0'+date[1]
                if len(date[2])<2:
                    date[2] = '0'+date[2]
                date = str(date[0])+str(date[1])+str(date[2])
                return int(date)
            except:
                pass
        try:
            return int(date)
        except:
            return 'Date'
        
   
    def derive(self, derive_queue):
        while derive_queue.qsize()>0:
            filename = derive_queue.get()
            
            debug = False
            time_log = deque()
            RSI = deque()
            BB_upper = deque()
            BB_lower = deque()
            SMA_long = deque()
            SMA_short = deque()
            output_file = deque()
            header = deque()
            if os.path.isfile('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+filename+'/'+filename+'.csv') == False:
                continue
            with open('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+filename+'/'+filename+'.csv', 'rb') as input_file:
                SMA_long_temp = deque()
                SMA_short_temp = deque()
                EMA_short_length = 12.0
                EMA_long_length = 26.0
                EMA_short_old = 0.0
                EMA_long_old = 0.0
                SD = 0.0
                donchian_days = 20.0
                DTemp = deque()
                RSI_days = 14.0
                RSI_temp = deque()
                
                if debug:
                    time_log = [0,0,0,0,0]
                
                temp = deque()
                
                
                for k in input_file:
                    if len(header)<1:
                        header.append('ok')
                        continue
                    temp.append(k)
                temp.reverse()
                start_time = time.time()
                
                for line in temp:
                    line = line.replace('"','').strip()
                    line = line.replace('[','')
                    line = line.replace(']','')
                    line_array = line.split(',');
                    if len(line_array)<7:
                        continue
                    
                    if len(header)<1:
                        for k in range(0, len(line_array)):
                            header.append(line_array[k])
                        continue
                    
                    for j in range(0, len(line_array)):
                        if '-' in line_array[j] or '/' in line_array[j]:
                            line_array[j] = 0.0
                        else: 
                            try:
                                line_array[j] = float(line_array[j])
                            except:
                                pass
                    
                    #Use adj closing value instead of open value
                    
                    temp = line_array[1]
                    line_array[1] = line_array[-1]
                    line_array[-1] = temp
                    
                    
                    if line_array[1] == 0.0:
                        continue
                    if type(line_array[1]) is str:
                        with open('exceptionsList.csv', 'ab') as except_file:
                            except_file.write(filename)
                        continue
                    
                    #Derive SMA_long and SMA_short
                    if debug:
                        start_time = time.time();
                    
                    SMA_long_temp.append(line_array[1])
                    SMA_short_temp.append(line_array[1])
                    if len(SMA_long_temp)>100:
                        SMA_long_temp.popleft()
                    if len(SMA_short_temp)>30:
                        SMA_short_temp.popleft()
                    SMA_long = sum(SMA_long_temp)/len(SMA_long_temp)
                    SMA_short_list = list(SMA_short_temp)
                    SMA_short = sum(SMA_short_list)/len(SMA_short_list)
                    
                    if debug:
                        time_log[0] = time_log[0] + time.time()-start_time
                    
                    #Derive EMA_short and EMA_long
                    if debug:
                        start_time = time.time();
                        
                    if EMA_short_old!=0:
                        EMA_short_val = line_array[1]*(2/(EMA_short_length+1)) + EMA_short_old*(1-(2/(EMA_short_length+1)))
                        EMA_short_old = EMA_short_val
                    else:
                        EMA_short_val = line_array[1]
                        EMA_short_old = EMA_short_val
                        
                    if EMA_long_old!=0:
                        EMA_long_val = line_array[1]*(2/(EMA_long_length+1)) + EMA_long_old*(1-(2/(EMA_long_length+1)))
                        EMA_long_old = EMA_long_val
                    else:
                        EMA_long_val = line_array[1]
                        EMA_long_old = EMA_long_val
                        
                    if debug:
                        time_log[1] = time_log[1] + time.time()-start_time
                        
                    #Derive BolingerBands
                    if debug:
                        start_time = time.time();
                    
                    M = 0.0
                    S = 0.0
                    k = 1
                    
                    for i in range(0, len(SMA_short_list)):
                        tmpM = M;
                        M += (SMA_short_list[i] - tmpM) / k;
                        S += (SMA_short_list[i] - tmpM) * (SMA_short_list[i] - M);
                        k=k+1
                    
                    try:
                        SD = math.sqrt(S / (k-2))
                        BB_upper=(2*SD)+SMA_short
                        BB_lower=(-2*SD)+SMA_short
                    except ZeroDivisionError:
                        BB_upper = line_array[1]
                        BB_lower = line_array[1]
                    
                    if debug:
                        time_log[2] = time_log[2] + time.time()-start_time
                        
                    #Derive Donchian Trends
                    if debug:
                        start_time = time.time();
                        
                    DTemp.append(line_array[1])
                    
                    if len(DTemp)>donchian_days:
                        DTemp.popleft()
                        
                    
                    if debug:
                        time_log[3] = time_log[3] + time.time()-start_time
                        
                    #Derive RSI Value
                    if debug:
                        start_time = time.time();
                        
                    RSI_temp.appendleft(line_array[1])
                    if len(RSI_temp) > RSI_days:
                        RSI_temp.pop()
        
                    up_days = deque()
                    down_days = deque()
                    
                    for i in range(0, len(RSI_temp)-1):
                        difference = RSI_temp[i]-RSI_temp[i+1];
                        if difference>0:
                            up_days.append(difference)
                        if difference<0:
                            down_days.append(-1*difference)
                    try:
                        upAvg = sum(up_days)/len(up_days)
                    except ZeroDivisionError:
                        upAvg = 0
                    try:
                        downAvg = sum(down_days)/len(down_days)
                    except ZeroDivisionError:
                        downAvg = 0
                    
                    try:
                        RS = upAvg/downAvg
                    except ZeroDivisionError:
                        RS = upAvg/0.01
        
                    RSI = 100 - 100/(1+RS)
                    
                    if debug:
                        time_log[4] = time_log[4] + time.time()-start_time
                        
                    # D volume
                    volume = line_array[5]
                    
                        
                    #Create output line
                    output_file.append([round(line_array[1],4), round(SMA_long,4), round(SMA_short,4), round(EMA_short_val,4), round(EMA_long_val,4), round(BB_upper,4), round(BB_lower,4), round(max(DTemp),4), round(min(DTemp),4), round(RSI,4), round(volume, 4)])
        
            output_file.reverse()
            with open('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/'+self.folder+'/'+filename+'/'+filename+'_train.csv', 'wb') as output:
                writer = csv.writer(output)
                writer.writerow(['Open','SMA_long','SMA_short','EMA_short','EMA_long','upper_bol_band','lower_bol_band','20_day_high','20_day_low','RSI','volume'])
                writer.writerows(output_file)
                
            if debug:
                print '\tSMA:\t' + str(time_log[0])
                print '\tEMA:\t' + str(time_log[1])
                print '\tBB:\t' + str(time_log[2])
                print '\tDT:\t' + str(time_log[3])
                print '\tRSI:\t' + str(time_log[4])
                print '\tTotal:\t' + str(sum(time_log))
            
        return True



if __name__ == '__main__':
    x = update_data()
    x.asset_type = 'etf'
    x.folder = 'ETF/ETF_old'
    x.update_process()