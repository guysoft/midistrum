#!/usr/bin/env python3
import threading
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.app import runTouchApp, App
from kivy.clock import Clock, mainthread
from kivy.core.image import Image as CoreImage
from kivy.uix.actionbar import ActionBar
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
# from kivy.lang import Builder
from kivy.factory import Factory
import os
import time
# import android.media.midi.MidiManager
from plyer.platforms.android import activity
from jnius import autoclass, cast
from android_midi import OpenMidiSendDeviceListener, get_midi_ports_list

# Plyer clases
MidiManager = autoclass('android.media.midi.MidiManager')
Context = autoclass('android.content.Context')

# Create the manager
sm = ScreenManager()


def callback(scr_name, instance):
    print('The button <%s> is being pressed' % instance.text)
    sm.current = 'Title ' + str(scr_name)


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class ScreenOne(Screen):
    
    def midi_started_callback(self):
        self.midi_listner.play_test()
        return

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.midi_listner = None
        
        print("Testing midi")
        
        midi_devices = get_midi_ports_list()
        for name, device in midi_devices:
            if name == "MIDI Connector Free Virtual Port 1":
                print("Yay")
                print(device.getOutputPortCount())
                print(device.getInputPortCount())
                
                service = activity.getSystemService(Context.MIDI_SERVICE)
                m = cast('android.media.midi.MidiManager', service)
                
                self.midi_listner = OpenMidiSendDeviceListener(self.midi_started_callback)
                m.openDevice(device, self.midi_listner, None)
                
                print("Opened midi device")
                break

        print("Done loading midi")
        
    def do_print(self):
        self.midi_listner.note_on(b'\x78')
        time.sleep(0.2)
        self.midi_listner.note_off(b'\x78')
        print("Button pressed")

class TitlebarNavigation(ActionBar):

    def __init__(self, **kwargs):
        ActionBar.__init__(self, **kwargs)

        


print("################################################")


class Midistrum(App):
    pass


if __name__ == '__main__':
    Midistrum().run()


# runTouchApp(sm)
