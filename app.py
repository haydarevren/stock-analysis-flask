from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import math
import numpy as np

from dotenv import load_dotenv
import os

from bokeh.io import output_file
from bokeh.plotting import figure
from bokeh.layouts import row,column

from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.palettes import Dark2 as palette


app = Flask(__name__)
app.vars={}
app.vars['price_checked']=[]

@app.route('/')
def root(): 
  return render_template('index.html')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        ticker = request.form['name_stock'].str.upper()

        app.vars['price_checked']=[]
        for p in ['price_type%i_name'%i for i in range(1,5)]:
            if request.form.get(p) != None: app.vars['price_checked'].append(True)
            else: app.vars['price_checked'].append(False)

        # nasdaq_list=pd.read_table('static/nasdaq.txt')
        # if ticker not in nasdaq_list['Symbol'].values:
        #     return 'Please enter a valid stock symbol'
        ticker_description = 'sas'
        script, div = create_bokeh(ticker=ticker, ticker_description=ticker_description, price_checked_list=app.vars['price_checked'])
        return render_template("plot_bokeh.html", ticker_description=ticker_description, div=div,script=script)
    

@app.route('/about')
def about():
    return render_template('about.html')


def get_data(ticker):
    try:    key=os.environ.get("API_KEY")
    except: 
        load_dotenv()
        key=os.environ.get("API_KEY")
        
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
    response = requests.get(url)
    response = response.json()
    df=pd.DataFrame(response['Time Series (Daily)']).transpose().astype(float)
    
    df['Date']=pd.to_datetime(df.index)
    return df


def create_bokeh(ticker,ticker_description,price_checked_list):
    price_types=['1. open', '2. high', '3. low', '5. adjusted close']
    price_names=['Opening','Highest','Lowest','Adjusted closing']
    df=get_data(ticker)

    TOOLS = 'pan, wheel_zoom, box_zoom, reset, save'

    plot_options = dict(x_axis_type="datetime",plot_width=900, plot_height=400, tools = TOOLS)

    

    title="{}'s Historical prices".format(ticker_description)
    p = figure(title=title,**plot_options)
    
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price ($)"
    p.xaxis.major_label_orientation = math.pi/4

    for i,price in enumerate(price_types):
        if price_checked_list[i]:
            p.line(df['Date'],df[price],legend=price_names[i],color=palette[len(price_types)][i],line_width=2)
        else: 
            pass
    

    fig=p
    
    script, div = components(fig)
    return script, div



if __name__ == "__main__":
    app.run(debug=True)
