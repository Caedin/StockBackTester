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
SP_PE_ratio = []

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
		
def get_data(stock_file):
	stock_data = []
	with open(stock_file, 'rb') as input:
		input.next()
		stock_data = [float(x.split(',')[-1]) for x in input]
		
		if 'gold' in stock_file:
			t = [0.0] * (len(stock_data)*21)
			for count,x in enumerate(stock_data):
				for y in xrange(21):
					t[count*21+y] = x
			stock_data = t
			stock_data.reverse()
	
	stock_data.reverse()
	return stock_data
	
def generate_leveraged_data(data, leverage_rate):
	leveraged_security_data = []
	for x in xrange(len(data)):
		if x == 0:
			leveraged_security_data.append(data[x])
			continue
		daily_change = ((data[x]-data[x-1]) / data[x-1])
		old = leveraged_security_data[-1]
		new = old * (leverage_rate*daily_change+1)
		leveraged_security_data.append(new)
	return leveraged_security_data
	
	
def AlignData(stk1, stk2, min_backtest_time=-1):
	global SP_PE_ratio
	
	stk1 = [x for x in stk1[1]]
	stk2 = [x for x in stk2[1]]
		
	if min_backtest_time==-1:
		min_backtest_time = min(len(stk1), len(stk2))
		
	t1 = [0.0] * min_backtest_time
	t2 = [0.0] * min_backtest_time
	t3 = [0.0] * min_backtest_time
	
	stk1.reverse()
	stk2.reverse()
	SP_PE_ratio.reverse()
	for x in xrange(min_backtest_time):
		t1[x] = stk1[x]
		t2[x] = stk2[x]
		t3[x] = SP_PE_ratio[x]
	
	stk1 = t1
	stk2 = t2
	SP_PE_ratio = t3
	stk1.reverse()
	stk2.reverse()
	SP_PE_ratio.reverse()
	return stk1, stk2
	
