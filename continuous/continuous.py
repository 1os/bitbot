#!/usr/bin/python

import sys, os

sys.path.append('/snap/bitbot/current/lib/python2.7/site-packages/')

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

# Create a decoder with certain model
config = Decoder.file_config(
    os.path.join(os.environ.get('SNAP_COMMON'), 'sphinx.cfg'))

import pyaudio

samprate = int(
    config.get_float("-samprate")) if config.exists("-samprate") else 16000
buflen = 1024
waitfor = 5

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=samprate,
    input=True,
    frames_per_buffer=buflen)
stream.start_stream()

decoder = Decoder(config)
decoder.start_utt()
record = False
dataToSend = bytearray()
count = 0
print 'ready'
while True:
    buf = stream.read(buflen)
    if buf:
        if record == True:
            dataToSend.extend(buf)
            count += 1
            if count >= int(waitfor * samprate / buflen):
                count = 0
                record = False
                filerecord = open(
                    os.path.join(os.environ.get('SNAP_COMMON'), 'record.pcm'),
                    "wb")
                filerecord.write(dataToSend)
                dataToSend = bytearray()
                print 'done'
        decoder.process_raw(buf, False, False)
    else:
        break
    if decoder.hyp() != None:
        record = True
        print 'Yes sir?'
        decoder.end_utt()
        decoder.start_utt()