from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector

from kivy.core.window import Window
from kivy.modules import inspector

from datetime import datetime,timedelta
import json
import os.path
import socket
import uuid

READ_SIZE = 4096
ENCODING = "utf-8"

class DataViewItem(BoxLayout):
    title = ""
    thumb = ""

class LifxController(Widget):
    lightsd_socket = None
    lightsd_socket_file = "/run/lightsd/socket"
    lightsd_devices= {}

    def connect(self):
        # Connect to lightsd, here using an Unix socket. The rest of the example is
        # valid for TCP sockets too. Replace /run/lightsd/socket by the output of:
        # echo $(lightsd --rundir)/socket
        if os.path.exists( self.lightsd_socket_file ):
            self.lightsd_socket = socket.socket(socket.AF_UNIX)
            self.lightsd_socket.connect( self.lightsd_socket_file )
            self.lightsd_socket.settimeout(2)  # seconds
        print( "Connect called")


    def update(self, dt):
        print ( "TS:", dt )

        response = self.__lightsd_update_state()

        state = response['result']
        print( "State:", state)
        print( "Devices: ", ",".join( self.lightsd_devices.keys() ))
        self.__lightsd_populate( state )

    # Helper Functions:

    def __lightsd_populate(self, state ):

        addrs = self.lightsd_devices.keys()
        ts    = datetime.now()
        for device in state:
            addr = ""
            try:
                addr = device['_lifx']['addr']
            except KeyError:
                print( "Fehler in Ausgabe von lightsd:")
                print ( json.dumps( device, sort_keys=True,
                               indent=4, separators=(',',': ') ) )
                continue

            if not addr in addrs:
                self.lightsd_devices[addr] = {
                    'raw': device,
                    'ts' : ts,
                    'state' : 'NEW'
                    }
                self.__lightsd_device_found( addr )
            else:
                self.lightsd_devices[addr] = {
                    'raw': device,
                    'ts' : ts,
                    'state' : 'KNOWN'
                    }

        for addr in addrs:
            if ts - self.lightsd_devices[addr]['ts'] > timedelta(seconds=10):
                # Automatic remove of device  after 30s !?
                #self.lightsd_devices.remove(addr)
                pass

                self.lightsd_devices[addr]['state']="LOST"
                self.__lightsd_device_lost( addr )

    def __lightsd_device_found(self, addr ):
        __doc__="Handle new device"
        print("New Device {:s}".format(addr))
        self.lightsd_devices[addr]['widget']=Factory.DataViewItem()
        self.lightsd_devices[addr]['widget'].title = self.lightsd_devices[addr]['raw']['label']
        self.ids.lamp_grid.add_widget( self.lightsd_devices[addr]['widget'] )

    def __lightsd_device_lost(self, addr ):
        __doc__="Handle lost device"
        print("Remove Device {:s}".format(addr))
        print("-> {!r}".format( self.lightsd_devices[addr].keys() ))
        self.ids.lamp_grid.remove_widget( self.lightsd_devices[addr]['widget'] )
        pass

    def __lightsd_update_state(self, target=["*"]):
        __doc__="Update state of all devices"
        # Prepare the request:

        request = json.dumps({
            "method": "get_light_state",
            "params": ["*"],
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
        }).encode(ENCODING, "surrogateescape")
        # Send it:
        response = self.__lightsd_send( request )

        return( response )

    def __lightsd_send(self, request ):
        __doc__="Send command to socket"
        if self.lightsd_socket:
            self.lightsd_socket.sendall(request)
        else:
            return {'id':0,'result':{}}
        # Prepare an empty buffer to accumulate the received data:
        response = bytearray()
        while True:
            # Read a chunk of data, and accumulate it in the response buffer:
            response += self.lightsd_socket.recv(READ_SIZE)
            try:
                # Try to load the received the data, we ignore encoding errors
                # since we only wanna know if the received data is complete.
                json.loads(response.decode(ENCODING, "ignore"))
                break  # Decoding was successful, we have received everything.
            except Exception:
                continue  # Decoding failed, data must be missing.

        response = response.decode(ENCODING, "surrogateescape")
        return ( json.loads(response) )


class LifxControlApp(App):
    def build(self):
        lc = LifxController()
        lc.connect()
        #inspector.create_inspector(Window, lc)
        Clock.schedule_interval( lc.update, 1.0 / 0.5 )

        return lc

if __name__ == '__main__':
    LifxControlApp().run()
