from math import pi
from bokeh.palettes import Category20c, Spectral
from bokeh.transform import cumsum
import calendar
import datetime as DT
from datetime import datetime, date
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show, curdoc
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider, DatetimeTickFormatter
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs, Toggle
from bokeh.io import output_file, show
from bokeh.models.widgets import RadioButtonGroup, Button
from bokeh.models.widgets.inputs import DatePicker

class mainplot:
    def __init__(self, df):
        self.data = df
    
    def prepare(self):
        #Creating Sessions data set
        self.daily_sessions = self.data.groupby('start_date').agg({'start_date':'count'}).rename(columns = {'start_date':'Sessions'})
        self.daily_sessions = self.daily_sessions.reset_index()
        self.daily_sessions['start_date'] = self.daily_sessions['start_date'].apply(lambda x:datetime.strptime(x, "%m/%d/%Y"))
        self.daily_sessions['Year'] = self.daily_sessions['start_date'].apply(lambda x:x.year)
        self.daily_sessions['Month'] = self.daily_sessions['start_date'].apply(lambda x:x.month)
        self.daily_sessions['Day'] = self.daily_sessions['start_date'].apply(lambda x:x.day)
        self.daily_sessions['Month_Abb'] = self.daily_sessions['Month'].apply(lambda x: calendar.month_abbr[x])
        self.daily_sessions['Month_Abb'] = str(self.daily_sessions['Month_Abb'])
        self.daily_sessions = self.daily_sessions.sort_values(by = ['Year', 'Month', 'Day'])
        #print(self.daily_sessions.head(10))
        
        #Creating Session Duration data set
        self.avg_time = self.data[['start_date', 'start_time', 'end_time']]
        self.avg_time['Delta'] = self.avg_time['end_time'] - self.avg_time['start_time']
        self.avg_time['Delta'] = self.avg_time['Delta'].apply(lambda x:x.seconds)
        self.avg_time['Day'] = self.avg_time['start_time'].apply(lambda x:x.day)
        self.avg_time['Year'] = self.avg_time['start_time'].apply(lambda x:x.year)
        self.avg_time['Month'] = self.avg_time['start_time'].apply(lambda x:x.month)
        self.avg_time = self.avg_time.groupby(['start_date', 'Day', 'Month', 'Year']).mean().rename(columns = {'Delta':'Avg_Time'})
        self.avg_time['Avg_Time'] = round(self.avg_time['Avg_Time'])
        self.avg_time = self.avg_time.reset_index()
        self.avg_time = self.avg_time.sort_values(by = ['Year', 'Month', 'Day'])
        #print(self.avg_time.head(10))
        
        #Creating Users data set
        self.users = self.data.groupby(['start_date', 'device_id']).count().reset_index()
        self.users = self.users.groupby(['start_date', 'device_id']).device_id.count()
        self.users = pd.DataFrame(self.users).rename(columns = {'device_id': 'Users'}).reset_index()
        self.users_final = self.users.groupby('start_date').sum().reset_index()
        #print(self.users_final.head(10))
        
        #Creating Final Data set for CDS
        self.daily_sessions = self.daily_sessions[['start_date', 'Year', 'Month', 'Day', 'Sessions']]
        self.avg_time = self.avg_time[['Year', 'Month', 'Day', 'Avg_Time']]
        self.data_final = self.avg_time
        self.data_final['Sessions'] = self.daily_sessions['Sessions']
        self.data_final['Date'] = self.daily_sessions['start_date']
        self.data_final['Users'] = self.users_final['Users']
        self.data_final = self.data_final.rename(columns = {'Avg_Time':'Session Duration'})
        #print(self.data_final.head(10))
        #print(self.data_final.info())
        
        ##Creating events data set for possibly a pie chart
        self.events = self.data.groupby(by = ['start_date', 'events_type']).agg({'events_type':'count'}).rename(
            columns = {'events_type': 'Sessions'}
        )
        self.events = self.events.reset_index()
        self.events['start_date'] = self.events['start_date'].apply(lambda x:datetime.strptime(x, "%m/%d/%Y"))
        self.events.rename(columns = {'start_date':'Date'}, inplace = True)
        self.events['Year'] = self.events['Date'].apply(lambda x:x.year)
        self.events['Month'] = self.events['Date'].apply(lambda x:x.month)
        self.events['Day'] = self.events['Date'].apply(lambda x:x.day)
        #print(self.events.info())
        
        
        ##Top Holograms
        self.holograms = self.data.groupby(by = ['start_date', 'hologram_loaded']).agg({'hologram_loaded':'count'}).rename(
            columns = {'hologram_loaded': 'Count'}
        )
        self.holograms = self.holograms.reset_index()
        self.holograms['start_date'] = self.holograms['start_date'].apply(lambda x:datetime.strptime(x, "%m/%d/%Y"))
        self.holograms.rename(columns = {'start_date':'Date'}, inplace = True)
        self.holograms['Year'] = self.holograms['Date'].apply(lambda x:x.year)
        self.holograms['Month'] = self.holograms['Date'].apply(lambda x:x.month)
        self.holograms['Day'] = self.holograms['Date'].apply(lambda x:x.day)
        #print(self.holograms)
        
        
        #Adding Widgets
        self.options = Select(title="", options=["Last 7 days", "Last 30 days", "Last 90 days", "Custom.."], value="Custom..")
        self.radio_button_group = RadioButtonGroup(labels=["Users", "Sessions", "Session Duration"], active=1)
        self.date_from = DatePicker(title="From", min_date=DT.date(2017,8,29), max_date=DT.date(2018,8,29), value=DT.date(2018,1,1))
        self.date_to = DatePicker(title="To", min_date=DT.date(2017,8,29), max_date=DT.date(2018,8,29), value=DT.date(2018,2,1))
        self.hover1 = HoverTool(
        tooltips=[("Date", "@Date{%a, %d %B}"),
                  ("Value", "@y")],
        formatters={
        "@Date" : "datetime"},
        mode = "vline"
        )
        self.hover3 = HoverTool(
        tooltips=[("Hologram", "@hologram_loaded"),
                  ("Count", "@Count")],
        mode = 'vline'
        )
        self.source = ColumnDataSource(data=dict(x = [], y = [], Year=[], Month=[], Day=[], Date=[]))
        self.source_events = ColumnDataSource(data=dict(events_type = [], Sessions = [], Date=[], angle = [], color = []))
        self.source_holograms = ColumnDataSource(data=dict(Rank = [], hologram_loaded = [], Count = [], color = []))
        
        #Creating Plot
        self.plot = figure(plot_width=748, plot_height=525, tools = 'wheel_zoom,box_zoom,reset,save', x_axis_type="datetime",
                          title = "How are your Users trending over time?")
                          #x_axis_type="datetime" logo = None,    
        self.plot.toolbar.logo = None
        self.plot.add_tools(self.hover1)
        self.plot.xgrid.visible = False
        self.plot.line(x = 'x', y = 'y', line_width = 3, source=self.source, color = "#2097BE")
        self.plot.circle(x = 'x', y = 'y', source = self.source, size=6, fill_color = "#2097BE", line_color = 'white')
        self.plot.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
        #self.plot.xaxis.major_label_orientation = 'vertical'
        self.plot.xaxis.minor_tick_line_color = None
        self.plot_events = figure(plot_width=748, plot_height=525, tools = 'wheel_zoom,box_zoom,reset,save',
                                  tooltips="@events_type: @Sessions", x_range=(-0.5, 1.0),
                                  title = "Breakdown of App Events")
        self.plot_events.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'), 
                        line_color="white", fill_color="color", source=self.source_events, legend = "events_type")
        self.plot_events.toolbar.logo = None
        self.plot_events.axis.axis_label=None
        self.plot_events.axis.visible=False
        self.plot_events.grid.grid_line_color = None
        
        self.plot_holograms = figure(plot_width=748, plot_height=525, tools = 'wheel_zoom,box_zoom,reset,save',
                                     title = "What are the Top Data Points people are interacting with?")
        self.plot_holograms.toolbar.logo = None
        self.plot_holograms.add_tools(self.hover1)
        self.plot_holograms.xgrid.visible = False
        self.plot_holograms.add_tools(self.hover3)
        self.plot_holograms.xaxis.minor_tick_line_color = None
        self.plot_holograms.vbar(x="Rank", top="Count", width = 0.95, source = self.source_holograms, color = "color")
        return self.plot, self.plot_events, self.plot_holograms, self.options, self.radio_button_group, self.date_from, self.date_to
    
    def select_sessions(self):
        today = DT.date(2018,7,20)
        from_date = self.date_from.value
        to_date = self.date_to.value
        week_ago  = []
        month_ago = []
        ninty_ago = []
        custom = pd.date_range(from_date, to_date)
        custom = pd.Series(custom)
        custom = custom.apply(lambda x:x.date())
        if self.options.value == "Custom..":
            self.date_from.disabled = False
            self.date_to.disabled = False
        else:
            self.date_from.disabled = True
            self.date_to.disabled = True
        for i in range(0,7):
            week_ago.append(today - DT.timedelta(days=i))
        for i in range(0,31):
            month_ago.append(today - DT.timedelta(days=i))
        for i in range(0,91):
            ninty_ago.append(today - DT.timedelta(days=i))
        if self.options.value == "Last 7 days":
            self.selected_holograms = self.holograms[
                self.holograms['Date'].isin(week_ago)
            ]
            self.selected_events = self.events[
                self.events['Date'].isin(week_ago)
            ]
            self.selected = self.data_final[
                self.data_final['Date'].isin(week_ago)
            ]
        elif self.options.value == "Last 30 days":
            self.selected_holograms = self.holograms[
                self.holograms['Date'].isin(month_ago)
            ]
            self.selected_events = self.events[
                self.events['Date'].isin(month_ago)
            ]
            self.selected = self.data_final[
                self.data_final['Date'].isin(month_ago)
            ]
        elif self.options.value == "Last 90 days":
            self.selected_holograms = self.holograms[
                self.holograms['Date'].isin(ninty_ago)
            ]
            self.selected_events = self.events[
                self.events['Date'].isin(ninty_ago)
            ]
            self.selected = self.data_final[
                self.data_final['Date'].isin(ninty_ago)
            ]
        elif self.options.value == "Custom..":
            self.selected_holograms = self.holograms[
                self.holograms['Date'].isin(custom)
            ]
            self.selected_events = self.events[
                self.events['Date'].isin(custom)
            ]
            self.selected = self.data_final[
                self.data_final['Date'].isin(custom)
            ]
        return self.selected, self.selected_events, self.selected_holograms
    
    def update(self):
        df, df2, df3 = self.select_sessions()
        x_name = 'Date'
        if self.radio_button_group.active == 0:
            self.y_name = 'Users'
            self.plot.yaxis.axis_label = self.y_name
        elif self.radio_button_group.active == 1:
            self.y_name = 'Sessions'
            self.plot.yaxis.axis_label = self.y_name
        else:
            self.y_name = 'Session Duration'
            self.plot.yaxis.axis_label = 'Session Duration (Sec)'
        self.plot.xaxis.axis_label = x_name
        self.source.data = dict(
            x=df[x_name],
            y=df[self.y_name],
            Year=df["Year"],
            Month = df["Month"],
            Day = df["Day"],
            Date = df["Date"]
        )
        #print(self.source.data)
        df2_new = df2.groupby('events_type').agg({'Sessions':'sum'}).reset_index()
        df2_new['angle'] = df2_new['Sessions']/df2_new['Sessions'].sum() * 2*pi
        df2_new['color'] = Category20c[df2_new.shape[0]]
        self.source_events.data = dict(
            events_type=df2_new["events_type"],
            Sessions=df2_new["Sessions"],
            angle=df2_new["angle"],
            color=df2_new["color"]
        )
        df3_new = df3.groupby('hologram_loaded').agg({'Count':'sum'})
        df3_new = df3_new.sort_values('Count', ascending = False)
        df3_new = df3_new.head(2)
        ranks = [1,2]
        df3_new['Rank'] = ranks
        df3_new = df3_new.reset_index()
        df3_new['color'] = ["#2097BE", "#b20000"]
        #print(df3_new)
        self.source_holograms.data = dict(
            Rank=df3_new["Rank"],
            Count = df3_new["Count"],
            hologram_loaded=df3_new["hologram_loaded"],
            color=df3_new["color"]
        )
        self.plot_holograms.xaxis.major_label_overrides = {1: list(df3_new.hologram_loaded)[0], 2: list(df3_new.hologram_loaded)[1]}
        self.plot_holograms.xaxis[0].ticker.desired_num_ticks = 2
        
    def final_sketch(self):
        controls = [self.options, self.date_from, self.date_to]
        for control in controls:
            control.on_change('value', lambda attr, old, new: self.update())
        self.radio_button_group.on_change('active', lambda attr, old, new: self.update())
        columns = [
            TableColumn(field="Date", title="Date", formatter = DateFormatter()),
            TableColumn(field="Sessions", title="Sessions"),
        ]
        self.data_table = DataTable(source=self.source, columns=columns, width=400, height=400)
        #self.inputs = widgetbox([self.radio_button_group, *controls], sizing_mode='fixed')
        self.inputs = row(self.radio_button_group, *controls)

        return self.inputs