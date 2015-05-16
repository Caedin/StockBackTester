'''
Created on Jul 6, 2014

@author: Keith
'''

class strategy_model(object):
    strategy = [];
    EMA_short = 0
    EMA_long = 0
    buy = 1
    
    initial_funds = 100000.0
    return_value = 1.0
    currently_held = False
    buy = -1
    sell_value = 0
    
    data = None
    number_days = 0
    
    def __init__(self):
        pass
    def set_strategy(self, strat):
        self.strategy = strat   
    def updatePrice(self, data):
        ''' EMA Calc '''
        self.data = data
        self.number_days+=1
        
        if self.strategy[0] == '1':
            short_over_long = False
            if self.EMA_short>self.EMA_long:
                short_over_long = True
                
            self.EMA_short = data.value(3)
            self.EMA_long = data.value(4)
            
            short_over_long_new = False
            if self.EMA_short>self.EMA_long:
                short_over_long_new = True
                
            
            if short_over_long != short_over_long_new:
                if self.EMA_short>self.EMA_long:
                    self.buy = 0
                else:
                    self.buy = 1
        
        #BB Calc 
        if self.strategy[1] == '1':
            if data.value(0)>data.value(5):
                self.buy = 0
        if data.value(0)<data.value(6):
                self.buy = 1
        
        
        #Donchian Trends
        if self.strategy[2] == '1':
            if data.value(0)>=data.value(7):
                self.buy = 0
            if data.value(0)<=data.value(8):
                self.buy = 1
        
        
        #RSI Indicators
        if self.strategy[3] == '1':
            if data.value(9)<=30:
                self.buy=0
            if data.value(9)>=70:
                self.buy=1
                
        # EMA-X Prime
        if self.strategy[4] == '1':
            short_over_long = False
            if self.EMA_short>self.EMA_long:
                short_over_long = True
                
            self.EMA_short = data.value(3)
            self.EMA_long = data.value(4)
            
            short_over_long_new = False
            if self.EMA_short>self.EMA_long:
                short_over_long_new = True
                
            
            if short_over_long != short_over_long_new:
                if self.EMA_short>self.EMA_long:
                    self.buy = 1
                else:
                    self.buy = 0
        
        #BB Calc 
        if self.strategy[5] == '1':
            if data.value(0)>data.value(5):
                self.buy = 1
            if data.value(0)<data.value(6):
                self.buy = 0
        
        
        #Donchian Trends
        if self.strategy[6] == '1':
            if data.value(0)>=data.value(7):
                self.buy = 1
            if data.value(0)<=data.value(8):
                self.buy = 0
        
        
        #RSI Indicators
        if self.strategy[7] == '1':
            if data.value(9)<=30:
                self.buy=1
            if data.value(9)>=70:
                self.buy=0
        
        self.calculate_profits()
    def calculate_profits(self):
        # TEST
        if self.currently_held==False and self.buy==0:
            self.buy_value = self.data.value(0)
            #print self.get_strategy()+"\tBought stock at:\t" + '${:4,.2f}'.format(self.buy_value)
            self.currently_held = True
            #raw_input("Press any key to continue...")
        
        elif self.buy==1 and self.currently_held==True:
            self.sell_value = self.data.value(0)
            #print self.get_strategy()+"\tSold stock at:\t" + '${:4,.2f}'.format(self.sell_value)
            
            try:
                self.return_value = (self.sell_value-self.buy_value)/self.buy_value
            except ZeroDivisionError:
                return
            self.initial_funds = self.initial_funds*(1+self.return_value)
            #print self.get_strategy()+"\tCurrent Funds:\t" + '${:4,.2f}'.format(self.initial_funds)
            #raw_input("Press any key to continue...")
            
            self.return_value = 0
            self.sell_value = 0
            self.buy_value = 0
            self.currently_held = False
        
        else:
            # Sets the value to hold
            self.buy = -1
        
        
    def get_value(self):
        return self.initial_funds
    def get_state(self):
        if self.number_days<5:
            return "NONE"
        if self.buy == 0:
            return "BUY"
        if self.buy == 1:
            return "SELL"
        if self.buy == -1:
            return "NONE"
    def get_strategy(self):
        return self.strategy
    
    
    
    
    
    
    
    
    
    
    
class strategy_model_python(object):
    strategy = []
    EMA_short = 0
    EMA_long = 0
    buy = -1
    data = None

    def __init__(self):
        pass
    def set_strategy(self, strat):
        self.strategy = strat   
        
    def updatePrice(self, data):
        #Default of no position
        self.buy = -1
        
        #Check if company is still in business
        if data[0]==0.0:
            self.buy = -1
            return
        
        #Check if company is liquid or not
        if data[10]<=25000:
            self.buy = -1
            return
        
        ''' EMA Calc '''
        self.data = data
        
        if self.strategy[0] == '1':
            short_over_long = False
            if self.EMA_short>self.EMA_long:
                short_over_long = True
                
            self.EMA_short = data[3]
            self.EMA_long = data[4]
            
            short_over_long_new = False
            if self.EMA_short>self.EMA_long:
                short_over_long_new = True
                
            
            if short_over_long != short_over_long_new:
                if self.EMA_short>self.EMA_long:
                    self.buy = 0
                else:
                    self.buy = 1
        
        #BB Calc 
        if self.strategy[1] == '1':
            if data[0]>data[5]:
                self.buy = 0
            if data[0]<data[6]:
                self.buy = 1
        
        
        #Donchian Trends
        if self.strategy[2] == '1':
            if data[0]>=data[7]:
                self.buy = 0
            if data[0]<=data[8]:
                self.buy = 1
        
        
        #RSI Indicators
        if self.strategy[3] == '1':
            if data[9]<=35:
                self.buy=0
            if data[9]>=70:
                self.buy=1
                
        # EMA-X Prime
        if self.strategy[4] == '1':
            short_over_long = False
            if self.EMA_short>self.EMA_long:
                short_over_long = True
                
            self.EMA_short = data[3]
            self.EMA_long = data[4]
            
            short_over_long_new = False
            if self.EMA_short>self.EMA_long:
                short_over_long_new = True
                
            
            if short_over_long != short_over_long_new:
                if self.EMA_short>self.EMA_long:
                    self.buy = 1
                else:
                    self.buy = 0
        
        #BB Calc 
        if self.strategy[5] == '1':
            if data[0]>data[5]:
                self.buy = 1
            if data[0]<data[6]:
                self.buy = 0
        
        
        #Donchian Trends
        if self.strategy[6] == '1':
            if data[0]>=data[7]:
                self.buy = 1
            if data[0]<=data[8]:
                self.buy = 0
        
        
        #RSI Indicators
        if self.strategy[7] == '1':
            if data[9]<=35:
                self.buy=1
            if data[9]>=70:
                self.buy=0
            
        
    def get_state(self):
        if self.buy == 0:
            return "BUY"
        if self.buy == 1:
            return "SELL"
        if self.buy == -1:
            return "NONE"