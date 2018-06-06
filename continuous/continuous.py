#!/usr/bin/python

import sys
import os

# sys.path.append('/snap/bitbot/current/usr/lib/python2.7/dist-packages/')
# sys.path.append('/snap/bitbot/current/lib/python2.7/site-packages/')

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

# Create a decoder with certain model
config = Decoder.file_config(
    os.path.join(os.environ.get('SNAP_COMMON'), 'sphinx.cfg'))

print "i'm going to watch " + config.get_string("-keyphrase")

import pyaudio
import audioop
import wave


class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """
        self.stream.close()
        self.p.terminate()


samprate = int(config.get_float("-samprate")
               ) if config.exists("-samprate") else 16000
buflen = 1024 * 3
waitfor = 5

p = pyaudio.PyAudio()

count = 0
lastInputDevice = 0
lastInputDeviceRate = 16000
while count < p.get_device_count():
    device = p.get_device_info_by_index(count)
    if device.get("maxInputChannels") > 0:
        print device
        print ""
        lastInputDevice = count
        lastInputDeviceRate = int(device.get("defaultSampleRate"))
    count = count + 1

print "selected device", lastInputDevice, "sample rate", lastInputDeviceRate

curState = None


def resample(data, rate):
    global curState
    (newfragment, state) = audioop.ratecv(data, 2, 1, rate, samprate, curState)
    curState = state
    return newfragment


stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=lastInputDeviceRate,
    input=True,
    frames_per_buffer=buflen,
    input_device_index=lastInputDevice)
stream.start_stream()

decoder = Decoder(config)
decoder.start_utt()
record = False
dataToSend = bytearray()
count = 0
print 'ready'

a = AudioFile(os.path.join(os.environ.get('SNAP'), 'sounds/Mallet.wav'))
a.play()
a.close()

while True:
    buf = resample(stream.read(buflen), lastInputDeviceRate)
    if buf:
        if record == True:
            dataToSend.extend(buf)
            count += 1
            if count >= int(waitfor * lastInputDeviceRate / buflen):
                count = 0
                record = False
                filerecord = open(
                    os.path.join(os.environ.get('SNAP_COMMON'), 'record.pcm'),
                    "wb")
                filerecord.write(dataToSend)
                dataToSend = bytearray()
                print 'done'
                a = AudioFile(os.path.join(
                    os.environ.get('SNAP'), 'sounds/Slick.wav'))
                a.play()
                a.close()
        decoder.process_raw(buf, False, False)
    else:
        break
    if decoder.hyp() != None:
        record = True
        print 'Yes sir?'
        a = AudioFile(os.path.join(
            os.environ.get('SNAP'), 'sounds/Rhodes.wav'))
        a.play()
        a.close()
        decoder.end_utt()
        decoder.start_utt()
