from ._anvil_designer import ceb_layoutTemplate
from anvil import *


class ceb_layout(ceb_layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
