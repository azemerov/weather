import streamlit as st
import pandas as pd
import time
from urllib.request import Request, urlopen
import urllib
import json
import datetime

begin = st.sidebar.date_input("Start date", value=datetime.datetime.now() - datetime.timedelta(days=1))
end = st.sidebar.date_input("End date", value=datetime.datetime.now() + datetime.timedelta(days=1))
begin = begin.strftime('%Y-%m-%dT%H:%M:%S.000Z')
end = end.strftime('%Y-%m-%dT%H:%M:%S.000Z')
query = '''{
    "collection":"temperature","database":"weatherDb","dataSource":"VespaCluster", 
    "filter":
    {
        "$and": 
        [
            {"ts": {"$gte": {"$date": "%s"}}},
            {"ts": {"$lte": {"$date": "%s"}}}
        ]
    },
    "sort": {"ts": -1}
}''' % (begin, end)
query = query.encode('utf-8')

request = Request('https://data.mongodb-api.com/app/data-blzil/endpoint/data/beta/action/find', data = query)
request.add_header('Content-Type', 'application/json')
request.add_header('Access-Control-Request-Headers', '*')
request.add_header('api-key', 'Z6p51gsY6CrdyGkhmLCy3uYHJJCmRWVvoVZHOZqPSfbxTX8u64tZg916BfdWLqXN')

response = urllib.request.urlopen(request)
payload = response.read()
data = json.loads(payload)
df = pd.json_normalize(data['documents'])
try:
  # use different scale for pressure : 0 = 1000 
  df['pressure'] = df['pressure'].apply(lambda x : x-1000)
except:
  pass

#print(df)

if not df.empty:
  kind = st.sidebar.radio("Select data", ["Temperature", "Pressure", "Humidity"])
  kind = {"Temperature":"temp", "Pressure":"pressure", "Humidity":"humidity"}[kind]
  st.line_chart(df, x='ts', y=[kind])
  st.write("From", begin, "to", end)
  if df["_id"].count() == 1000:
    st.write("reached the limit of 1000 records")
  else:
    st.write(df["_id"].count(), "measurements")
  st.write("Mininmum TS:", df["ts"].min())
  st.write("Maximum TS:", df["ts"].max())
  st.write("Minimum value:", df[kind].min())
  st.write("Maximum value:", df[kind].max())
  #st.write(data)
else:
  st.sidebar.write("No data for the selected range")
