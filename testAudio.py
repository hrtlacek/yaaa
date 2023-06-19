from pyo import Server,Granulator,Sig,SndTable,HannTable,Trig,Phasor,Noise,OscTrig
from pyo import *
print("Audio host APIS:")
pa_list_host_apis()
pa_list_devices()
print("Default input device: %i" % pa_get_default_input())
print("Default output device: %i" % pa_get_default_output())

defOut = pa_get_default_output()

s = Server(duplex=0)
s.setOutputDevice(defOut)

# s = Server()
s.boot()
