'''
Created on Jul 18, 2014

@author: Keith
'''
from __future__ import division
import sys
import matplotlib.pyplot as plt
import random
import urllib
import os

plt.ion()

psuedo_sample_size = 2520

base_url = "http://ichart.finance.yahoo.com/table.csv?s="
def make_url(ticker_symbol):
    return base_url + ticker_symbol

output_path = "."
def make_filename(ticker_symbol, directory="Stocks"):
    return output_path + "/" + directory + "/" + ticker_symbol + ".csv"

def pull_historical_data(ticker_symbol, directory="Stocks"):
	try:
		file_name = make_filename(ticker_symbol, directory)
		if os.path.isfile(file_name) == True:
			return file_name
		else:	
			urllib.urlretrieve(make_url(ticker_symbol), file_name)
			return file_name
	except urllib.ContentTooShortError as e:
		outfile = open(make_filename(ticker_symbol, directory), "w")
		outfile.write(e.content)
		outfile.close()

def get_data(stk1):
	spxl_data = []
	with open(stk1, 'rb') as input:
		input.next()
		spxl_data = [float(x.split(',')[-1]) for x in input]
		
		if 'gold' in stk1:
			t = [0.0] * (len(spxl_data)*21)
			for count,x in enumerate(spxl_data):
				for y in xrange(21):
					t[count*21+y] = x
			spxl_data = t
			spxl_data.reverse()
	
	spxl_data.reverse()
	return spxl_data
	
def generate_leveraged_data(data, leverage_rate):
	leveraged_etf = []
	for x in xrange(len(data)):
		if x == 0:
			leveraged_etf.append(data[x])
			continue
		chng = ((data[x]-data[x-1]) / data[x-1])
		old = leveraged_etf[-1]
		new = old * (leverage_rate*chng+1)
		leveraged_etf.append(new)
	return leveraged_etf
	
def invest_with_rebalance(stk1, stk2, ratio, window=0.10, back_test_length=-1, leverage = 1, investment_period = 1, chart=True, verify_data_lengths=True, periodic_rebalance="None", rebalance=True):
	daily_inc = 10
	spxl_fund = 0
	tmf_fund = 0
	price = 0
	rebalance_fee = 14
	periodic_rebalance_time = max(len(stk1[1]), len(stk2[1]))+1
	
	name1 = stk1[0]
	name2 = stk2[0]

	if verify_data_lengths==True:
		if leverage!=1:
			stk1 = [x for x in stk1[1]]
			stk2 = [x for x in stk2[1]]
			stk1 = generate_leveraged_data(stk1, leverage)
			#stk2 = generate_leveraged_data(stk2, leverage)
		else:
			stk1 = [x for x in stk1[1]]
			stk2 = [x for x in stk2[1]]
			
		if back_test_length==-1:
			min_backtest_time = min(len(stk1), len(stk2))
		else:
			min_backtest_time = back_test_length
			
		t1 = [0.0] * min_backtest_time
		t2 = [0.0] * min_backtest_time
		
		stk1.reverse()
		stk2.reverse()
		for x in xrange(min_backtest_time):
			t1[x] = stk1[x]
			t2[x] = stk2[x]
		
		stk1 = t1
		stk2 = t2
		stk1.reverse()
		stk2.reverse()
	else:
		stk1 = stk1[1]
		stk2 = stk2[1]
	
	fund_values = [0.0] * (len(stk1)+1)
	spxl_values = [0.0] * (len(stk1)+1)
	tmf_values = [0.0] * (len(stk1)+1)
	
	spxl_values[0] = ratio*10
	tmf_values[0] = (1-ratio)*10
	fund_values[0] = tmf_values[0] + spxl_values[0]
	
	if periodic_rebalance=="Daily":
		periodic_rebalance_time = 1
	if periodic_rebalance=="Weekly":
		periodic_rebalance_time = 5
	if periodic_rebalance=="Monthly":
		periodic_rebalance_time = 21
	if periodic_rebalance=="Quarterly":
		periodic_rebalance_time = 63
	if periodic_rebalance=="Yearly":
		periodic_rebalance_time = 252
	
	spxl_fund = 0
	tmf_fund = 0
	rebalance_count = 0
	rebalance_window = window
	c=0
	
	for x,y in zip(stk1, stk2):
		c+=1
		try:
			price_s1 = x
			daily_spxl_investment = 0
			if c%investment_period==0:
				daily_spxl_investment = ratio * daily_inc*investment_period
			spxl_shares = daily_spxl_investment/price_s1
			spxl_fund += spxl_shares
		except ZeroDivisionError:
			spxl_shares = 0
			spxl_fund = 0
			
		try:
			price_s2 = y
			daily_tmf_investment = 0
			if c%investment_period==0:
				daily_tmf_investment = (1-ratio) * daily_inc*investment_period
			tmf_shares = daily_tmf_investment/price_s2
			tmf_fund += tmf_shares
		except ZeroDivisionError:
			tmf_shares = 0
			tmf_fund = 0
		
		spxl_values[c] = (spxl_fund*price_s1)
		tmf_values[c] = (tmf_fund*price_s2)
		fund_values[c] = (spxl_fund*price_s1 + tmf_fund*price_s2)
	
		if price_s1 == 0 or price_s2 == 0: continue
		
		percent_spxl = spxl_values[c]/fund_values[c]
		
		# Rebalance SPXL -> TMF
		if (percent_spxl > (ratio+rebalance_window) or c%periodic_rebalance_time==0) and rebalance==True:
			#print "Rebalance SPXL -> TMF"
			rebalance_count+=1
			target_spxl_value = ratio * fund_values[c]
			# Sell SPXL
			sell_amount = spxl_values[c] - target_spxl_value
			sell_shares = sell_amount/price_s1
			spxl_fund -= sell_shares
			cash_pool = sell_amount-rebalance_fee
			spxl_values[c] = spxl_fund*price_s1
			# Buy TMF
			tmf_shares = cash_pool / price_s2
			tmf_fund+= tmf_shares
			tmf_values[c]=(tmf_fund*price_s2)
			fund_values[c] = (spxl_fund*price_s1 + tmf_fund*price_s2)
			
		# Rebalance TMF -> SPXL
		if (percent_spxl < (ratio-rebalance_window) or c%periodic_rebalance_time==0)  and rebalance==True:
			#print "Rebalance TMF -> SPXL"
			rebalance_count+=1
			target_tmf_value = (1-ratio) * fund_values[c]
			# sell TMF
			sell_amount = tmf_values[c] - target_tmf_value
			sell_shares = sell_amount/price_s2
			tmf_fund -= sell_shares
			cash_pool = sell_amount-rebalance_fee
			tmf_values[c] = tmf_fund*price_s2
			# Buy SPXL
			spxl_shares = cash_pool / price_s1
			spxl_fund += spxl_shares
			spxl_values[c]=(spxl_fund*price_s1)
			fund_values[c] = (spxl_fund*price_s1 + tmf_fund*price_s2)
		
			
	years = len(stk1)/252

	basic_value = [0.0] * (len(stk1)+1)
	multiplier = 0
	for x in xrange(0, len(stk1)+1):
		if x%investment_period==0: multiplier+=1
		basic_value[x] = 10*investment_period*multiplier
		
	days = [x/252+(2015-years) for x in xrange(len(stk1)+1)]
	
	if chart==True:
		fig = plt.figure()
		ax = fig.add_subplot('111')

		ax.plot(days, basic_value, label='Invested Dollars')
		ax.plot(days, spxl_values, label=name1.upper())
		ax.plot(days, tmf_values, label=name2.upper())
		ax.plot(days, fund_values, label='Total')
		plt.legend(loc='best')
		
		fig.canvas.show()
		return fund_values[-1], rebalance_count
	else:
		return fund_values[-1], rebalance_count
		
