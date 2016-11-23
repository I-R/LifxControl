from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.logger import Logger
from kivy.factory import Factory

import pprint
pp = pprint.PrettyPrinter(indent=4)

class DataViewItem(BoxLayout):
    did   = StringProperty("")
    title = StringProperty("")
    thumb = StringProperty("")

    pass

class DataView(BoxLayout):

    items = ListProperty([])

    def on_items(self, *args):
        #print( "Self:",type(self))
        #print( "data_view:",dir(self))

        self.clear_widgets()
        for item in self.items:
            Logger.info ("DataView: Item - {!r}".format(item) )
            w = Factory.DataViewItem( **item )
            print( w, w.title )
            self.add_widget(w)

        print( "DV",self.children )


class LifxController(Widget):
    lamp_grid=ObjectProperty(None)

    def build(self):
        Logger.info("LC: build")

        items = [
            {'did':'0', 'title': 'My first Picture', 'thumb': 'picture1.png'},
            {'did':'1', 'title': 'Hello world', 'thumb': 'hello.jpg'}
        ]

        self.lamp_grid.clear_widgets()
        for item in self.items:
            Logger.info ("DataView: Item - {!r}".format(item) )
            w = Factory.DataViewItem( **item )
            print( w, w.title )
            self.lamp_grid.add_widget(w)

        # You can set items at init
        #d = DataView(items=items)
        """d = DataView()

        d.items = items

        l = self

        self.lamp_grid.add_widget(d)

        print ( "LC:", l.children )
        """

        print ( "LG:", self.lamp_grid.children )

        return self



class LifxControlApp(App):
    lamps_list=[]

    def build(self):
        l = LifxController()
        Logger.info("LCA: build")
        #Logger.info("LCA: l - {!r}".format( dir(l) ) )

        items = [
            {'did':'0', 'title': 'My first Picture', 'thumb': 'img/img1.png'},
            {'did':'1', 'title': 'Hello world', 'thumb': 'img/img2.png'}
        ]

        # You can set items at init
        #d = DataView(items=items)

        l.lamp_grid.clear_widgets()
        for item in items:
            Logger.info ("DataView: Item - {!r}".format(item) )
            w = Factory.DataViewItem( **item )
            print( w, w.title )
            l.lamp_grid.add_widget(w)

        """
        d = DataView()

        d.items = items

        l.lamp_grid.add_widget(d)
        """

        print ( "LC:", l.children )
        print ( "Hint:", l.lamp_grid.size_hint_x)
        for c in l.lamp_grid.children:
            print ( "LG:", c.title )

        return l


if __name__ == '__main__':
    LifxControlApp().run()