def invest_with_rebalance(stk1, stk2, stock_holding_ratio, window=0.10, back_test_length=-1, leverage_rate = 1, investment_period = 1, chart=True, verify_data_lengths=True, periodic_rebalance="None", rebalance=True):
	daily_investment = 10
	first_stock_shares = 0
	second_stock_shares = 0
	price = 0
	rebalance_fee = 14
	periodic_rebalance_time = max(len(stk1[1]), len(stk2[1]))+1
	
	first_stock_symbol = stk1[0]
	second_stock_symbol = stk2[0]

	if verify_data_lengths==True:
		stk1, stk2 = AlignData(stk1, stk2, min_backtest_time=back_test_length)
		if leverage_rate!=1:
			stk1 = generate_leveraged_data(stk1, leverage_rate)
	else:
		stk1 = stk1[1]
		stk2 = stk2[1]
	
	portfolio_values = [0.0] * (len(stk1)+1)
	first_stock_values = [0.0] * (len(stk1)+1)
	second_stock_values = [0.0] * (len(stk1)+1)
	
	first_stock_values[0] = stock_holding_ratio*10
	second_stock_values[0] = (1-stock_holding_ratio)*10
	portfolio_values[0] = second_stock_values[0] + first_stock_values[0]
	
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
	
	first_stock_shares = 0
	second_stock_shares = 0
	number_of_rebalances_made = 0
	rebalance_window = window
	day = 0
	
	for x,y in zip(stk1, stk2):
		day+=1
		try:
			first_stock_price = x
			daily_first_stock_investment = 0
			if day%investment_period==0:
				daily_first_stock_investment = stock_holding_ratio * daily_investment * investment_period
			daily_first_stock_shares = daily_first_stock_investment/first_stock_price
			first_stock_shares += daily_first_stock_shares
		except ZeroDivisionError:
			daily_first_stock_shares = 0
			first_stock_shares = 0
			
		try:
			second_stock_price = y
			daily_second_stock_investment = 0
			if day%investment_period==0:
				daily_second_stock_investment = (1-stock_holding_ratio) * daily_investment * investment_period
			daily_second_stock_shares = daily_second_stock_investment/second_stock_price
			second_stock_shares += daily_second_stock_shares
		except ZeroDivisionError:
			daily_second_stock_shares = 0
			second_stock_shares = 0
		
		first_stock_values[day] = (first_stock_shares*first_stock_price)
		second_stock_values[day] = (second_stock_shares*second_stock_price)
		portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
	
		if first_stock_price == 0 or second_stock_price == 0: continue
		
		first_stock_portfolio_percent = first_stock_values[day]/portfolio_values[day]
		
		# Rebalance first_stock -> second_stock
		if (first_stock_portfolio_percent > (stock_holding_ratio+rebalance_window) or day%periodic_rebalance_time==0) and rebalance==True:
			number_of_rebalances_made+=1
			target_first_stock_value = stock_holding_ratio * portfolio_values[day]
			# Sell first_stock
			cash_to_sell = first_stock_values[day] - target_first_stock_value
			shares_to_sell = cash_to_sell/first_stock_price
			first_stock_shares -= shares_to_sell
			cash_pool = cash_to_sell-rebalance_fee
			first_stock_values[day] = first_stock_shares*first_stock_price
			# Buy second_stock
			daily_second_stock_shares = cash_pool / second_stock_price
			second_stock_shares+= daily_second_stock_shares
			second_stock_values[day]=(second_stock_shares*second_stock_price)
			portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
			
		# Rebalance second_stock -> first_stock
		if (first_stock_portfolio_percent < (stock_holding_ratio-rebalance_window) or day%periodic_rebalance_time==0)  and rebalance==True:
			#print "Rebalance second_stock -> first_stock"
			number_of_rebalances_made+=1
			target_second_stock_value = (1-stock_holding_ratio) * portfolio_values[day]
			# sell second_stock
			cash_to_sell = second_stock_values[day] - target_second_stock_value
			shares_to_sell = cash_to_sell/second_stock_price
			second_stock_shares -= shares_to_sell
			cash_pool = cash_to_sell-rebalance_fee
			second_stock_values[day] = second_stock_shares*second_stock_price
			# Buy first_stock
			daily_first_stock_shares = cash_pool / first_stock_price
			first_stock_shares += daily_first_stock_shares
			first_stock_values[day] = (first_stock_shares*first_stock_price)
			portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
		
			
	years = len(stk1)/252

	amount_invested = [0.0] * (len(stk1)+1)
	multiplier = 0
	for x in xrange(0, len(stk1)+1):
		if x%investment_period==0: multiplier+=1
		amount_invested[x] = 10*investment_period*multiplier
		
	days = [x/252+(2015-years) for x in xrange(len(stk1)+1)]
	
	if chart==True:
		fig = plt.figure()
		ax = fig.add_subplot('111')

		ax.plot(days, amount_invested, label='Invested Dollars')
		ax.plot(days, first_stock_values, label=first_stock_symbol.upper())
		ax.plot(days, second_stock_values, label=second_stock_symbol.upper())
		ax.plot(days, portfolio_values, label='Total')
		plt.legend(loc='best')
		
		fig.canvas.show()
		return portfolio_values[-1], number_of_rebalances_made
	else:
		return portfolio_values[-1], number_of_rebalances_made
		
