import calendar
import warnings
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show, curdoc
from datetime import datetime, date
from bokeh.layouts import layout, widgetbox, column, row, gridplot
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs, Button

hv.extension('bokeh', logo=False)
renderer = hv.renderer('bokeh')
warnings.filterwarnings("ignore")
#output_file('ContextGrid_App.html')

def disable_logo(plot, element):
    plot.state.toolbar.logo = None
hv.plotting.bokeh.ElementPlot.finalize_hooks.append(disable_logo)

from main import fetch
'''
query = ("""SELECT * FROM cg_sessions.session_event ORDER BY id""") 
bigquery = fetch.import_data(query)
data = bigquery.data_output()
'''
data = pd.read_csv("cg_sessions_covid_updated.csv")
data = data.drop(columns=["Unnamed: 0"])
data['start_date'] = data['start_time'].apply(lambda x:x.split()[0])
data['end_date'] = data['end_time'].apply(lambda x:x.split()[0])
data['start_time'] = pd.to_datetime(data['start_time'])
data['start_day'] = data['start_time'].apply(lambda x:x.day)
data['start_month'] = data['start_time'].apply(lambda x:x.month)
data['start_hour'] = data['start_time'].apply(lambda x:x.hour)
data['start_minute'] = data['start_time'].apply(lambda x:x.minute)
data['end_time'] = pd.to_datetime(data['end_time'])
data['end_hour'] = data['end_time'].apply(lambda x:x.hour)
data['end_minute'] = data['end_time'].apply(lambda x:x.minute)
data['Avg_session'] = data['end_minute'] - data['start_minute']

from Charts import heatmap

hm = heatmap.heatmap(data).plot_heatmap()
print("Heatmap Live")
'''
from Charts import barchart

bar = barchart.bars(data).plot_barchart()
print("Barchart Live")
'''
from Charts import test_covid

main_page = test_covid.mainplot(data)
sketch = main_page.prepare()
inputs = main_page.final_sketch()
div1 = Div(text = """<html>
   <head>
      <style type="text/css">
                 body {
            padding: 0in; 
         }
         .square {
         position: relative;
            background-color: #E0E0E0;
            width: 1500px;
            height: 80px;
            border: 0px;
         }
         .square p{
          font-size:30pt;
          margin: 0;
          background: #E0E0E0;
          position: relative;
          top: -90%;
          left: -26%;
          text-align: center;
          margin:auto;
          padding:0;
          height:5%;
          font-family:Roboto;
          color:#2097BE;
      width:55%;
      transform: translate(50%, 50%)   
         }
      </style>
   </head>
   <body>
      <div class="square">
      <img src="https://github.com/dhaval8895/HGL_logo/blob/master/logo.png?raw=true", width = 85, height = 85>
      <p>HealthGrid Alliance Dashboard</p></div>
   </body>
</html>""")
#plot_layout = layout([[inputs, sketch[0]]], sizing_mode='fixed')
#div2 = Div(text="""<img src="https://www.dropbox.com/s/dnmgcb2373f0xpd/4.png" alt="div_image">""", width=150, height=150)
plot_layout = column(div1, inputs, row(sketch[0], sketch[1]), row(hm, sketch[2]))
main_page.update()
print("Home Layout Live")
##
'''
from Charts import piechart
pie = piechart.pie(data).plot_pie()
print("Pie chart live")
'''




#tab1 = Panel(child = plot_layout, title = "Home")
#tab2 = Panel(child = hm, title = "Heatmap")
#tab3 = Panel(child = bar, title="Bar Chart")
#tabs = Tabs(tabs=[tab1, tab2, tab3])
curdoc().add_root(plot_layout)
curdoc().title = "HEALTHGRID ALLIANCE DASHBOARD"
