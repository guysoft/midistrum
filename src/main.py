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
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, NumericProperty
# from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.settings import SettingItem
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
import os
import sys
import time
from kivy.utils import platform
import mido
import pretty_midi
from pychord import Chord

# import android.media.midi.MidiManager

__version__ = "0.2.9"
__version_code__ = 1021209

CHROMATIC = 12

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
else:
    import pygame.midi
    pygame.midi.init()

# Create the manager
sm = ScreenManager()


def callback(scr_name, instance):
    print('The button <%s> is being pressed' % instance.text)
    sm.current = 'Title ' + str(scr_name)


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class MultiTouchButton(Button):
    text = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # self.text = f'Touch ID: {touch.id}'
            get_main_app().chord = self.text

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # self.text = 'Button'
            print(self.text + "-")

def get_main_app():
     return App.get_running_app().root.children[0]

class CursorRectangle(Widget):
    number = NumericProperty()
    inside = False

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
            if not self.inside:
                self.inside = True
                print(f"Note on {self.number}")
                press_time = App.get_running_app().config.get("Midistrum", "press_time")
                threading.Thread(target=lambda: get_main_app().pluck_string(self.number, press_time,)).start()
                # Hangle pluck
        else:
            if self.inside:
                self.inside = False
                # Handle note off
                print(f"Note off {self.number}")
    
    def on_touch_down(self,touch):
        self.inside = False
        self.on_touch_move(touch)
            
            # print(f"Cursor position inside Rectangle {self.number} {self.rect.pos} - x: {touch.pos[0]}, y: {touch.pos[1]}")
        # else:
        #     print("Cursor position outside Rectangle")

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class SettingMIDI(SettingItem):
    popup = ObjectProperty(None, allownone=True)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _set_option(self, instance):
        self.value = instance.text
        self.popup.dismiss()

    def _create_popup(self, instance):
        global midi
        root = ScrollView(size_hint=(1, None), size=(1, 200))

        content = BoxLayout(orientation='vertical', spacing=10)
        root.add_widget(content)
        self.popup = popup = Popup(content=root,
                                   title=self.title, size_hint=(1, 1), size=(1000, 1000))

        if platform == 'android':
            devices = get_midi_ports_list()
            device_count = len(devices)
            print(f'Len: {device_count}')
        else:
            device_count = pygame.midi.get_count()
        print("heigt:")
        height = device_count * 200 + 150 + 200
        print(height)
        popup.height = 150

        # content.add_widget(Widget(size_hint_y=None, height=200))
        uid = str(self.uid)

        if platform == 'android':
            for device_name, device in devices:
                state = 'down' if device_name == self.value else 'normal'
                btn = ToggleButton(text=device_name, state="normal", group=uid)
                btn.bind(on_release=self._set_option)
                content.add_widget(btn)

            # for i in range(device_count):
            #     for port in devices[i].getPorts():
            #         if midi.getName(devices[i]) != 'MasterGrid' and (
            #                 port.getType() == 2 or midi.getName(devices[i]) == self.value):
            #             state = 'down' if midi.getName(devices[i]) == self.value else 'normal'
                        
        else:
            for i in range(device_count):
                if pygame.midi.get_device_info(i)[3] == 1 and (
                        pygame.midi.get_device_info(i)[4] == 0 or pygame.midi.get_device_info(i)[
                        1].decode() == self.value):
                    state = 'down' if pygame.midi.get_device_info(i)[1].decode() == self.value else 'normal'
                    btn = ToggleButton(text=pygame.midi.get_device_info(i)[1].decode(), state=state, group=uid)
                    btn.bind(on_release=self._set_option)
                    content.add_widget(btn)

        btn = Button(text='Cancel', size_hint_y=None, height=50)
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        popup.open()

def get_chords_base(chord_name):
    print(chord_name)

    return [pretty_midi.note_name_to_number(f'{note_name}1') for note_name in Chord(chord_name).components()]

def get_note_from_number(number, chord, shift = CHROMATIC):
    notes_in_chord = len(chord)
    number = number + notes_in_chord
    return int(chord[number % notes_in_chord] + CHROMATIC * int(number/ notes_in_chord))
    

class SeparateThreadPrinter(threading.Thread):
    def run(self):
        print("Printing message on a separate thread")
        time.sleep(5)
        print("Printing message again after sleeping")

    
class ScreenOne(Screen):
    
    def midi_started_callback(self):
        # self.midi_listner.play_test()
        return

    def set_midi_device(self, device_name):

        if get_platform() == "android":
            midi_devices = get_midi_ports_list()
            for name, device in midi_devices:
                if name == device_name:
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

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.midi_listner = None
        self.chord = None
        self.url_popup = AboutPopup(title='About Midistrum')

        midi_device = App.get_running_app().config.get("Midistrum", "midi_device")
        self.set_midi_device(midi_device) 
        print("Testing midi")



    def pluck_string(self, number=None, press_time=1000):
        if get_platform() == "android":
            scale = self.chord
            chord_base = get_chords_base(scale)
            note = get_note_from_number(number, chord_base)
            if note < 127:
                print(note, press_time)
                data = mido.Message('note_on', note=note).bin()
                self.midi_listner.send(data)
                time.sleep(float(press_time) / 1000)
                data = mido.Message('note_off', note=note).bin()
                self.midi_listner.send(data)
            else:
                print(f"note too high: {note}")

            # note = b'\x78'
            # self.midi_listner.note_on(note)
        print("Button pressed")

class TitlebarNavigation(ActionBar):

    def __init__(self, **kwargs):
        ActionBar.__init__(self, **kwargs)

class AboutPopup(Popup):
    def __init__(self, **kwargs):
        super(AboutPopup, self).__init__(**kwargs)

    def open_url(self):
        import webbrowser
        webbrowser.open("http://github.com/guysoft/midistrum")
        


print("################################################")


class Midistrum(App):
    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Midistrum', {
            'text': 'Hello',
            'press_time': 1000,
            'midi_device': "",
            })
        
    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        #     settings.add_json_panel('My Label', self.config, 'settings.json')
        settings.register_type('midi', SettingMIDI)
        json_config_str = ""
        with open("settings.json") as f:
            json_config_str = f.read()
        settings.add_json_panel('Midistrum', self.config, data=json_config_str)

    def on_config_change(self, config, section, key, value):
        if key == 'midi_device':
            # TODO CLOSE OLD
            print("Set_Foncig")
            try:
                if get_main_app().midi_listner is not None:
                    get_main_app().midi_listner.close()
            except:
                pass
            midi_device = App.get_running_app().config.get("Midistrum", "midi_device")
            get_main_app().set_midi_device(midi_device)


if __name__ == '__main__':
    if(platform == 'android' or platform == 'ios'):
        Window.maximize()
    else:
        Window.size = (1024, 620)
    Midistrum().run()


# runTouchApp(sm)
