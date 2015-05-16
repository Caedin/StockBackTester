This program charts investment strategies comparing two different stocks.

Dependencies:
	Python 2.7, matplotlib, urllib

Input methods:
	You can run the program in two ways.
	
		Method 1: Manual Input
			To run the program this way simply run "python backtest.py" or double click the python file. You will be prompted to fill out the above options, after which
			the program will download data if needed and then display the chart.
		
		Method 2: Command line
			To run the program this way run the program with the following command line options: "python backtest.py <Stock 1> <Stock 2> <Ratio> <Periodic Rebalance> <Window of Rebalancing>"
			
			For example, "python backtest.py AAPL GOOG 0.75 None 0.1"
				This runs the program holding 75% of the portfolio in Apple and 25% in Google. The program will not periodically rebalance, but will rebalance if AAPL becomes 
				greater than 85% or less than 65% of the portfolios max value.

Options:
	Stock 1, Stock 2: 
		There are two ticker symbols. The data is downloaded from Yahoo Finance, so the symbol must be recognized on their site. Some index symbols don't work.
		If you want to use some data that isn't available from Yahoo Finance you can download it manually and put it in the Stock folder. Ensure the data is in
		the same format as the other files, and is in the right order.
	
	Ratio:
		This is the ratio that the simulation will invest in. For example, if you input 0.6 the program will spend 60% of its investment on stock 1 and 40% on stock
		two in purchase. This is also the "target ratio". So when you rebalance, the program will sell some of Stock 1 or 2 and buy the other to bring the portfolio balance
		back to 60% and 40%, or whatever input you provide.
	
	Periodic Rebalance:
		This is used if you want to rebalance the portfolio back to the target ratio on some specific periodic time. The options are None, Daily, Weekly, Monthly, Quarterly, Yearly.
		Please capitalize the first letter and spell the word correctly, I didn't write any error checking, so if it is not exactly as it appears above it will default to "None".
	
	Window of Rebalancing: This value represents the maximum amount your portfolio can deviate from the target ratio before it will execute a rebalancing event. For example,
		If your window of rebalancing is 0.1 and your target ratio is 0.6, and you have chosen AAPL as stock 1 and GOOG as stock 2, if the price of AAPL rises so that it is above
		70% of your portfolio, or falls to below 50% of your portfolio, it will rebalance back to 60% AAPL and 40% GOOG.
	
Other Interesting Information:
	The program will fetch stock data for the two stocks from Yahoo. It will then synchronize the data and begin running the experiment from the furthest back point in history
	the two stocks share. So if a stock was brought onto the market in 2004 and another in 2006 the back testing will run 2006 - 2015.
	
	I've included S&P data and the price of gold from 1950 to 2015 in the stocks folder. This can be accessed by using "SP_daily" and "gold" in the program inputs.
	
	The program simulates investing $10 per day, into the two stocks at the ratio you define. It assumes you can purchase partial shares and has no commission costs on purchases.
	There is code in place to do investments every X period such as monthly or yearly instead of daily but is not provided in the input. If you know python it should be easy to see
	how to use it. Simply pass in an input argument for the optional parameter investment_period. This is counts as the number of days between investments. A value of 10 would 
	be $100 invested every 10 trading days (2 weeks).
	
	Rebalancing incurs a cost of $14, one $7 charge to sell and one $7 charge to buy. To change this value change the following line of code: "rebalance_fee = 14" line 98.
	
	
Contact:
	If you have trouble, ideas for future work, or comments please contact me at kwdyer@uh.edu. Thank you!