def InvestWithRebalancingUsingPERatios(stk1, stk2, back_test_length=-1, leverage_rate = 1, investment_period = 1, chart=True, verify_data_lengths=True, PriceToEarningsEquityThreshold = 15):
	global SP_PE_ratio
	daily_investment = 10
	first_stock_shares = 0
	second_stock_shares = 0
	price = 0
	rebalance_fee = 14
	
	first_stock_symbol = stk1[0]
	second_stock_symbol = stk2[0]

	if verify_data_lengths==True:
		stk1, stk2 = AlignData(stk1, stk2, min_backtest_time=back_test_length)
		if leverage_rate!=1:
			stk1 = generate_leveraged_data(stk1, leverage_rate)
	else:
		stk1 = stk1[1]
		stk2 = stk2[1]
	
	portfolio_values = [0.0] * (len(stk1)+1)
	first_stock_values = [0.0] * (len(stk1)+1)
	second_stock_values = [0.0] * (len(stk1)+1)
	
	first_stock_values[0] = 10
	second_stock_values[0] = 10
	portfolio_values[0] = second_stock_values[0] + first_stock_values[0]
	
	first_stock_shares = 0
	second_stock_shares = 0
	number_of_rebalances_made = 0
	day = 0
	
	for x,y in zip(stk1, stk2):
		day+=1
		if SP_PE_ratio[day-1] > PriceToEarningsEquityThreshold:
			stock_holding_ratio = 0
		else:
			stock_holding_ratio = 1
		
		try:
			first_stock_price = x
			daily_first_stock_investment = 0
			if day%investment_period==0:
				daily_first_stock_investment = stock_holding_ratio * daily_investment * investment_period
			daily_first_stock_shares = daily_first_stock_investment/first_stock_price
			first_stock_shares += daily_first_stock_shares
		except ZeroDivisionError:
			daily_first_stock_shares = 0
			first_stock_shares = 0
			
		try:
			second_stock_price = y
			daily_second_stock_investment = 0
			if day%investment_period==0:
				daily_second_stock_investment = (1-stock_holding_ratio) * daily_investment * investment_period
			daily_second_stock_shares = daily_second_stock_investment/second_stock_price
			second_stock_shares += daily_second_stock_shares
		except ZeroDivisionError:
			daily_second_stock_shares = 0
			second_stock_shares = 0
		
		first_stock_values[day] = (first_stock_shares*first_stock_price)
		second_stock_values[day] = (second_stock_shares*second_stock_price)
		portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
	
		if first_stock_price == 0 or second_stock_price == 0: continue
		
		first_stock_portfolio_percent = first_stock_values[day]/portfolio_values[day]
		
		# Rebalance first_stock -> second_stock
		if SP_PE_ratio[day-1] > PriceToEarningsEquityThreshold and first_stock_shares>0:
			number_of_rebalances_made+=1
			target_first_stock_value = 0
			# Sell first_stock
			cash_to_sell = first_stock_values[day] - target_first_stock_value
			shares_to_sell = cash_to_sell/first_stock_price
			first_stock_shares -= shares_to_sell
			cash_pool = cash_to_sell-rebalance_fee
			first_stock_values[day] = first_stock_shares*first_stock_price
			# Buy second_stock
			daily_second_stock_shares = cash_pool / second_stock_price
			second_stock_shares+= daily_second_stock_shares
			second_stock_values[day]=(second_stock_shares*second_stock_price)
			portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
			
		# Rebalance second_stock -> first_stock
		if SP_PE_ratio[day-1] < PriceToEarningsEquityThreshold and second_stock_shares>0:
			number_of_rebalances_made+=1
			target_second_stock_value = 0
			# sell second_stock
			cash_to_sell = second_stock_values[day] - target_second_stock_value
			shares_to_sell = cash_to_sell/second_stock_price
			second_stock_shares -= shares_to_sell
			cash_pool = cash_to_sell-rebalance_fee
			second_stock_values[day] = second_stock_shares*second_stock_price
			# Buy first_stock
			daily_first_stock_shares = cash_pool / first_stock_price
			first_stock_shares += daily_first_stock_shares
			first_stock_values[day] = (first_stock_shares*first_stock_price)
			portfolio_values[day] = (first_stock_shares*first_stock_price + second_stock_shares*second_stock_price)
		
			
	years = len(stk1)/252

	amount_invested = [0.0] * (len(stk1)+1)
	multiplier = 0
	for x in xrange(0, len(stk1)+1):
		if x%investment_period==0: multiplier+=1
		amount_invested[x] = 10*investment_period*multiplier
		
	days = [x/252+(2015-years) for x in xrange(len(stk1)+1)]
	
	if chart==True:
		fig = plt.figure()
		ax = fig.add_subplot('111')

		ax.plot(days, amount_invested, label='Invested Dollars')
		ax.plot(days, first_stock_values, label=first_stock_symbol.upper())
		ax.plot(days, second_stock_values, label=second_stock_symbol.upper())
		ax.plot(days, portfolio_values, label='Total')
		plt.legend(loc='best')
		
		fig.canvas.show()
		return portfolio_values[-1], number_of_rebalances_made
	else:
		return portfolio_values[-1], number_of_rebalances_made
		
