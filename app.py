from flask import Flask, render_template, request, redirect
import requests
from dotenv import load_dotenv
import os

import pandas as pd
from math import pi
import numpy as np

from bokeh.io import output_file
from bokeh.plotting import figure
from bokeh.layouts import row,column

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.palettes import Dark2 as palette

app = Flask(__name__)
app.vars={}
app.vars['price_checked']=[]
app.vars['analysis_checked']=[]

try:  
    api_key=os.environ.get("API_KEY")
except: 
    load_dotenv()
    api_key=os.environ.get("API_KEY")

company_list=pd.read_table('static/NASDAQ.txt')

@app.route('/')
def root(): 
  return render_template('index.html')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        ticker = request.form['name_stock'].upper() 

        app.vars['price_checked']=[]
        for p in ['price_type%i'%i for i in range(1,5)]:
            if request.form.get(p) != None: 
                app.vars['price_checked'].append(True)
            else: 
                app.vars['price_checked'].append(False)

        app.vars['analysis_checked']=[]
        for p in ['analysis_type%i'%i for i in range(1,6)]:
            if request.form.get(p) != None: 
                app.vars['analysis_checked'].append(True)
            else: 
                app.vars['analysis_checked'].append(False)
        
        if ticker not in company_list['Symbol'].values:
            return 'Please enter a valid stock symbol'

        ticker_desc = list(company_list[company_list['Symbol']==ticker]['Description'])[0]        

        script1, div1, script2, div2, script3, div3 = create_bokeh(ticker=ticker,price_checked_list=app.vars['price_checked'], analysis_checked_list=app.vars['analysis_checked'])

        return render_template("plot_bokeh.html", div1=div1,script1=script1, div2=div2,script2=script2, script3=script3, div3=div3, ticker=ticker , ticker_desc=ticker_desc)
    

@app.route('/about')
def about():
    return render_template('about.html')


def get_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={api_key}&datatype=csv'
    df = pd.read_csv(url)
    df = df[::-1].reset_index(drop=True)
    df['timestamp']=pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    df['daily_returns']=df['adjusted_close'].pct_change()
    df['monthly_returns']=df['adjusted_close'].asfreq('BM').pct_change(1)
    df['monthly_returns']=df['monthly_returns'].interpolate( limit_area='inside')
    df['yearly_returns']=df['adjusted_close'].asfreq('BY').pct_change(1)
    df['yearly_returns']=df['yearly_returns'].interpolate( limit_area='inside')
    df['daily_log_returns']=np.log1p(df['daily_returns'])
    df['annualized_volatility']=df['daily_log_returns'].rolling(window=252).std() * np.sqrt(252)
    df['momentum_12_1']=df['adjusted_close'].asfreq('MS').ffill().shift(1).pct_change(11)
    df['momentum_12_1']=df['momentum_12_1'].interpolate( limit_area='inside')

    df['moving_avg_21']=df['adjusted_close'].rolling(window=21).mean()
    df['moving_avg_50']=df['adjusted_close'].rolling(window=50).mean()
    df['moving_avg_200']=df['adjusted_close'].rolling(window=200).mean()
    return df



def create_bokeh(ticker,price_checked_list,analysis_checked_list):
    df=get_data(ticker)
    TOOLS = 'pan, wheel_zoom, box_zoom, reset, save'

    price_types=['open', 'high', 'low', 'adjusted_close']
    price_names=['Opening','Highest','Lowest','Adjusted closing']
    
    plot_options = dict(x_axis_type="datetime",plot_width=900, plot_height=400, tools = TOOLS)
    title="{}'s Historical prices".format(ticker)
    p1 = figure(title=title,**plot_options)
    
    p1.xaxis.axis_label = "Date"
    p1.yaxis.axis_label = "Price ($)"
    p1.xaxis.major_label_orientation = pi/4

    for i,price in enumerate(price_types):
        if price_checked_list[i]:
            p1.line(df.index,df[price],legend=price_names[i],color=palette[len(price_types)][i],line_width=2)
        else: 
            pass
    
    script1, div1 = components(p1)

    analysis_types=['daily_returns', 'monthly_returns', 'yearly_returns', 'annualized_volatility','momentum_12_1' ]
    analysis_names=['Daily Returns','Monthly Returns','Yearly Returns','Annualized Volatility', 'Daily 12-1 Price Momentum Signal' ]

    title="{}'s Analysis".format(ticker)
    p2 = figure(title=title,**plot_options)
    
    p2.xaxis.axis_label = "Date"
    p2.xaxis.major_label_orientation = pi/4

    for i,analysis in enumerate(analysis_types):
        if analysis_checked_list[i]:
            p2.line(df.index,df[analysis],legend=analysis_names[i],color=palette[len(analysis_types)][i],line_width=2)
        else: 
            pass
    

    script2, div2 = components(p2)


    title="{} Candlestick".format(ticker)
    p3 = figure(title=title,**plot_options)

    inc = df.close > df.open
    dec = df.open > df.close
    w = 12*60*60*1000 # half day in ms

    p3.xaxis.major_label_orientation = pi/4
    p3.grid.grid_line_alpha=0.3

    p3.segment(df.index, df.high, df.index, df.low, color="black")
    p3.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color="#17BECF", line_color="black")
    p3.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color="#7F7F7F", line_color="black")

    p3.line(df.index, df['moving_avg_21'], legend='21 Day Moving Avg',line_width=2, line_dash='dashed', color=palette[3][1])
    p3.line(df.index, df['moving_avg_50'], legend='50 Day Moving Avg',line_width=2, line_dash='dashed', color=palette[3][2])
    p3.line(df.index, df['moving_avg_200'], legend='200 Day Moving Avg',line_width=2, line_dash='dashed', color=palette[3][3])

    script3, div3 = components(p3)

    return script1, div1, script2, div2, script3, div3

if __name__ == "__main__":
    app.run(debug=True)
