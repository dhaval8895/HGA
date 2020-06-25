import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show
from datetime import datetime, date
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs
from bokeh.io import curdoc, output_file, show
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider, DatetimeTickFormatter, FactorRange

renderer = hv.renderer('bokeh')

class heatmap:
    def __init__(self, df):
        self.data = df
        #print(self.data.info())
        self.data['Weekday'] = self.data['start_time'].apply(lambda x:x.strftime("%a"))
        self.data['Hour'] = self.data['start_time'].apply(lambda x:x.strftime("%I %p"))
    def plot_heatmap(self):
        ##Stacked Bar chart for Day and Event Type
        self.day_hour = self.data.groupby(by = ['Weekday', 'Hour']).agg({'Weekday': 'count'}).rename(
            columns = {'Weekday':'Sessions'}
        )
        self.day_hour = self.day_hour.reset_index()
        #print(self.day_hour)
        key_dimensions_hm = [('Weekday', 'Weekday'), ('Hour', 'Hour')]
        value_dimensions_hm = [('Sessions')]
        macro_hm = hv.Table(self.day_hour, key_dimensions_hm, value_dimensions_hm)
        hm = macro_hm.to.heatmap(['Weekday', 'Hour'], 'Sessions', []).options(width=748, show_legend=True, height = 525, 
                                                                               color=hv.Cycle('Spectral'), tools = ['hover'],
                                                                              title_format = "Heatmap")
        hm_plot = renderer.get_plot(hm).state
        hm_plot.y_range = FactorRange(factors = ['01 AM', '02 AM', '03 AM', '04 AM', '05 AM', '06 AM', '07 AM', '08 AM', '09 AM',
                                                 '10 AM', '11 AM', '12 PM', '01 PM', '02 PM', '03 PM', '04 PM', '05 PM', '06 PM',
                                                 '07 PM', '08 PM', '09 PM', '10 PM', '11 PM'])
        return hm_plot