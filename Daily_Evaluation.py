'''
Created on March, 21 2014

@author: Keith Dyer
'''

import os
import time
import random
from multiprocessing import Process
import strategy_model
import math



class daily_evaluator(Process):

    save_path = 'December'

    
    def __init__(self, queue):
        super(daily_evaluator, self).__init__()
        self.queue= queue
    
    def run(self):
        while self.queue.empty() == False:
            self.daily_evaluations()
            
    def load_data_to_memory(self):
        self.stock_data = {}
        for k in self.symbols:
            tfile = []
            with open("stocks_old/"+k+"/"+k+"_train.csv", 'rb') as input_file:
                for line in input_file:
                    tfile.append(line)
            self.stock_data[k] = tfile
        
    
    def daily_evaluations(self, strategy=None):
        if strategy == None:
            strategy = self.queue.get()
        if strategy == None:
            return -1.0
        
        self.sector = {}
        # Gather list of all stocks/sectors
        with open('NYSE.csv', 'r') as f:
            next(f)
            for line in f:
                line = line.replace('"',"").strip()
                spl =line.split(',')
                self.sector[spl[0]] = str(spl[7])
        with open('NASDAQ.csv', 'r') as f:
            next(f)
            for line in f:
                line = line.replace('"',"").strip()
                spl =line.split(',')
                self.sector[spl[0]] = str(spl[7])
        with open('AMEX.csv', 'r') as f:
            next(f)
            for line in f:
                line = line.replace('"',"").strip()
                spl =line.split(',')
                self.sector[spl[0]] = str(spl[7])
                
        self.symbols = os.listdir('C:/Users/Keith/Desktop/Workspace/Eclipse Workspace/Stock_Predictor/src/stocks_old')  
        for key in self.symbols:
            if key not in self.sector:
                self.sector[key] = 'Unclassified'
        
        self.load_data_to_memory()
        
        self.days_ago = 100
        portfolio_val = []
        self.path = 'C:\\Users\\Keith\\Desktop\\Workspace\\Eclipse Workspace\\Stock_Predictor\\src\\'+self.save_path+'\\'+str(strategy)
        self.funds = 5000
        # This says if we are doing a larger sample, create a new folder
        if self.days_ago>1:
            num_strat = 0
            while os.path.isdir(self.path):
                num_strat+=1
                self.path = self.path.split('-')
                self.path = self.path[0]
                self.path = self.path+'-'+str(num_strat)
            
        
        while self.days_ago>0:
            
            self.buy_list = []
            self.sell_list = []
            self.log = []
            self.assets = {}
            self.open_price = {}
            self.cash = 0.0
            self.timer = {}
            self.trade_profits = 0.0
            self.max_stocks = 20
            self.commision_charges = 0.0
            
                
            
            #Read Asset file
            #start_time = time.time()
            #print 'Reading Assets'
            self.read_asset(strategy)
            #print '\tComplete:\t'+str(time.time()-#start_time)
            
            #Calculate buy/sells
            ##start_time = time.time()
            #print 'Calculate Predictions'
            self.calculate_predictions(strategy)
            #print '\tComplete:\t'+str(time.time()-#start_time)
            #Process sells
            ##start_time = time.time()
            #print 'Process Sells'
            self.process_sells(strategy)
            #print '\tComplete:\t'+str(time.time()-#start_time)
            #Process buys
            ##start_time = time.time()
            #print 'Process Buys'
            self.process_buys(strategy)
            #print '\tComplete:\t'+str(time.time()-#start_time)
            #Write log file
            ##start_time = time.time()
            #print 'Writing Log'
            portfolio_val.append(self.write_log(strategy))
            #print '\tComplete:\t'+str(time.time()-#start_time)
            #Write Asset File
            #start_time = time.time()
            #print 'Saving Assets'
            self.write_asset_file(strategy)
            #print '\tComplete:\t'+str(time.time()-#start_time)
            
            self.days_ago = self.days_ago-1
        with open(self.path+'/'+str(strategy)+'_super_log.csv', 'wb') as slog:
            count = 0
            portfolio_val.reverse()
            for k in portfolio_val:
                slog.write(str(count)+', ' +'${:4,.2f}'.format(k)+'\n')
                count+=1
                
        return 1.0
        
        

    
    def read_asset(self, strat):
        if os.path.isfile(self.path+'/'+str(strat)+'_assets.csv') == True:
            with open(self.path+'/'+str(strat)+'_assets.csv', 'rb') as f:
                for line in f:
                    line = line.replace('\n','').strip()
                    asset = line.split(':')
                    if '$' in asset[1]:
                        asset[1] = asset[1].replace('$','')
                        asset[1] = asset[1].replace(',','')
                        asset[1] = asset[1].strip()
                        
                        self.cash = self.cash + float(asset[1])
                        continue
                    self.assets[asset[0]] = [asset[1],asset[2],asset[3]]
        else:
            num_strat = 0
            while os.path.isdir(self.path):
                num_strat+=1
                self.path = self.path.split('-')
                self.path = self.path[0]
                self.path = self.path+'-'+str(num_strat)
            os.mkdir(self.path)
            self.cash = self.funds;
    
    def evaluate_stock(self, symbols_temp, strat):
            for stock in symbols_temp:
                ''' CSV file is formated and ready to go. Load data into program '''
                stock_data = []
                strategy_models = []
                temp = strategy_model.strategy_model_python()
                temp.set_strategy(strat)
                strategy_models.append(temp)
                
                
                count = 0
                try:
                    input_file = self.stock_data[stock]
                    for line in input_file:
                        count+=1
                        if count<self.days_ago:
                            continue
                        data = line.split(',')
                        if data[0] != 'Open':
                            for k in range(0, len(data)):
                                data[k] = float(data[k])
                            stock_data.append(data)
                            if stock not in self.open_price:
                                self.open_price[stock] = data[0]
                        if len(stock_data)>2:
                            break
                    
                    stock_data.reverse()
                    
                    if len(stock_data)>2:
                        for line in stock_data:
                            for i in strategy_models:
                                i.updatePrice(line)

                    for i in strategy_models:
                        if i.get_state() == "BUY":
                            self.buy_list.append([stock, self.open_price[stock]])
                        if i.get_state() == "SELL":
                            self.sell_list.append([stock, self.open_price[stock]])   
                except IOError:
                    pass
                            
                    
    def calculate_predictions(self, strat):
        for stock in self.symbols:
            self.evaluate_stock([stock], strat)
        
    def process_sells(self , strat):
        self.trade_profits = 0
        for sell_stock in self.sell_list:
            if sell_stock[0] in self.assets:
                shares = float(self.assets[sell_stock[0]][0])
                price = float(self.open_price[sell_stock[0]])
                self.cash = self.cash + shares*price
                return_value = (shares*price)-float((self.assets[sell_stock[0]][1]))
                self.log.append('Sold '+str(int(shares))+' shares of '+str(sell_stock[0])+' for '+'${:4,.2f}'.format(price) + ' per share. Profit: '+'${:4,.2f}'.format(return_value))
                self.trade_profits = self.trade_profits + return_value
                self.assets.pop(sell_stock[0])
                self.cash = self.cash - 7.0
                self.commision_charges += 7.0
                    
    def process_buys(self, strat):
        buy_lists_by_sector = {}
        list_of_sectors = []
        final_buys = []
        self.max_stocks = self.cash/1000
        invest_amount = 1000
        
        for key in self.sector:
            if self.sector[key] not in list_of_sectors:
                list_of_sectors.append(self.sector[key])
        for sector in list_of_sectors:
            buy_lists_by_sector[sector] = []
        
        for stock in self.buy_list:
            buy_lists_by_sector[self.sector[stock[0]]].append(stock)
        
        temp_num_stocks = 0.0
        for key in buy_lists_by_sector:
            try:
                final_buys.append((key,(float(len(buy_lists_by_sector[key]))/float(len(self.buy_list)) * self.max_stocks)))
                temp_num_stocks += int(float(len(buy_lists_by_sector[key]))/float(len(self.buy_list)) * self.max_stocks)
            except ZeroDivisionError:
                final_buys.append((key,0))
        
        if temp_num_stocks<self.max_stocks:
            c = 0
            final_buys.sort(key=lambda x: x[1])
            final_buys.reverse()
            while temp_num_stocks<self.max_stocks:
                test_tuple = final_buys[c]
                test_tuple = (test_tuple[0], math.ceil(test_tuple[1]))
                final_buys[c] = test_tuple
                temp_num_stocks+=1
                c+=1
                
                
        temp = {}
        for k in final_buys:
            temp[k[0]] = int(k[1])
        final_buys = temp
        
        random.shuffle(self.buy_list)
        for buy_stock in self.buy_list:
            try:
                shares = int(invest_amount/buy_stock[1])
                if shares>0:
                    if final_buys[self.sector[buy_stock[0]]]>0:
                        final_buys[self.sector[buy_stock[0]]] = final_buys[self.sector[buy_stock[0]]] - 1
                        
                        if buy_stock[0] in self.assets:
                            self.assets[buy_stock[0]] = [(float(self.assets[buy_stock[0]][0]) + shares), (float(self.assets[buy_stock[0]][1]) + (shares * self.open_price[buy_stock[0]]))]
                        else:
                            self.assets[buy_stock[0]] = [shares, (shares * self.open_price[buy_stock[0]]), 1.0]
                        
                        self.cash = self.cash -  (shares * self.open_price[buy_stock[0]]);
                        self.cash = self.cash - 7.0
                        self.commision_charges += 7.0
                        self.log.append('Bought '+str(int(shares))+' shares of '+str(buy_stock[0]) + ' at ' + '${:4,.2f}'.format(buy_stock[1]) + ' per share')
            except ZeroDivisionError:
                pass
        
    def write_log(self, strat):
        # Calculate total assets
        portfolio_value = 0.0
        sector_sums = {}
        
        
        
        for key in self.assets:
            try:
                if self.sector[key] not in sector_sums:
                    return_value =  float(self.open_price[key])/(float(self.assets[key][1])/float(self.assets[key][0]))
                    sector_sums[self.sector[key]] = [[float(self.assets[key][1])], [return_value]]
                elif self.sector[key] in sector_sums:
                    return_value =  float(self.open_price[key])/(float(self.assets[key][1])/float(self.assets[key][0]))
                    sector_sums[self.sector[key]][0].append(float(self.assets[key][1]))
                    sector_sums[self.sector[key]][1].append(return_value)
            except KeyError:
                print key
                    
        
        
        self.log.append('\nPortfolio By Sector')
        self.log.append('{0:50}'.format(str('Sector'))+'{0:10}'.format('Invested')+'{:>10}'.format('Return'))
        for key in sector_sums:
            ratio = sum(sector_sums[key][1])/len(sector_sums[key][1])
            if ratio<1:
                ratio = -1/(ratio) +1
            else:
                ratio = ratio - 1
            
            ratio = ratio * 100
            ratio = str(round(ratio, 2))+'%'
            self.log.append('{0:50}'.format(str(key))+'${0:10,.2f}'.format(sum(sector_sums[key][0]))+'{:>10}'.format(ratio))
            
        
        for key in self.assets:
            a = self.assets[key][0]
            try:
                portfolio_value = portfolio_value + (float(a) * self.open_price[key])
            except KeyError:
                print key
                
        if self.cash>0:
            portfolio_value+=self.cash
        
        self.log.append('\n{0:25}'.format('Trade Profits') + '${:4,.2f}'.format(self.trade_profits))
        self.log.append('\n{0:25}'.format('Commission Fees') + '-${:4,.2f}'.format(self.commision_charges))
        
        overall_return = portfolio_value/self.funds
        if overall_return<1:
            overall_return = (-1/overall_return + 1)*100
        else:
            overall_return = (overall_return - 1)*100
            
        self.log.append('{0:25}'.format('Portfolio Value') +'${0:4,.2f}'.format(portfolio_value)+'{0:10,.2f}%'.format(overall_return))
        
        with open(self.path+'/'+str(strat)+'_log.csv', 'ab') as log_file:
            date = time.strftime("%d_%m_%Y")
            log_file.write('Log file for '+str(date)+'\n')
            for row in self.log:
                if 'Portfolio' not in row:
                    log_file.write('\t'+str(row)+'\n')
                else: 
                    
                    log_file.write(str(row)+'\n')
            log_file.write('-----------------------------------------------------------\n')
        
        return portfolio_value
            
    def write_asset_file(self, strat):
        temp_list = []
        for key in self.assets:
            temp_list.append([key, self.assets[key][0], self.assets[key][1]])
        temp_list.sort()
        with open(self.path+'/'+str(strat)+'_assets.csv', 'wb') as asset_file:
            for k in temp_list:
                try:
                    return_value = float(self.open_price[k[0]])/(float(k[2])/float(k[1]))
                    asset_file.write(str(k[0])+":"+str(k[1])+":"+str(k[2])+":"+str(return_value)+'\n')
                except KeyError:
                    print k[0]
            asset_file.write(str('cash:\t')+'${:4,.2f}'.format(self.cash))