def generate_chart_manual():
	try:
		stk1 = raw_input("Enter Stock 1: ")
		stk2 = raw_input("Enter Stock 2: ")
		ratio = float(raw_input("Enter target ratio for Stock 1: "))
		periodic_rebalance = raw_input("Periodic Rebalancing: [None, Daily, Weekly, Monthly, Quarterly, Yearly]: ")
		window_rebalance = float(raw_input("Maximal Target Difference: "))
		
		stocks = []
		t1 = pull_historical_data(stk1)
		t2 = pull_historical_data(stk2)
		t1 = get_data(t1)
		t2 = get_data(t2)
		stocks.append((stk1.upper(), t1))
		stocks.append((stk2.upper(), t2))
		
		invest_with_rebalance(stocks[0], stocks[1], ratio=ratio, window=window_rebalance, leverage=1, rebalance=True, chart=True, periodic_rebalance=periodic_rebalance)
	except Exception:
		print 'Some unknown exception occured. Check input arguments.'
		raw_input()
		exit()
	
def generate_chart_cmdline():
	stk1 = sys.argv[1]
	stk2 = sys.argv[2]
	ratio = float(sys.argv[3])
	periodic_rebalance = sys.argv[4]
	window_rebalance = float(sys.argv[5])
	
	stocks = []
	t1 = pull_historical_data(stk1)
	t2 = pull_historical_data(stk2)
	t1 = get_data(t1)
	t2 = get_data(t2)
	stocks.append((stk1.upper(), t1))
	stocks.append((stk2.upper(), t2))
	
	invest_with_rebalance(stocks[0], stocks[1], ratio=ratio, window=window_rebalance, leverage=3, rebalance=True, chart=True, periodic_rebalance=periodic_rebalance)
	
if __name__ == '__main__':
	if len(sys.argv)==1:
		generate_chart_manual()
	else:
		generate_chart_cmdline()
	raw_input()

	
	
