'''
Created on Sep 17, 2014

@author: Keith
'''
import os


class probability_model(object):
    
    master_dictionary = {}
    stock_folder = "stocks_old"
    
    def init(self):
        pass
    
    def build_model(self):
        folders = os.listdir('./'+self.stock_folder)
        master_list = []
        for k in folders:
            if os.path.isfile('./'+self.stock_folder + '/' + k + '/' + k +'_train.csv'):
                with open('./'+self.stock_folder + '/' + k + '/' + k +'_train.csv', 'rb') as input_file:
                    input_file.next()
                    t = []
                    for line in input_file:
                        t.append(line)
                    t.reverse()
                    
                    close = 0
                    for line in t:
                        values = line.strip().split(',')
                        values.pop()
                        if close == 0:
                            close = values[0]
                            values.append('NULL')
                        elif values[0]>close:
                            values.append('YES')
                            close = values[0]
                        elif values[0]<close:
                            values.append('NO')
                            close = values[0]
                        
                        values = values[-2:]
                        if values[1] == 'YES' or values[1] == 'NO':
                            values[0] = round(float(values[0]))
                            master_list.append(values)
        
        for x in master_list:
            rsi_val = x[0]
            rsi_action = x[1]
            
            if rsi_val not in self.master_dictionary and rsi_action == 'YES':
                self.master_dictionary[rsi_val] = 1
            if rsi_val in self.master_dictionary and rsi_action == 'YES':
                self.master_dictionary[rsi_val] = self.master_dictionary[rsi_val] + 1
                
        
        for key in self.master_dictionary:
            c = 0
            for x in master_list:
                if x[0] == key:
                    c+=1
                
            if c>0:
                self.master_dictionary[key] = float(self.master_dictionary[key])/float(c)
        
        
        for k in self.master_dictionary: print str(k) + '\t' + str(self.master_dictionary[k])










if __name__ == '__main__':
    test = probability_model()
    test.build_model()