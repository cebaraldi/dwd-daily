import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import os.path
import requests
import csv
import io
import zipfile
from urllib.request import urlretrieve
import pandas as pd
from contextlib import closing
import json


@anvil.server.callable
def dl_to_weather_stations(url):
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.splitlines()
        #format_string = "%Y%m%d"
        wsid = []
        date_from = []
        date_to = []
        height = []
        lat = []
        lng = []
        station = []
        region = []
        abgabe = []
        for line in lines[2:]:    
          wsid.append(line[0:5])
          date_from.append(line[6:14])
          date_to.append(line[15:23])
          height.append(line[24:38])
          lat.append(line[39:50])
          lng.append(line[51:60])
          station.append(line[61:101].strip()) #.strip())
          region.append(line[102:142].strip()) #.strip())
          abgabe.append(line[143:].strip()) #.strip())
        # dictionary of lists 
        dict = {'wsid': wsid, 'date_from': date_from, 'date_to': date_to, 'height': height, # [m]
                'lat': lat, 'lng': lng, 'name': station, 'region': region, 'abgabe': abgabe}
        df = pd.DataFrame(dict) #.drop(index=[0,1])
        # Convert columns
        df['date_from'] = pd.to_datetime(df['date_from']).dt.date
        df['date_to'] = pd.to_datetime(df['date_to']).dt.date
        df['height'] = pd.to_numeric(df['height'], downcast="integer")
        df['lat'] = pd.to_numeric(df['lat'], downcast="float")
        df['lng'] = pd.to_numeric(df['lng'], downcast="float")
        # remove stations w/ missing latest observation
        df1 = df[df['date_to']==df['date_to'].max()]
        # remove stations where abgabe is not 'Frei'
        df2 = df1[df1['abgabe']=='Frei']
    return(df2.to_dict('list'))

def dict_to_dataframe(data_dict):
    """Converts a dictionary with a binary string value into a Pandas DataFrame.
  
    Args:
      data_dict: The input dictionary.
  
    Returns:
      A Pandas DataFrame.
    """
    value = next(iter(data_dict.values()))  # Extract the value
    decoded_value = value.decode('utf-8')  # Decode the byte string
    records = decoded_value.strip().split('eor\r\n')
    data = [record.split(';') for record in records]
    # Trim column names using strip()
    df = pd.DataFrame(data[1:], columns=(s.strip() for s in data[0]))
    df = df[df.columns[:-1]]
    # Remove leading and trailing spaces from all columns
    df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)  
    return(df)  
  
@anvil.server.callable
def dl_zip(wsid, date_from, date_to, recent, historical):
    url = 'https://opendata.dwd.de/'
    path = 'climate_environment/CDC/observations_germany/climate/daily/kl/'
    recent_path = path + 'recent/'
    filename = f'tageswerte_KL_{wsid}_akt.zip'
    url = url + recent_path + filename
    body = {}
    r = requests.get(url)
    with closing(r), zipfile.ZipFile(io.BytesIO(r.content)) as archive:   
        # print({member.filename: archive.read(member) for member in archive.infolist()})
        body ={member.filename: archive.read(member) 
              for member in archive.infolist() 
              if (member.filename.startswith('produkt_klima_tag_'))
              }
    df = dict_to_dataframe(body)
    df = df.drop('STATIONS_ID', axis=1) # already given as parameter
    dict_list = df.to_dict('list')
    return(dict_list)

#def send_feedback(name, email, feedback):
#@anvil.server.callable
#def send_feedback(email):
#    anvil.email.send(
#      from_name='name',
#      to=email,
#      subject=f"Feedback from {email}",
#      #html='The Anvil <a href="https://anvil.works/forum">Forum</a> is friendly and informative.',
#      text={" ***"},
#    )

@anvil.server.callable
def send_feedback(address, name, email, feedback):
    anvil.email.send(
      from_name=name,
      to=address,
      subject=f"Feedback from {email}",
      html='The Anvil <a href="https://anvil.works/forum">Forum</a> is friendly and informative.',
      text=f"{feedback}"
    )
