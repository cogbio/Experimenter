'''
WXCOG.py
  This is a module for Experimenter to generate some wxPython widgets
  with less code in the actual experiment script file.
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

import wx # external library; can be found in http://www.wxpython.org

# --------------------------------------------------

def generate_button(bId=-1, parent=None, b_label='button', b_size=(100, 20), b_pos=(0.5, 0.5)):
    '''
      Generate a button with given parameters and return it
    '''
    button = wx.Button(parent, id=bId, label=b_label, size=b_size)
    p_size = parent.GetSize()
    b_size = button.GetSize()
    posX = p_size[0] * b_pos[0] - b_size[0] / 2
    posY = p_size[1] * b_pos[1] - b_size[1] / 2
    button.SetPosition((posX, posY))
    return button

# --------------------------------------------------

def generate_button_likert_scale(start_id, parent, pos, number_of_buttons, names=['Least', 'Medium', 'Most']):
    '''
      Generate a Likert-scale with buttons
      start_id: starting id of the liker-scale-button
    '''
    ret_btns = []
    b_size = (100, 30)
    interval = 5.0 # intervals between buttons
    posX_inc_factor = (b_size[0]+interval)/parent.GetSize()[0]
    posX = pos[0] - (number_of_buttons/2*posX_inc_factor)

    for i in range(number_of_buttons):
        bID = start_id + i
        b_pos = (posX, pos[1])
        posX += posX_inc_factor
        if i == 0: b_label = names[0]
        elif i == number_of_buttons/2: b_label = names[1]
        elif i == number_of_buttons-1: b_label = names[2]
        else:            
            if i < number_of_buttons/2: b_label = '<'
            elif i > number_of_buttons/2: b_label = '>'
        ret_btns.append( generate_button(bID, parent, b_label, b_size, b_pos) )
    return ret_btns

# ===========================================================

class TimeoutBar(object):
    def __init__(self, parent, p_size, timeoutTime, gUpdateTimeInterval, gText):
        '''
          Generates the TimeoutBar
        '''
        self.timeoutTime = timeoutTime
        self.gUpdateTimeInterval = gUpdateTimeInterval
        self.gauge = wx.Gauge(parent.panel, id = -1, range = timeoutTime, pos = (0, 0), size = (p_size[0] - 50, -1))
        self.gauge.Position = (p_size[0]/2 - self.gauge.GetSize()[0]/2, p_size[1]/2 - self.gauge.GetSize()[1]/2)
        self.gauge.SetBezelFace(10)
        self.gauge.SetShadowWidth(1)
        self.gaugeText = wx.StaticText(parent.panel, pos = (0, 0), label =  gText)
        self.gaugeText.Position = (p_size[0]/2 - self.gaugeText.GetSize()[0]/2, self.gauge.Position[1])

        timerID_TimoutBar = 199
        self.count = 0
        self.gaugeTimer = wx.Timer(self, timerID_TimoutBar)
        self.gaugeTimer.Start(gUpdateTimeInterval)
        wx.EVT_TIMER(self, timerID_TimoutBar, self.OnTimoutBarTimer)

    # --------------------------------------------------


    def OnTimoutBarTimer(self, event):
        self.count += 1
        currTimeGaugePos = self.gUpdateTimeInterval * self.count
        self.gauge.SetValue(currTimeGaugePos)
        if currTimeGaugePos >= self.timeoutTime: self.stopTimeoutBar()

    # --------------------------------------------------

    def stopTimeoutBar(self):
        self.gaugeTimer.Stop()
        self.gaugeTimer.Destroy()
        self.gaugeText.Destroy()
        self.gauge.Destroy()

# ===========================================================

class Slider_class(object):
    def __init__(self, parent, params):
        label = params[0]
        pos = params[1]
        size = params[2]
        width = size[0]
        height = size[1]
        minVal = params[3]
        maxVal = params[4]
        startVal = params[5]
        labelOffset = params[6]

        middleY = int(height/2.0)
        self.slider = wx.Slider(parent.panel, 100, 5, minVal, maxVal, pos=(0, middleY), size = (width, -1),
                           style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS )

        self.minText = wx.StaticText(parent.panel, -1, "min", pos = (10, middleY+labelOffset))
        self.maxText = wx.StaticText(parent.panel, -1, "max", pos = (width-30, middleY+labelOffset))
        self.labelText = wx.StaticText(parent.panel, -1, label, pos = (int(width/2.0)+labelOffset, 10))
        
        self.slider.SetTickFreq(5, 1) # Does not appear to work, on a Mac

        # Bind the OnClick, using the enclosing frame. WARNING: This assumes that 'parent' is a frame (not a panel)
        # Actually better to let the calling object do the binding, so commented out
        parent.parent.Bind(wx.EVT_SLIDER, self.OnClick, self.slider) 

    # --------------------------------------------------

    def OnClick(self, event):
        ### Sliders send a stream of events to both mouse down and drag events
        ### We only want a final value, so need to check the mouse state
        mouseState = wx.GetMouseState()
        if (mouseState.leftDown == False and mouseState.rightDown == False):
            self.parent.Slider_response(self.slider.GetValue())

# ===========================================================
