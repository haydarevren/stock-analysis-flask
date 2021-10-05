# Flask on Heroku

Welcome to my milestone project for the TDI 12-day course! This code grabs stock data from the alphavantage dataset and puts it into a pandas dataframe to be plotted via Bokeh embedding. Flask is used to tie the code to html and the app is deployed via Heroku. You can view my completed Heroku app [here](https://hevren-stock-analysis.herokuapp.com/). The app takes ticker, year, and various price metrics as inputs and outputs a time-series plot.

The repository contains a basic template for a Flask configuration that will
work on Heroku.

Price plots: Opening, Highest, Lowest, Adjusted closing
Analysis plots: Daily Returns, Monthly Returns, Yearly Returns, Annualized Volatility, Daily 12-1 Price Momentum Signal
