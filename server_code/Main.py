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

@anvil.server.callable
def extract_year_from_date(date_value):
    year = date_value.year
    return year
  
@anvil.server.callable
def get_records_for_year(table_name, date_column_name, year):
    """
    Retrieves records from a table where the specified date column's year matches the given year.
  
    Args:
      table_name (str): The name of the table.
      date_column_name (str): The name of the date column.
      year (int): The target year.
  
    Returns:
      list: A list of records matching the criteria.
    """
    table = app_tables[table_name]
    records = table.search(**{date_column_name: q.date_extract('year') == year})
    return records
  
@anvil.server.callable
def get_region():
    rows =  app_tables.dwd_weatherstations.search()
    unique_values = set(row['region'] for row in rows)
    sorted_values = sorted(list(unique_values))
    sorted_values.insert(0,"<Please select a region>")
    return sorted_values  

@anvil.server.callable
def get_ws(region):
    rows = app_tables.dwd_weatherstations.search(region=q.ilike(region))
    unique_values = set(row['name'] for row in rows)
    sorted_values = sorted(list(unique_values))
    sorted_values.insert(0,"<Please select a station>")
    return sorted_values

@anvil.server.callable
def dlObservations(region, ws):
    record = app_tables.dwd_weatherstations.search(
      name=q.ilike(ws), 
      region=q.ilike(region)
    )
    url = "https://opendata.dwd.de/"
    path = 'climate_environment/CDC/observations_germany/climate/daily/kl/'
    recent_path = path + 'recent/'
    #historical_path = path + 'historical/'
  
    for r in record:
        filename = f"tageswerte_KL_{r['wsid']}_akt.zip"
        #print(filename)
        # BINARY Data
        url = url + recent_path + filename
        print(url, filename)
  
  #    if not os.path.exists(filename):
  #      urlretrieve(url, filename)
  #      
  #      try:
  #        with zipfile.ZipFile(filename, mode="r") as archive:
  #          for file in archive.namelist():
  #            if file.endswith("/tmp/produkt_klima_tag_*.txt"):
  #              archive.extract(file, ".")
  #              print(file)
  #      except FileNotFoundError:
  #        return False

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
        lon = []
        city = []
        region = []
        for line in lines[2:]:
            wsid.append(line[0:5])
            date_from.append(line[6:14])
            date_to.append(line[15:23])
            height.append(line[24:42])
            lat.append(line[43:52])
            lon.append(line[53:60])
            city.append(line[61:101].strip())
            region.append(line[102:].strip())
        # dictionary of lists 
        dict = {'wsid': wsid, 'date_from': date_from, 'date_to': date_to, 'height': height, # [m]
                'lat': lat, 'lon': lon, 'name': city, 'region': region} # [°]
        df = pd.DataFrame(dict) #.drop(index=[0,1])
        # Convert columns
        df['date_from'] = pd.to_datetime(df['date_from']).dt.date
        df['date_to'] = pd.to_datetime(df['date_to']).dt.date
        df['height'] = pd.to_numeric(df['height'], downcast="integer")
        df['lat'] = pd.to_numeric(df['lat'], downcast="float")
        df['lon'] = pd.to_numeric(df['lon'], downcast="float")
        #print(df.head())
    return(df.to_dict('list'))
