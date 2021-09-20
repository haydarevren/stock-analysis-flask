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
app.vars['analysis_checked']=[]

company_list=pd.read_table('static/NASDAQ.txt')

@app.route('/')
def root(): 
  return render_template('index.html')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        app.vars['stock_name'] = request.form['name_stock'].str.upper()

        if app.vars['stock_name'] not in company_list['Symbol'].values:
            return 'Please enter a valid stock symbol'

        app.vars['price_checked']=[]
        for p in ['price_type%i_name'%i for i in range(1,5)]:
            if request.form.get(p) != None: app.vars['price_checked'].append(True)
            else: app.vars['price_checked'].append(False)
        
        app.vars['analysis_checked']=[]
        for p in ['analysis_type%i_name'%i for i in range(1,6)]:
            if request.form.get(p) != None: app.vars['analysis_checked'].append(True)
            else: app.vars['analysis_checked'].append(False)
        
        script1, div1, script2, div2 = create_bokeh(ticker=app.vars['stock_name'],price_checked_list=app.vars['price_checked'], analysis_checked_list=app.vars['analysis_checked'])

        return render_template("plot_bokeh.html", div1=div1,script1=script1, div2=div2,script2=script2 ,company=list(company_list[company_list['Symbol']==app.vars['stock_name'] ]['Description'])[0])
    

@app.route('/about')
def about():
    return render_template('about.html')


def get_data(ticker):
    try:  
        api_key=os.environ.get("API_KEY")
    except: 
        load_dotenv()
        api_key=os.environ.get("API_KEY")
        
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
    p1.xaxis.major_label_orientation = math.pi/4

    for i,price in enumerate(price_types):
        if price_checked_list[i]:
            p1.line(df.index,df[price],legend=price_names[i],color=palette[len(price_types)][i],line_width=2)
        else: 
            pass
    
    script1, div1 = components(p1)

    analysis_types=['daily_returns', 'monthly_returns', 'yearly_returns', 'annualized_volatility','momentum_12_1' ]
    analysis_names=['Daily Returns','Monthly Returns','Yearly Returns','Annualized Volatility', 'Daily 12-1 Price Momentum Signal' ]

    plot_options = dict(x_axis_type="datetime",plot_width=900, plot_height=400, tools = TOOLS)
    title="{}'s Analysis".format(ticker)
    p2 = figure(title=title,**plot_options)
    
    p2.xaxis.axis_label = "Date"
    p2.xaxis.major_label_orientation = math.pi/4

    for i,analysis in enumerate(analysis_types):
        if analysis_checked_list[i]:
            p2.line(df.index,df[analysis],legend=analysis_names[i],color=palette[len(analysis_types)][i],line_width=2)
        else: 
            pass
    

    script2, div2 = components(p2)

    return script1, div1, script2, div2


if __name__ == "__main__":
    app.run(debug=True)
