# forever-transaction
Plot key metrics for Subscription Model Business to determine the 'health' of the subscriber base.

Download the python script, put it in a map together with a 'data' folder, where you add the input data, and an 'output' folder where the plots and csv are saved.

The input data should have one row per transaction and contain the following columns:
<ul>
<li>CustomerId: the unique id of each customer (string)
<li>Time: the data for each transaction (datetime)
<li>Price: the revenue associated to each transaction (float)
</ul>
The output is a csv-file that summarizes the data month by month, and five png's plotting Acquisition, Retention (churn rate and # churned customers), Monetization (ARPU and LTV), Growth (MRR and Growth rate) and the Forever Transaction Indicator (FT).
