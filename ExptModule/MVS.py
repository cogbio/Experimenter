'''
MVS.py
  This is a module for Experimenter to display images.
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

import math
from sys import platform
from os import path
from time import time, sleep
from random import randint, uniform, choice
from copy import copy

import wx, wx.media # external library; can be found in http://www.wxpython.org
import numpy as np # external library; can be found in http://www.numpy.org/

# --------------------------------------------------

def load_img(panel, file_path, iID=-1, posX=0.5, posY=0.5, width=None, height=None, h_flip=False):
    tmp_null_log = wx.LogNull() # this is for not seeing the tif Library warning
    img = wx.Image(file_path, wx.BITMAP_TYPE_ANY)
    del tmp_null_log # delete the null-log to restore the logging
    if width != None and height != None: img = img.Rescale(width, height)
    if h_flip: img = img.Mirror()
    imgSize = img.GetSize()
    imgPos = (int(panel.GetSize()[0] * posX - imgSize[0]/2), int(panel.GetSize()[1] * posY - imgSize[1]/2))
    bmp = img.ConvertToBitmap()
    loaded_img = wx.StaticBitmap(panel, iID, bmp, imgPos, imgSize)
    return loaded_img

# --------------------------------------------------

def load_movie(panel, file_path, id, pos=(0,0), size=(-1,-1), showControls=False):
    try:
        movie = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER,
                                         #szBackend=wx.media.MEDIABACKEND_DIRECTSHOW
                                         #szBackend=wx.media.MEDIABACKEND_QUICKTIME
                                         #szBackend=wx.media.MEDIABACKEND_WMP10
                                         )
        movie.Load(file_path)
        movie.SetInitialSize()
    except NotImplementedError:
        raise

    if size == (-1,-1): # if size is not determined
        size = movie.GetBestSize()
    else:
        movie.Size = size
    if pos == 'center': # if the position is a string, 'center'
        ### position it in the center
        panelSize = panel.GetSize()
        movie.Position = (panelSize[0]/2-size[0]/2, panelSize[1]/2-size[1]/2)
    else:
        movie.Position = pos

    if showControls: movie.ShowPlayerControls(flags = wx.media.MEDIACTRLPLAYERCONTROLS_STEP)      

    return movie

# --------------------------------------------------

def load_crosshair(panel, iID=-1, width=None, height=None):
    '''
      load the corsshair image in the center
    '''
    file_path = path.join('input', 'media', 'crosshair.png')
    img = wx.Image(file_path, wx.BITMAP_TYPE_ANY)
    if width != None and height != None: img = img.Rescale(width, height)
    imgSize = img.GetSize()
    imgPos = (int(panel.GetSize()[0] * 0.5 - imgSize[0]/2), int(panel.GetSize()[1] * 0.5 - imgSize[1]/2))
    bmp = img.ConvertToBitmap()
    loaded_img = wx.StaticBitmap(panel, iID, bmp, imgPos, imgSize)
    return loaded_img

# --------------------------------------------------

def img2buffer(img):
    '''
      input: wx.Image object
      output: the input image's width, height, RGB(A)-data
    '''
    w, h = img.GetWidth(), img.GetHeight()
    data = np.array(img.GetDataBuffer(), dtype='c')
    data = data.reshape( (h, w, 3) )
    if img.HasAlpha():
        data_A = np.empty( (h,w,4), 'c')
        data_A[...,:3] = data
        data_A[...,3] = np.array(img.GetAlphaBuffer(), dtype='c').reshape(h,w)
        return w, h, data_A
    else:
        return w, h, data
