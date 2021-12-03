# Flask on Heroku

![stockanalysis_animation](https://user-images.githubusercontent.com/79766032/144130802-b3e6776f-e25c-4a6f-bff0-ad34b3a8e3a3.gif)

This code grabs stock data from the alphavantage dataset and puts it into a pandas dataframe to be plotted via Bokeh embedding. Flask is used to tie the code to html and the app is deployed via Heroku. You can view my completed Heroku app [here](https://hevren-stock-analysis.herokuapp.com/). The app takes ticker, year, and various price metrics as inputs and outputs a time-series plot.

The repository contains a basic template for a Flask configuration that will
work on Heroku.

Price plots: Opening, Highest, Lowest, Adjusted closing

Analysis plots: Daily Returns, Monthly Returns, Yearly Returns, Annualized Volatility, Daily 12-1 Price Momentum Signal

## Installation and Usage

  - Git clone the existing template repository.
  - Procfile, requirements.txt, conda-requirements.txt, and runtime.txt contain some default settings.
  - Install Flask
    ```$ pip install flask```
  - Install virtualenv to manage dependencies :
    ```$ pip install virtualenv ```
    ```pip install -r requirements.txt ```
  - To launch the app:
    ``` python app.py ```
  - Once the Flask app is running, navigate to the `localhost` link provided:
    <code> * Running on <b>http://127.0.0.1:5000/</b> (Press CTRL+C to quit)</code>
