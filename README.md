# forever-transaction
Plot key metrics for Subscription Model Business to determine the 'health' of the subscriber base.

Download the python script, put it in a map together with a 'data' folder, where you add the input data, and an 'output' folder where the plots and csv are saved.

The input data should have one row per transaction and contain the following columns:
CustomerId: the unique id of each customer (string)
Time: the data for each transaction (datetime)
Price: the revenue associated to each transaction (float)
