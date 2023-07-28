import time
from jnius import autoclass, cast, java_method, PythonJavaClass
from plyer.platforms.android import activity

MidiManager = autoclass('android.media.midi.MidiManager')
MidiDeviceInfo = autoclass('android.media.midi.MidiDeviceInfo')
PortInfo = autoclass('android.media.midi.MidiDeviceInfo$PortInfo')
MidiDevice = autoclass('android.media.midi.MidiDevice')
MidiInputPort = autoclass('android.media.midi.MidiInputPort')
Context = autoclass('android.content.Context')


def get_midi_ports_list():
    return_value = []
    service = activity.getSystemService(Context.MIDI_SERVICE)
    m = cast('android.media.midi.MidiManager', service)
    device_list = m.getDevices()
    
    for dev_info in device_list:
        dev_info_casted = cast('android.media.midi.MidiDeviceInfo', dev_info)
        # Java: deviceName = devInfo.getProperties().getString(MidiDeviceInfo.PROPERTY_NAME);
        device_name = dev_info_casted.getProperties().getString(MidiDeviceInfo.PROPERTY_NAME);
        return_value.append((device_name, dev_info_casted))
    return return_value

class OpenMidiSendDeviceListener(PythonJavaClass):
    """
    Listener class for opening a midi device. 
    android/media/midi/MidiManager/OnDeviceOpenedListener
    
    Java is along the lines of:
    public class OpenMidiReceiveDeviceListener implements MidiManager.OnDeviceOpenedListener {
        @Override
        public void onDeviceOpened(MidiDevice device) {
            mReceiveDevice = device;
            startReadingMidi(mReceiveDevice, 0/*mPortNumber*/);
        }
    }
    """
    # __javacontext__ = 'app'
    __javainterfaces__ = ['android/media/midi/MidiManager$OnDeviceOpenedListener']
    
    def __init__(self, callback_func):
        """ init listner, with a callback for when the port is open and running
        """
        self.port_casted = None
        self.callback_func = callback_func
        super(OpenMidiSendDeviceListener, self).__init__()
    # Landroid/media/midi/MidiManager$OnDeviceOpenedListener;
    @java_method('(Landroid/media/midi/MidiDevice;)V')
    def onDeviceOpened(self, device):
        port = device.openInputPort(0)
        port_casted = cast('android.media.midi.MidiInputPort', port)
        self.port_casted = port_casted
        
        # Uncomment if you want to test midi
        # self.play_test()
        # self.close()
        self.callback_func()
        
    def play_test(self):
        for i in range(1,5):
            # data = b'\x90\x3D\x78'
            # self.port_casted.send(data, 0, 3)
            self.note_on(b'\x78')
            time.sleep(1)
            self.note_off(b'\x78')
            
    def send_data_to_port(self, data):
        self.port_casted.send(data, 0, len(data))

    def send(self, data):
        self.send_data_to_port(data)

    def note_on(self, note):
        data = b'\x90\x3D' + note
        # self.port_casted.send(data, 0, 3)
        self.send_data_to_port(data)
        
    def note_off(self, note):
        data = b'\x80\x3D' + note
        self.send_data_to_port(data)
        
    def close(self):
        self.port_casted.close()
