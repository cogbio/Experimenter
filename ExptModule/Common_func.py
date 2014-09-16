'''
Common_func.py
  This has a set of functions commonly used in Experimenter.
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

import string, glob, os, hashlib, pickle
from time import time, localtime
from datetime import datetime
import wx # external library; can be found in http://www.wxpython.org
import input.config
settings = input.config.settings
settings = dict( map (lambda (key, value): (string.upper(key), value) , settings.items() ) ) # make it to have upper-case keys; so it's case-insensitive
if settings["COMM_ARDUINO"]: import serial # external library; can be found in http://pyserial.sourceforge.net/

dictHexadecimal = { '0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15 }

# --------------------------------------------------

def get_time_stamp():
    ts = datetime.now()
    ts = ('%.4i_%.2i_%.2i_%.2i_%.2i_%.2i_%.6i')%(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, ts.microsecond)
    return ts

# --------------------------------------------------

def writeFile(filePath, txt):
    '''
      Function for writing texts into a file
    '''
    file = open(filePath, 'a')
    if file:
        file.write(txt)
        file.close()
    else:
        raise Exception("unable to open [" + filePath + "]")

# --------------------------------------------------

def uppsercaseTuples(dictItems):
    '''
      Get the items(from a dictionary) 
      and make the key to the upper-case 
      then return it.
    '''
    return (string.upper(dictItems[0]), dictItems[1])

# --------------------------------------------------

def uppercaseDict(passedDict):
    '''
      Get the dictionary, 
      change the keys to the upper-case
      then return it.
    '''
    return dict(map(uppsercaseTuples, passedDict.items()))

# --------------------------------------------------

def HexToDec(inCode):
    '''
      Convert Hexadecimalcode to Decimal number.
      inCode is a string of hexadecimal code such as 'FF'
    '''
    inCode = inCode.strip()
    ret_num = 0
    for i in range(len(inCode)):
        _number = dictHexadecimal[ inCode[i].upper() ]
        ret_num += _number * (16 ** ( len(inCode) - (i+1) ))
    return ret_num

# --------------------------------------------------

def try_open(port):
    '''
      function for Arduino-chip connection
    '''
    try:
        port = serial.Serial(port, 9600, timeout = 0)
    except serial.SerialException:
        return None
    else:
        return port

# --------------------------------------------------

def serial_scan(ARDUINO_USB_GLOB):
    '''
      function for Arduino-chip connection
    '''
    for fn in glob.glob(ARDUINO_USB_GLOB):
        port = try_open(fn)
        if port is not None:
            yield port

# --------------------------------------------------

def chooseFile(parent, msg, extension="*"):
    '''
      choosing a file using the wx.FileDialog
    '''
    currDir = os.getcwd()
    dlg = wx.FileDialog(parent, msg, currDir, "", "*."+extension, wx.OPEN)
    dlgResult = dlg.ShowModal()
    if dlgResult == wx.ID_OK:
        filename = dlg.GetFilename()
        dirname = dlg.GetDirectory()
        dlg.Destroy()
        file = os.path.join(dirname, filename)
    elif dlgResult == wx.ID_CANCEL:
        dlg.Destroy()
        file = None
    return file

# --------------------------------------------------

def generateHash():
    '''
      generate a unique ID and return as string
    '''
    ha = hashlib.sha1()
    ha.update(str(time.time()))
    return ha.hexdigest()

# --------------------------------------------------

def destroy_objects():
    '''
      destory all the objects with consecutive IDs
    '''
    obj = wx.FindWindowById(0)
    i = 0
    while obj is not None:
        obj.Destroy()
        i += 1
        obj = wx.FindWindowById(i)

# --------------------------------------------------

def GridCoordToIndex(row, col, cols):
    '''
      Convert a row and column to an index for a grid of specified number of rows and columns
      Uses Western reading standard (starting in upper left and moving right and down)
    '''
    index = (row*cols)+col
    return index

# --------------------------------------------------

def GridIndexToCoord(index, cols):
    '''
      Convert a row and column to an index for a grid of specified number of rows and columns
      Uses Western reading standard (starting in upper left and moving right and down)
    '''
    row = index / cols
    col = index % cols
    return row, col

# --------------------------------------------------

def degreesToRadians(degrees):
    radians = degrees * pi/180.0
    return radians

# --------------------------------------------------

def radiansToDegrees(radians):
    degrees = radians * 180.0/pi
    return degrees

# --------------------------------------------------

def change_bg_color(panel, color = 'hex/AA,AA,AA'):
    '''
      changing the given panel's bg-color
    '''
    bgColor = color.split("/")
    if len(bgColor) > 1: # It's a hexadecimal code
        RGBcode = bgColor[1].split(",")
        RGBcode = HexToDec(RGBcode) # Converting the hexadecimal-code to the decimal-code
        color = ( wx.Colour(RGBcode[0], RGBcode[1], RGBcode[2]) )
    panel.SetBackgroundColour(color)
    panel.Refresh()
    #try: wx.SafeYield()
    #except: pass

# --------------------------------------------------

def monitoring_func(inPanel, outPanel, m_img_id, ratio = 1, progress_info = [], coord = [-1,-1]):
    '''
      Copying the inPanel to the outPanel for monitoring.
      m_img_id is the ID for the image getting created on outPanel
      ratio is the ratio of the widht & height. 0.5 ratio --> 0.25 size-ratio
    '''
    dcScreen = wx.WindowDC(inPanel) #Create a DC for the inPanel
 
    bitmapWidth = inPanel.GetSize()[0]
    bitmapHeight = inPanel.GetSize()[1]
    
    bmp = wx.EmptyBitmap(bitmapWidth, bitmapHeight, depth = -1)
    memDC = wx.MemoryDC()  #Create a memory DC that will be used to copy the screen
    memDC.SelectObject(bmp) # Associate the bitmap to the memoryDC
    # Now Blit (in this case copy) the actual screen to the memory DC and thus the Bitmap
    memDC.Blit( 0, 0, # xdest, ydest Copy to these X, y coordinates # subtract away the window bar area
                bitmapWidth, # width of copied rect - must be shared by source and dest
                bitmapHeight, # height of copied rect - must be shared by source and dest
                dcScreen, # source DC from which to copy
                0,0 )

    if ratio != 1: # if the ratio is not 1, draw the outline
        memDC.SetBrush(wx.Brush((0,0,0), wx.TRANSPARENT))
        memDC.DrawRectangle(0, 0, bitmapWidth-1, bitmapHeight-1)

    if coord != [-1,-1]: # some (mouse-click) coordinates were passed.
        memDC.SetBrush(wx.Brush((0,0,0), wx.SOLID))
        memDC.DrawEllipse(coord[0]-15, coord[1]-15, 30, 30)


    # Select the Bitmap out of the memory DC by selecting a new uninitialized Bitmap
    memDC.SelectObject(wx.NullBitmap)

    # Change the monitoring size
    if ratio != 1:
        bitmapWidth = bitmapWidth * ratio
        bitmapHeight = bitmapHeight * ratio
        img = bmp.ConvertToImage()
        img.Rescale(bitmapWidth, bitmapHeight)
        bmp = img.ConvertToBitmap()
        txt = wx.StaticText(outPanel, m_img_id+1, pos = (10 , bitmapHeight+10), label = '* Monitoring ratio of width && height: %i %%'%int(ratio*100))
        txt.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))

    if len(progress_info) > 0: # there's the progress-info
        txt = wx.StaticText(outPanel, 
            m_img_id+2, 
            pos = (10 , bitmapHeight+30), 
            label = '* Progress-Info: Trial [%i/%i], Section [%i/%i]'%(progress_info[0], progress_info[1], progress_info[2], progress_info[3]))
        txt.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))

    wx.StaticBitmap(outPanel, m_img_id, bmp, (0,0), (bitmapWidth, bitmapHeight)) # draw on the output panel

# --------------------------------------------------

def save(exptApp, savePath):
    '''
      save the current point in the session and exptDetails
    '''
    _s_info = ""
    for key in exptApp.expt.subjectInfo.iterkeys():
        _s_info += exptApp.expt.subjectInfo[key].strip().replace(' ', '-') + "_"
    _s_info = _s_info.rstrip("_")
    fileName = "%s_%s.sav"%(_s_info, get_time_stamp())
    f = open(os.path.join(savePath, fileName), "w") 
    if f:
        _txt = "Experiment started at, %s\n"%exptApp.expt.exptDateTime
        _txt += "Subject info: \n"
        for key in exptApp.expt.subjectInfo.iterkeys():
            _txt += "%s, %s\n"%(key, exptApp.expt.subjectInfo[key])
        _txt += "========================\n"
        f.write(_txt)
        f.write("#SAVEDATA" + '\n')
        f.write(str(exptApp.expt.trialCounter) + '\n')
        f.write(str(exptApp.expt.sectionCounter) + '\n')
        f.write(str(exptApp.expt.exptDataFileName) + '\n')
        tmpStr = ''
        for e in exptApp.expt.sectionIndices: tmpStr += str(e) + ","
        tmpStr = tmpStr.rstrip(",")
        f.write(tmpStr + '\n')
        tmpStr = ''
        for e in exptApp.expt.trialIndices: tmpStr += str(e) + ","
        tmpStr = tmpStr.rstrip(",")
        f.write(tmpStr + '\n')
        f.write(str(exptApp.exptDetails))
        f.close()

        writeFile(exptApp.expt.exptDataFileName, "# The session was saved @ %s\n"%get_time_stamp())
    else:
        raise Exception("unable to save.")
    return fileName

# --------------------------------------------------

def load(file, exptApp):
    '''
      load a file to restore the point where in the session and EventFile(exptDetails)
    '''
    f = open(file, "r")
    if f:
        flag_start = False
        data = []
        for line in f:
            line = line.strip()
            if flag_start:
                data.append(line)
            if line == '#SAVEDATA': flag_start = True
        f.close()
        #os.remove(exptApp.expt.exptDataFileName) # delete the file loaded with the start of the program.
        os.remove(file) # delete the saved data file.
        exptApp.expt.trialCounter = int(data[0])
        exptApp.expt.sectionCounter = int(data[1])
        exptApp.expt.exptDataFileName = data[2]
        exptApp.expt.sectionIndices = data[3].split(",")
        for i in range(len(exptApp.expt.sectionIndices)): exptApp.expt.sectionIndices[i] = int(exptApp.expt.sectionIndices[i])
        exptApp.expt.trialIndices = data[4].split(",")
        for i in range(len(exptApp.expt.trialIndices)): exptApp.expt.trialIndices[i] = int(exptApp.expt.trialIndices[i])
        from ast import literal_eval
        exptApp.exptDetails = literal_eval(data[5])

        writeFile(exptApp.expt.exptDataFileName, "# The session was loaded @ %s\n"%get_time_stamp())
    else:
        msg = "unable to load the file."
        recordLog(msg)
        raise Exception(msg)

# --------------------------------------------------

