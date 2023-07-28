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
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, NumericProperty
# from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
import os
import sys
import time
from kivy.utils import platform
# import android.media.midi.MidiManager

import plyer

def get_platform():
    return platform

if get_platform() == "android":
    from plyer.platforms.android import activity
    from jnius import autoclass, cast
    from android_midi import OpenMidiSendDeviceListener, get_midi_ports_list

    # Android clases
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


class MultiTouchButton(Button):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # self.text = f'Touch ID: {touch.id}'
            print(self.text)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # self.text = 'Button'
            print(self.text + "-")

class CursorRectangle(Widget):
    number = NumericProperty()

    def __init__(self, **kwargs):
        super(CursorRectangle, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start, .1)

    def on_start(self, dt):
        self.bind(pos=self.update_rect, size=self.update_rect)
    
        print(self.number)

        with self.canvas:
            if self.number % 2 == 0:
                Color(0.5, 0.5, 0.5)
            else:
                Color(0.25, 0.25, 0.25)
            
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.update_rect()

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            print(f"Cursor position inside Rectangle {self.number} {self.rect.pos} - x: {touch.pos[0]}, y: {touch.pos[1]}")
        # else:
        #     print("Cursor position outside Rectangle")

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ScreenOne(Screen):
    
    def midi_started_callback(self):
        self.midi_listner.play_test()
        return

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.midi_listner = None
        
        print("Testing midi")

        if get_platform() == "android":
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
        else:
            print(f"midi not implemented for: {get_platform()}")
        
    def do_print(self):
        if get_platform() == "android":
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
    if(platform == 'android' or platform == 'ios'):
        Window.maximize()
    else:
        Window.size = (1024, 620)
    Midistrum().run()


# runTouchApp(sm)
