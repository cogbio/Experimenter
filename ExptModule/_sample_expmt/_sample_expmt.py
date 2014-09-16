'''
_sample_expmt.py
  Experiment module file as a sample.
  This is not a real experiment, but just for showing how to play a 
  sound and display images.
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

import wx
from os import path
from time import sleep, time
from random import randint

from ExptModule.MAS import Output_AudioData
from ExptModule.MVS import load_img
from ExptModule.Common_func import destroy_objects, writeFile, get_time_stamp

debug = True

# ===========================================================

class SampleExpmtPanel:

    def __init__(self, parent, msgInterval = []):
        if debug: print "SampleExpmtPanel.__init__"

        self.parent = parent
        self.exptApp = parent.exptApp
        
        self.panel = wx.Panel(parent.mainPanel, id=-1, pos = parent.screenPos, size = parent.Size)
        self.audio = Output_AudioData( output_dev_keywords=['built-in'], 
                                       sample_width=2, 
                                       rate=44100, 
                                       wav_buffer=1024)
        self.imgs = []

    # --------------------------------------------------
        
    def presentStimulus(self, stimuli):
        if debug: print "SampleExpmtPanel.presentStimulus"

        for img in self.imgs: img.Destroy() # delete all the images
        self.imgs = []
        self.audio.init_sounds() # delete sounds from the previous trial

        self.stiimuli = stimuli
        delay_for_user_response_start = 3000 # in milliseconds
        # There will be 1 seconds of delay after showing each 3 upper images, therefore, 3000 ms in total.
        
        for i in range(self.stiimuli["NUM_STIMULI"]):
            stimulus =  self.stiimuli[str(i)]
            if '.wav' == stimulus["FILEPATH"][-4:].lower(): # sound file
                self.audio.load_sounds([stimulus["FILEPATH"]])
                self.audio.play_sound( snd_idx = len(self.audio.wfs)-1, 
                                       stream_idx = 0, 
                                       stop_prev_snd = False)
                delay_for_user_response_start += self.audio.sound_lengths[-1]
            else: # image file
                width = None; height = None; posX = 0.5; posY = 0.5
                if stimulus.has_key("WIDTH"): width = stimulus["WIDTH"]
                if stimulus.has_key("HEIGHT"): height = stimulus["HEIGHT"]
                if stimulus.has_key("POSX"): posX = stimulus["POSX"]
                if stimulus.has_key("POSY"): posY = stimulus["POSY"]
                self.imgs.append( load_img(panel = self.panel, 
                                           file_path = stimulus["FILEPATH"], 
                                           iID = i, # image id
                                           posX = posX, 
                                           posY = posY, 
                                           width = width, 
                                           height = height) )
                self.imgs[-1].name = path.split(stimulus["FILEPATH"])[1]
                ### show the first 3 images with 1 seconds delay, 
                ### then show the 4th and the 5th images together as choice images
                if 'st01' in self.imgs[-1].name:
                    self.imgs[-1].Hide()
                    wx.FutureCall(self.audio.sound_lengths[-1], self.imgs[-1].Show)
                elif 'st02' in self.imgs[-1].name:
                    self.imgs[-1].Hide()
                    wx.FutureCall(self.audio.sound_lengths[-1]+1000, self.imgs[-1].Show)
                elif 'st03' in self.imgs[-1].name:
                    self.imgs[-1].Hide()
                    wx.FutureCall(self.audio.sound_lengths[-1]+2000, self.imgs[-1].Show)
                elif ('st04' in self.imgs[-1].name) or ('st05' in self.imgs[-1].name):
                    self.imgs[-1].Bind(wx.EVT_LEFT_DOWN, self.OnClick, self.imgs[-1]) # Bind mouse-left-click with the image
                    self.imgs[-1].Hide()
                    wx.FutureCall(self.audio.sound_lengths[-1]+3000, self.imgs[-1].Show)
        return delay_for_user_response_start

    # --------------------------------------------------

    def OnClick(self, event):
        if debug: print "SampleExpmtPanel.OnClick"
        obj = event.GetEventObject()
        self.parent.HandleGUIResponse(obj.name)

    # --------------------------------------------------

    def OnTest(self, event):
        if debug: print "SampleExpmtPanel.OnTest"
        print 'T-key is pressed.'

    # --------------------------------------------------
