import numpy as np
import pandas as pd
from datetime import datetime
import google.cloud.bigquery as bigquery
from google.oauth2 import service_account
import numpy as np
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
import os
files = os.listdir()
json = []
for f in files:
    if f.endswith('json'):
        json.append(f)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json[0]

class import_data:
    
    def __init__(self, query):
        self.query = query
    
    def data_output(self):
        query = self.query
        client = bigquery.Client()
        query_job = client.query(query)
        output = query_job.result().to_dataframe()
        print("Data fetched from BigQuery")
        data = output
        #Creating features
        print("Performing Data Preperations")
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
        print("Data Ready for Analysis")
        return data