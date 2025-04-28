#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import backtrader as bt
import backtrader.analyzers as btanalyzers
import matplotlib.pyplot as plt

# Define the SMA Strategy
class SMAStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),  # Fast moving average period
        ('slow_period', 20),  # Slow moving average period
    )

    def log(self, txt, dt=None):
        """Logging function for the strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def __init__(self):
        # Keep references to the "close" lines in the data dataseries
        self.vti_close = self.datas[0].close
        self.tlt_close = self.datas[1].close
        
        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # Add SMA indicators for VTI (data[0])
        self.vti_fast_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period)
        
        self.vti_slow_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period)
        
        # Add SMA indicators for TLT (data[1])
        self.tlt_fast_sma = bt.indicators.SimpleMovingAverage(
            self.datas[1], period=self.params.fast_period)
        
        self.tlt_slow_sma = bt.indicators.SimpleMovingAverage(
            self.datas[1], period=self.params.slow_period)
        
        # Indicators for the plotting show
        bt.indicators.CrossOver(self.vti_fast_sma, self.vti_slow_sma)
        bt.indicators.CrossOver(self.tlt_fast_sma, self.tlt_slow_sma)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        # Log the closing prices of both assets
        self.log(f'VTI Close: {self.vti_close[0]:.2f}, TLT Close: {self.tlt_close[0]:.2f}')

        # Check if an order is pending... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet... we MIGHT BUY VTI if...
            if self.vti_fast_sma[0] > self.vti_slow_sma[0] and self.vti_fast_sma[-1] <= self.vti_slow_sma[-1]:
                self.log(f'BUY VTI CREATE, {self.vti_close[0]:.2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(data=self.datas[0])
            # Or we MIGHT BUY TLT if...
            elif self.tlt_fast_sma[0] > self.tlt_slow_sma[0] and self.tlt_fast_sma[-1] <= self.tlt_slow_sma[-1]:
                self.log(f'BUY TLT CREATE, {self.tlt_close[0]:.2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(data=self.datas[1])

        else:
            # Already in the market... we might sell
            # Check which asset we're holding (VTI or TLT)
            if self.getposition(self.datas[0]).size > 0:  # Holding VTI
                if self.vti_fast_sma[0] < self.vti_slow_sma[0] and self.vti_fast_sma[-1] >= self.vti_slow_sma[-1]:
                    self.log(f'SELL VTI CREATE, {self.vti_close[0]:.2f}')
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell(data=self.datas[0])
            elif self.getposition(self.datas[1]).size > 0:  # Holding TLT
                if self.tlt_fast_sma[0] < self.tlt_slow_sma[0] and self.tlt_fast_sma[-1] >= self.tlt_slow_sma[-1]:
                    self.log(f'SELL TLT CREATE, {self.tlt_close[0]:.2f}')
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell(data=self.datas[1])


def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(SMAStrategy)

    # Get the data directory
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # Check if the data directory exists
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist. Please run download_historical_data.py first.")
        return
    
    # Path to the VTI data file
    vti_data_path = os.path.join(data_dir, "VTI_data.csv")
    
    # Check if the VTI data file exists
    if not os.path.exists(vti_data_path):
        print(f"VTI data file {vti_data_path} does not exist. Please run download_historical_data.py first.")
        return
    
    # Path to the TLT data file
    tlt_data_path = os.path.join(data_dir, "TLT_data.csv")
    
    # Check if the TLT data file exists
    if not os.path.exists(tlt_data_path):
        print(f"TLT data file {tlt_data_path} does not exist. Please run download_historical_data.py first.")
        return
    
    # Create a Data Feed for VTI using GenericCSVData
    vti_data = bt.feeds.GenericCSVData(
        dataname=vti_data_path,
        # Do not pass values before this date
        fromdate=datetime.datetime(2020, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2025, 12, 31),
        # CSV Format specification
        dtformat='%Y-%m-%d',     # Date format
        datetime=0,              # Date is in column 0
        open=1,                  # Open price is in column 1
        high=2,                  # High price is in column 2
        low=3,                   # Low price is in column 3
        close=4,                 # Close price is in column 4
        volume=5,                # Volume is in column 6
        openinterest=-1,         # No open interest data
        reverse=False)
    
    # Create a Data Feed for TLT using GenericCSVData
    tlt_data = bt.feeds.GenericCSVData(
        dataname=tlt_data_path,
        # Do not pass values before this date
        fromdate=datetime.datetime(2020, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2025, 12, 31),
        # CSV Format specification
        dtformat='%Y-%m-%d',     # Date format
        datetime=0,              # Date is in column 0
        open=1,                  # Open price is in column 1
        high=2,                  # High price is in column 2
        low=3,                   # Low price is in column 3
        close=4,                 # Close price is in column 4
        volume=5,                # Volume is in column 6
        openinterest=-1,         # No open interest data
        reverse=False)

    # Add the Data Feeds to Cerebro
    cerebro.adddata(vti_data, name='VTI')
    cerebro.adddata(tlt_data, name='TLT')

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission - 0.25% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.0025)

    # Add analyzers
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()
    strat = results[0]

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # Print analyzer results
    print('Sharpe Ratio:', strat.analyzers.sharpe.get_analysis())
    print('Drawdown:', strat.analyzers.drawdown.get_analysis())
    print('Returns:', strat.analyzers.returns.get_analysis())

    # Plot the result
    plt.style.use('dark_background')
    figs = cerebro.plot(style='candlestick', barup='green', bardown='red', 
                 plotdist=1.0, volume=False, 
                 barupfill=False, bardownfill=False,
                 valuetags=True, numfigs=2)  # Use numfigs=2 to plot each data feed separately


if __name__ == "__main__":
    main()
