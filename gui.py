from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config

class TheGrid(GridLayout):
    """background_color = ObjectProperty(None)"""
    pass

class Gui(App):
    def build(self):
        return TheGrid()


gui = Gui()

gui.run()
