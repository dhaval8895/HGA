import calendar
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show, curdoc
from datetime import datetime, date
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs

renderer = hv.renderer('bokeh')

class bars:
    def __init__(self, df):
        self.data = df
    def plot_barchart(self):
        hv.extension('bokeh', logo=False)
        ##Stacked Bar chart for Day and Event Type
        self.events_day = self.data.groupby(by = ['start_day', 'events_type']).agg({'events_type':'count'}).rename(
            columns = {'events_type': 'Sessions'}
        )
        self.events_day = self.events_day.reset_index()
        key_dimensions   = [('start_day', 'Day'), ('events_type', 'Event')]
        value_dimensions = [('Sessions')]
        macro = hv.Table(self.events_day, key_dimensions, value_dimensions)
        self.bars = macro.to.bars(['Day', 'Event'], 'Sessions', []).options(stack_index= 1, width=1100, show_legend=False, height = 600, 
                                                               tools=['hover'], color = hv.Cycle('Category20'))
        bar_plot = renderer.get_plot(self.bars).state
        return bar_plot