def generate_chart_manual_window():
	stk1 = raw_input("Enter Stock 1: ")
	stk2 = raw_input("Enter Stock 2: ")
	stock1_leverage_rate = float(raw_input("Stock 1 Leverage: "))
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
	
	invest_with_rebalance(stocks[0], stocks[1], stock_holding_ratio=ratio, window=window_rebalance, leverage_rate=stock1_leverage_rate, rebalance=True, chart=True, periodic_rebalance=periodic_rebalance)

		
def generate_chart_manual_PriceToEarnings():
	stk1 = raw_input("Enter Stock 1: ")
	stk2 = raw_input("Enter Stock 2: ")
	stock1_leverage_rate = float(raw_input("Stock 1 Leverage: "))
	PriceToEarningsEquityThreshold = float(raw_input("Enter threshold P/E level: "))
	
	stocks = []
	t1 = pull_historical_data(stk1)
	t2 = pull_historical_data(stk2)
	t1 = get_data(t1)
	t2 = get_data(t2)
	stocks.append((stk1.upper(), t1))
	stocks.append((stk2.upper(), t2))
	
	InvestWithRebalancingUsingPERatios(stocks[0], stocks[1], leverage_rate=stock1_leverage_rate, PriceToEarningsEquityThreshold = PriceToEarningsEquityThreshold)

def findOptimalPriceToEarningsThreshold():
	stk1 = raw_input("Enter Stock 1: ")
	stk2 = raw_input("Enter Stock 2: ")
	stock1_leverage_rate = float(raw_input("Stock 1 Leverage: "))
	
	stocks = []
	t1 = pull_historical_data(stk1)
	t2 = pull_historical_data(stk2)
	t1 = get_data(t1)
	t2 = get_data(t2)
	stocks.append((stk1.upper(), t1))
	stocks.append((stk2.upper(), t2))
	
	returns = []
	for x in xrange(5,40,1):
		for y in xrange(x, 40, 1):
			PriceToEarningsEquityThreshold = (x,y)
			localReturn = InvestWithRebalancingUsingPERatios(stocks[0], stocks[1], leverage_rate=stock1_leverage_rate, PriceToEarningsEquityThreshold = PriceToEarningsEquityThreshold, chart=False)
			returns.append((PriceToEarningsEquityThreshold, localReturn[0]))
		
	returns.sort(key=lambda x: x[1])
	returns.reverse()
	for k in returns:
		print k[0], " : ", k[1]
	
	
def ReadInSPPriceToEarnings():
	global SP_PE_ratio
	
	stock_data = []
	with open(".\\Stocks\\shiller_pe.csv", 'rb') as input:
		input.next()
		stock_data = [float(x.split(',')[-1]) for x in input]
		t = [0.0] * (len(stock_data)*21)
		for count,x in enumerate(stock_data):
			for y in xrange(21):
				t[count*21+y] = x
		stock_data = t
	
	stock_data.reverse()
	SP_PE_ratio = stock_data
	
def chooseRebalancingMethod():
	method = raw_input("Choose Rebalancing Method: [P/E, Window, Optimal P/E]\t")
	return method
	
if __name__ == '__main__':
	ReadInSPPriceToEarnings()
	method = chooseRebalancingMethod()
	if method == "P/E":
		generate_chart_manual_PriceToEarnings()
	elif method == "Window":
		generate_chart_manual_window()
	elif method == "Optimal P/E":
		findOptimalPriceToEarningsThreshold()
	raw_input()

	
	
