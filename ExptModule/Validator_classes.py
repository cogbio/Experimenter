'''
Validator_classes.py
  This is a module for Experimenter to validate a value in a TextCtrl 
  widget.
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

import string
import wx # external library; can be found in http://www.wxpython.org

# ===========================================================

class TextValidator(wx.PyValidator):
     def __init__(self):
         wx.PyValidator.__init__(self)

     # --------------------------------------------------

     def Clone(self):
         return TextValidator()

     # --------------------------------------------------

     def Validate(self, win):
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()

         if len(text) == 0:
             wx.MessageBox("Please enter value in the " + textCtrl.Name + " field.")
             textCtrl.SetBackgroundColour("pink")
             textCtrl.SetFocus()
             textCtrl.Refresh()
             return False
         
         for i in range(len(text)):
             if text[i] in string.digits:
                 wx.MessageBox("Letters only!")
                 textCtrl.SetBackgroundColour("pink")
                 textCtrl.SetFocus()
                 textCtrl.Refresh()
                 return False
                 
         for i in range(len(text)):
             if text[i] in string.punctuation:   
                 wx.MessageBox("Letters only!")
                 textCtrl.SetBackgroundColour("pink")
                 textCtrl.SetFocus()
                 textCtrl.Refresh()
                 return False
            
         textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
         textCtrl.Refresh()
         return True

     # --------------------------------------------------

     def TransferToWindow(self):
         '''
           Transfer data from validator to window.
           The default implementation returns False, indicating that an error
           occurred.  We simply return True, as we don't do any data transfer.
         '''
         return True # Prevent wxDialog from complaining.

     # --------------------------------------------------

     def TransferFromWindow(self):
         '''
           Transfer data from window to validator.
           The default implementation returns False, indicating that an error
           occurred.  We simply return True, as we don't do any data transfer.
         '''
         return True # Prevent wxDialog from complaining.

# ===========================================================

class NumberValidator(wx.PyValidator):
     def __init__(self):
         wx.PyValidator.__init__(self)

     # --------------------------------------------------

     def Clone(self):
         return NumberValidator()

     # --------------------------------------------------

     def Validate(self, win):
         numberCtrl = self.GetWindow()
         number = str(numberCtrl.GetValue())
         
         if len(number) == 0:
             wx.MessageBox("Please enter value in the " + numberCtrl.Name + " field.")
             numberCtrl.SetBackgroundColour("pink")
             numberCtrl.SetFocus()
             numberCtrl.Refresh()
             return False
             
         for i in range(len(number)):
             if number[i] in string.letters:
                 wx.MessageBox("Numbers only.")
                 numberCtrl.SetBackgroundColour("pink")
                 numberCtrl.SetFocus()
                 numberCtrl.Refresh()
                 return False
            
         for i in range(len(number)):
             if number[i] in string.punctuation:
                 wx.MessageBox("Numbers only.")
                 numberCtrl.SetBackgroundColour("pink")
                 numberCtrl.SetFocus()
                 numberCtrl.Refresh()
                 return False
   
         numberCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
         numberCtrl.Refresh()
         return True

     # --------------------------------------------------

     def TransferToWindow(self):
         return True # Prevent wxDialog from complaining.

     # --------------------------------------------------

     def TransferFromWindow(self):
         return True # Prevent wxDialog from complaining.

# ===========================================================

class CharValidator(wx.PyValidator):
     '''
       validating each character input
       flag : "no-letter" or "no-digit"
     '''
     def __init__(self, flag):
          wx.PyValidator.__init__(self)
          self.flag = flag
          self.Bind(wx.EVT_CHAR, self.OnChar)

     # --------------------------------------------------

     def Clone(self):
          return CharValidator(self.flag)

     # --------------------------------------------------

     def Validate(self, win):
          return True

     # --------------------------------------------------

     def TransferToWindow(self):
          return True

     # --------------------------------------------------
     
     def TransferFromWindow(self):
          return True

     # --------------------------------------------------

     def OnChar(self, evt):
          key = chr(evt.GetKeyCode())
          if self.flag == "no-letter" and key in string.letters:
               return
          if self.flag == "no-digit" and key in string.digits:
               return
          evt.Skip()

