from .. import Globals
from ._anvil_designer import MapTemplate
from anvil import *
from anvil.tables import app_tables
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q

class Map(MapTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Fill dropdown component for region selection
        Globals.regions = sorted(list(set(Globals.weather_stations['region'])))
        Globals.regions_extracted = True
        self.markers = {}
    
        # Center to map of germany
        self.map_of_germany.center = GoogleMap.LatLng(Globals.de_lat, Globals.de_lon)
        self.map_of_germany.zoom = Globals.de_zoom

        def get_values_by_condition(list_a, list_b, condition):
            return [b for a, b in zip(list_a, list_b) if a == condition]
      
        if Globals.region is not None:
            name = get_values_by_condition(Globals.weather_stations['region'], 
                                              Globals.weather_stations['name'], 
                                              Globals.region)
            lat = get_values_by_condition(Globals.weather_stations['region'], 
                                        Globals.weather_stations['lat'], 
                                        Globals.region)
            lon = get_values_by_condition(Globals.weather_stations['region'], 
                                        Globals.weather_stations['lng'], 
                                        Globals.region)
            height = get_values_by_condition(Globals.weather_stations['region'], 
                                        Globals.weather_stations['height'], 
                                        Globals.region)
            green_icon = GoogleMap.Icon(
                  url="http://maps.google.com/mapfiles/kml/paddle/grn-blank.png"
                )
            self.map_of_germany.clear()   
            for n, lat, lon, h in zip(name, lat, lon, height):
                marker = GoogleMap.Marker(
                  animation=GoogleMap.Animation.DROP,
                  position=GoogleMap.LatLng(lat, lon),
                  icon = green_icon
                )     
                self.markers[marker]=f'{n}\n{h} m a.s.l.'
                def marker_click(sender, **event_args):
                    i = GoogleMap.InfoWindow(content=Label(text=self.markers[sender]))
                    i.open(map, sender)
                marker.add_event_handler("click", marker_click)
                self.map_of_germany.add_component(marker)    
  
