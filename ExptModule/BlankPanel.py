'''
BlankPanel.py
  When the Response-panel is not necessary or not applicable, 
  this module fills in the response-panel.
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

class BlankPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel(parent.mainPanel, id=-1, pos=(0, 0), size=(10, 10))
        
    def Enable(self):
        print "\nPanel Enabled\n"
        
    def Disable(self):
        print "\nPanel Disabled\n"
