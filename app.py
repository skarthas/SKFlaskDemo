from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
from bokeh.plotting import figure,show,ColumnDataSource
from bokeh.embed import components
from bokeh.resources import INLINE
import pandas as pd
import numpy as np
import holidays
from datetime import datetime,timedelta
import os

app = Flask(__name__)

app.vars={}

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index',methods=['Get','POST'])
def indexes():
  if request.method == 'GET':
  	return render_template('index.html')
  else:
	app.vars['tickername'] = request.form['ticker']
	app.vars['close'] = request.form.get('cprice')
	app.vars['aclose'] = request.form.get('acprice')
	app.vars['open'] = request.form.get('oprice')
	app.vars['aopen'] = request.form.get('aoprice')
	return redirect('/graphing')	

@app.route('/graphing',methods=['GET'])
def graphing():
  now = datetime.now()-timedelta(days=1)
  while (now in holidays.UnitedStates() or now.weekday()>4):
	now = now-timedelta(days=1)
  past = now-timedelta(days=30)
  while (past in holidays.UnitedStates() or past.weekday()>4):
        past = past-timedelta(days=1)
  print(past)

  api_url='https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=%s&qopts.columns=date,open,close,adj_open,adj_close&date.gte=%s&date.lt=%s&api_key=zTJsP31gZnkKyDXYG5DD' % (app.vars['tickername'],past.strftime("%Y%m%d"),now.strftime("%Y%m%d"))
  session = requests.Session()
  session.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
  raw_data = session.get(api_url)

  data = raw_data.json()
  pdf = pd.DataFrame(data['datatable']['data'],columns=['dates','open','close','adj_open','adj_close'])
  pdf['dates']=pd.to_datetime(pdf['dates'])
  ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
  plot = figure(title='Data from Quandle WIKI set',x_axis_label='date',x_axis_type='datetime')

  if(app.vars['close']):
	plot.line(x=pdf['dates'],y=pdf['close'],legend='%s:Close'%app.vars['tickername'],color="blue") 

  if(app.vars['aclose']):  
        plot.line(x=pdf['dates'],y=pdf['adj_close'],legend='%s:Adj. Close'%app.vars['tickername'],color="green")  
 
  if(app.vars['open']):
        plot.line(x=pdf['dates'],y=pdf['open'],legend='%s:Open'%app.vars['tickername'],color="orange")

  if(app.vars['aopen']):
        plot.line(x=pdf['dates'],y=pdf['adj_open'],legend='%s:Adj. Open'%app.vars['tickername'],color="red")

  js_resources = INLINE.render_js()
  css_resources = INLINE.render_css()
  script, div = components(plot)

  return render_template('graph2.html',plot_script=script,plot_div=div, js_resources=js_resources, css_resources=css_resources, ticker=app.vars['tickername'])
	

  
if __name__ == '__main__':
  app.run(port=33507,debug=True)
