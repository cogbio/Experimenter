'''
MAS.py
  This is a module for Experimenter to play auditory stimuli, and rec-
  ording sound from microphone.
----------------------------------------------------------------------
Copyright (C) 2014 Jinook Oh, W. Tecumseh Fitch for ERC Advanced Grant 
SOMACCA # 230604 
- Contact: jinook.oh@univie.ac.at, tecumseh.fitch@univie.ac.at

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from copy import copy
from sys import argv
from time import time, sleep
from threading import Thread
import wave, Queue
import wx # external library; can be found in http://www.wxpython.org
import pyaudio # external library; can be found in http://people.csail.mit.edu/hubert/pyaudio/
import numpy as np # external library; can be found in http://www.numpy.org/

# --------------------------------------------------

def load_sound(wave_file_path):
    '''
      load the sound (wx.Sound) with the given file path
      calculate the length of the sound.
    '''
    wav = wave.open(wave_file_path, "r")
    numFrames = wav.getnframes() # note that this is accurate whether for stereo or mono
    sRate = float(wav.getframerate())
    soundlength = round(1000*numFrames/sRate) # length in msecs
    wav.close()
    sound = wx.Sound(wave_file_path)
    return soundlength, sound

# ===========================================================

class Output_AudioData:
    '''
      play sound using pyAudio
      can use multiple streams(physically different ouput devices)
    '''
    def __init__(self, output_dev_keywords=['built-in'], sample_width=2, rate=44100, wav_buffer=1024):
    # sample_width: desired sample width in bytes (1, 2, 3, or 4)
        self.pa = pyaudio.PyAudio()
        self.w_buffer = wav_buffer
        self.sample_width = sample_width
        self.rate = rate
        self.ps_th = [] # play-sound thread
        self.ps_q = [] # play_sound queue
        self.init_sounds()
        
        for i in range(len(output_dev_keywords)): output_dev_keywords[i] = output_dev_keywords[i].lower()
        self.device_index_list = self.find_output_device(output_dev_keywords)

        self.streams = []
        self.open_output_streams()
        print '%i streams are open.'%len(self.streams)

    # --------------------------------------------------

    def init_sounds(self):
        if self.ps_th != []:
            for i in range(len(self.ps_th)):
                while self.ps_th[i] != None: sleep(0.1) # a sound is playing. block until it finishes before initialization
        self.wfs = []
        self.sound_lengths = []

    # --------------------------------------------------

    def load_sounds(self, snd_files=[]):
        if snd_files == []: return
        for snd_file in snd_files:
            self.wfs.append(wave.open(snd_file, 'rb'))
            numFrames = self.wfs[len(self.wfs)-1].getnframes() # this is accurate whether for stereo or mono
            sRate = float(self.wfs[len(self.wfs)-1].getframerate())
            self.sound_lengths.append(round(1000*numFrames/sRate)) # length in msecs

    # --------------------------------------------------

    def remove_sounds(self, rem_idx=[]):
        '''
          remove sounds with indices, indicated in rem_idx
        '''
        if rem_idx == []: return
        for ri in rem_idx:
            self.wfs[ri] = None
            self.sound_lengths[ri] = None
        while None in self.wfs: self.wfs.remove(None)
        while None in self.sound_lengths: self.sound_lengths.remove(None)

    # --------------------------------------------------

    def open_output_streams(self):
        for i in range(len(self.device_index_list)):
            try:
                self.streams.append( self.pa.open(format = self.pa.get_format_from_width(self.sample_width),
                                                channels = 1,
                                                rate = self.rate,
                                                output_device_index = self.device_index_list[i],
                                                output = True) )
                self.ps_th.append(None)
                self.ps_q.append(Queue.Queue())
            except:
                pass

    # --------------------------------------------------

    def close_output_streams(self):
        if len(self.streams) > 0:
            for i in range(len(self.streams)):
                self.streams[i].close()
        self.streams = []

    # --------------------------------------------------

    def find_output_device(self, output_dev_keywords):
        built_in_output_idx = -1
        device_index_list = []            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i) 
            print "Device #%i: %s"%(i, devinfo["name"])
            for j in range(len(output_dev_keywords)):
                if output_dev_keywords[j] in devinfo["name"].lower():
                    if devinfo["maxOutputChannels"] > 0:
                        print( "Found an usb-audio-output: device %d - %s"%(i,devinfo["name"]) )
                        device_index_list.append(i)
        if device_index_list == []:
            print( "No preferred audio-output found; using default output device." )
        return device_index_list

    # --------------------------------------------------

    def play_sound_run(self, snd_idx, stream_idx=0):
        audio_output_data = self.wfs[snd_idx].readframes(self.w_buffer)
        msg = ''
        while audio_output_data != '':
            self.streams[stream_idx].write(audio_output_data)
            audio_output_data = self.wfs[snd_idx].readframes(self.w_buffer)
            try: msg = self.ps_q[stream_idx].get(False)
            except Queue.Empty: pass
            if msg == 'terminate': break
        self.wfs[snd_idx].rewind()
        self.ps_th[stream_idx] = None

    # --------------------------------------------------

    def play_sound(self, snd_idx=0, stream_idx=0, stop_prev_snd=False):
        '''
          This function works with 'play_sound_run'. Generate a thread and use it for playing a sound once.
          stop_prev_snd = False; means that if the requested stream is busy, it ignores the request to play sound.
        '''
        if self.ps_th[stream_idx] != None: # playing previous sound
            if stop_prev_snd == True:
                self.ps_q[stream_idx].put('terminate', True, None)
                self.ps_th[stream_idx].join()
                self.ps_th[stream_idx] = None
            else:
                return False
        ### start sound playing
        self.ps_th[stream_idx] = Thread(target=self.play_sound_run, args=(snd_idx, stream_idx,))
        self.ps_th[stream_idx].start()
        return True

# ===========================================================

class Input_AudioData:
    '''
      Connect to a microphone and retrieve data from it, and record.
      Also it has some other functions for getting RMS amplitude,
      applying some filter...
    '''
    def __init__(self, input_dev_keywords=["input", "h4"], rate=44100, channels=1):
        self.input_dev_keywords = input_dev_keywords
        self.format = pyaudio.paInt16
        self.rate = rate # sampler rate
        self.sampWidth = 2
        self.channels = channels
        self.nyq_rate = self.rate/2.0
        self.cutoff_hz = 500.0 # cut-off frequency of the FIR filter
        self.short_normalize = (1.0/32768.0)
        self.input_block_time = 0.04
        self.input_frames_per_block = int(self.rate*self.input_block_time)
        self.freq_res = self.rate/float(self.input_frames_per_block) # Frequency Resolution

        self.pa = pyaudio.PyAudio()
        self.device_index = self.find_input_device()
        self.stream = self.open_mic_stream()
        self.recordingData = None

    # --------------------------------------------------

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            if devinfo["maxInputChannels"] > 0:
                print( "Device %d: %s"%(i,devinfo["name"]) )
                for keyword in self.input_dev_keywords:
                    if keyword.lower() in devinfo["name"].lower():
                        print( "Found an audio-input: device %d - %s"%(i,devinfo["name"]) )
                        device_index = i
        if device_index == None:
            print( "No preferred input found; using default input device." )
        return device_index # use the last device

    # --------------------------------------------------

    def open_mic_stream( self ):
        stream = self.pa.open( format = self.format,
                               channels = self.channels,
                               rate = self.rate,
                               input = True,
                               input_device_index = self.device_index,
                               frames_per_buffer = self.input_frames_per_block )
        return stream

    # --------------------------------------------------

    def listen(self):
        audio_data = None
        try:
            audio_data = np.fromstring(self.stream.read(self.input_frames_per_block), dtype=np.short).tolist()
            #audio_data = audio_data * self.short_normalize
            #self.audio_data = self.FIR_filter(audio_data)
            #audio_data = audio_data * 32768
        except IOError, e:
            print( "Error : %s"%(e) ) # When an error (such as buffer_overflow) occurs
            self.listen() # read the data from mic again.
        return audio_data

    # --------------------------------------------------

    def data_write_to_wave(self, recordingData, sound_duration, wave_file_path):
        snd_file = wave.open(wave_file_path, 'wb')
        durSamps = int(sound_duration*self.rate)
        snd_file.setparams((self.channels, self.sampWidth, self.rate, durSamps, 'NONE', 'noncompressed'))
        snd_file.writeframes(np.array(recordingData, dtype=np.int16).tostring())
        snd_file.close()

    # --------------------------------------------------

    def FIR_filter(self, signal):
        '''
          FIR High pass filter
        '''
        numtaps = 31 # length of the filter (number of coefficients; filter order + 1)
        fir_coeff = firwin(numtaps, [self.cutoff_hz/self.nyq_rate, 0.99], pass_zero=False) # Use firwin to create a lowpass FIR filter
        filtered_signal = lfilter(fir_coeff, 1.0, signal)
        return filtered_signal

    # --------------------------------------------------

    def get_rms(self):
        '''
          RMS Amplitude
        '''
        count = len(self.audio_data)/2
        sum_squares = 0.0
        n = self.audio_data * self.short_normalize
        n = n ** 2
        sum_squares = sum(n)
        rms = sqrt(sum_squares/count)
        return rms

    # --------------------------------------------------

    def close(self):
        self.stream.close()
        self.pa.terminate()

    # --------------------------------------------------

    def recording(self, recording_time, wave_file_path):
        r_t = Thread(target=self.recording_run, args=(recording_time, wave_file_path,))
        r_t.start()

    # --------------------------------------------------

    def recording_run(self, recording_time, wave_file_path):
        recording_time = recording_time / 1000.0
        rec_start_time = time()
        recordingData = []
        while time() - rec_start_time <= recording_time+0.08:
        # +0.08 since it's always 0.08 less than its intended recording length.(?)
            audio_data = self.listen()
            if audio_data != None: recordingData += audio_data
        self.data_write_to_wave(recordingData, recording_time, wave_file_path)

# ===========================================================

