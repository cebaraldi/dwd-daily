from ._anvil_designer import MapTemplate
from anvil import *


class Map(MapTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
