import numpy as np
import pandas as pd
from datetime import datetime
from dashboard_main import fetch_data

##Defining Service account credentials for fetching data from GCP

cred = 'velvety-accord-186814-bbf0d61a262b.json'
p_id = 'velvety-accord-186814'
query = ("""SELECT * FROM cg_sessions.session_event ORDER BY id""")
bigquery = fetch_data.import_data(cred, p_id, query)
data = bigquery.data_output()

#Creating features
data['start_date'] = data['start_time'].apply(lambda x:x.strftime('%Y-%m-%d'))
data['end_date'] = data['end_time'].apply(lambda x:x.strftime('%Y-%m-%d'))
data['start_time'] = pd.to_datetime(data['start_time'])
data['start_day'] = data['start_time'].apply(lambda x:x.day)
data['start_month'] = data['start_time'].apply(lambda x:x.month)
data['start_hour'] = data['start_time'].apply(lambda x:x.hour)
data['start_minute'] = data['start_time'].apply(lambda x:x.minute)
data['end_time'] = pd.to_datetime(data['end_time'])
data['end_hour'] = data['end_time'].apply(lambda x:x.hour)
data['end_minute'] = data['end_time'].apply(lambda x:x.minute)
data['Avg_session'] = data['end_minute'] - data['start_minute']