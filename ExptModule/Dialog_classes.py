'''
Dialog_classes.py
  This is a module for Experimenter to show dialoges for asking parti-
  cipant's information before experiment, showing any message during
  the experiment, asking questions after the experiment.
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

from math import ceil
import wx, Validator_classes

# ===========================================================

class PopupDialog(wx.Dialog):
    '''
      General Popup_Message Dialog
    '''
    def __init__(self, parent = None, id = -1, title = "Message", inString = "", pos = None, size = (200, 150), cancel_btn = True):
        wx.Dialog.__init__(self, parent, id, title)
        self.SetSize(size)
        if pos == None: self.Center()
        else: self.SetPosition(pos)
        txt = wx.StaticText(self, -1, label = inString, pos = (20, 20))
        txt.SetSize(size)
        txt.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        txt.Wrap(size[0]-30)
        okButton = wx.Button(self, wx.ID_OK, "OK")
        b_size = okButton.GetSize()
        okButton.SetPosition((size[0] - b_size[0] - 20, size[1] - b_size[1] - 40))
        okButton.SetDefault()
        if cancel_btn == True:
            cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
            b_size = cancelButton.GetSize()
            cancelButton.SetPosition((size[0] - b_size[0]*2 - 40, size[1] - b_size[1] - 40))

# ===========================================================

class NameAgeDialog(wx.Dialog):
    '''
      Asking some info about the participant at the beginning of the Experimenter
    '''
    def __init__(self, parent = None, id = -1, title = "Dialog Subclass", size = (300, 270) ):
        wx.Dialog.__init__(self, parent, id, title, size = size)

        self.Center()
        dlgWidth = self.GetSize()[0]

        nameTitle = wx.StaticText(self, -1, label = "Name:", pos = (15, 15))
        self.name = wx.TextCtrl(self, value = "Joe Schmo", pos = (80, 15), validator = Validator_classes.TextValidator())

        ageTitle = wx.StaticText(self, -1, label = "Age:", pos = (15, 65))
        self.ageValue = wx.TextCtrl(self, value = "23", pos = (80, 65), validator = Validator_classes.NumberValidator())
        
        self.sex = wx.RadioBox(self, -1, "Gender:", (80, 100), wx.DefaultSize, ["Female", "Male"])
        
        okButton = wx.Button(self, wx.ID_OK, "OK")
        btnWidth = okButton.GetSize()[0]
        okButton.Position = (dlgWidth/2 - btnWidth - 20, 175)
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btnWidth = cancelButton.GetSize()[0]
        cancelButton.Position = (dlgWidth/2 + 20, 175)

    # --------------------------------------------------

    def GetValues(self):
        values = dict( [ ["name", self.name.GetValue()], ["age", self.ageValue.GetValue()],
                         ["sex", self.sex.GetStringSelection()] ] )
        return values

# ===========================================================

class Post_Q_Dialog(wx.Dialog):
    '''
      Post-experiment questionnaire Dialog
      Example of 'inString' in using Post_Q_Dialog
      Q_string = {}
      Q_string["number_of_questions"] = 3
      Q_string[0] = {}
      Q_string[0]["type"] = 'text'
      Q_string[0]["question"] = '1. Question 1.'
      Q_string[1] = {}
      Q_string[1]["type"] = 'checkbox'
      Q_string[1]["question"] = '2. Select options.(Check-box)'
      Q_string[1]["options"] = ['Option1', 'Option2', 'Option3']
      Q_string[2] = {}
      Q_string[2]["type"] = 'radiobutton'
      Q_string[2]["question"] = '3. Select options.(Radio-button)'
      Q_string[2]["options"] = ['Option1', 'Option2', 'Option3']
    '''
    def __init__(self, parent = None, id = -1, title = "Post Questionnaire", inString = {}, size = (200, 150)):
        if len(inString) == 0:
            errMsg = 'Parameter is not proper; Length of inString is 0.'
            error = wx.MessageBox(errMsg, 'ERROR!')
            return

        wx.Dialog.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        _width_f = 8
        self.inString = inString
        the_font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        Q_items = []
        posY = 10
        for i in range(inString["number_of_questions"]):
            txt = wx.StaticText(self, -1, label = inString[i]["question"], pos = (10, posY))
            txt.SetFont(the_font)
            txt.Wrap(size[0]-20)
            _lines = ceil((len(inString[i]["question"]) * _width_f)/float(size[0]))
            posY += _lines * 20
            if inString[i]["type"] == 'text':
                Q_items.append(wx.TextCtrl(self, id=-1, value = "", pos = (10, posY), size = (300, 50), style=wx.TE_MULTILINE))
                posY += 70
            elif inString[i]["type"] == 'checkbox':
                Q_items.append([])
                for j in range(len(inString[i]["options"])):
                    Q_items[len(Q_items)-1].append(wx.CheckBox(self, id=-1, label=inString[i]["options"][j], pos = (10, posY)))
                    posY += 30
            elif inString[i]["type"] == 'radiobutton':
                r_string = []
                for j in range(len(inString[i]["options"])): r_string.append(inString[i]["options"][j])
                Q_items.append(wx.RadioBox(self, -1, "", (10, posY), wx.DefaultSize, r_string))
                posY += 30
            posY += 30

        self.Q_items = Q_items
        
        okButton = wx.Button(self, wx.ID_OK, "OK")
        b_size = okButton.GetSize()
        okButton.Position = (size[0] - b_size[0] - 20, size[1] - b_size[1] - 40)

    # --------------------------------------------------

    def GetValues(self):
        values = '\n\n---< Post-Experiment Questionnaire >---\n'
        for i in range(self.inString["number_of_questions"]):
            values += self.inString[i]["question"] + "\n"
            if self.inString[i]["type"] == 'checkbox':
                for j in range(len(self.inString[i]["options"])):
                    values += self.Q_items[i][j].GetLabel() + ": " + str(self.Q_items[i][j].GetValue()) + "\n"
            elif self.inString[i]["type"] == 'radiobutton':
                values += str(self.Q_items[i].GetStringSelection()) + "\n"
            else:
                values += str(self.Q_items[i].GetValue()) + "\n"
            values += "\n"
        return values

# ===========================================================
