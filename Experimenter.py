'''
Experimenter v 1.0.0
  Runs perceptual and cognitive experiments
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

import os, sys, time, subprocess
from random import shuffle
import wx # external library; can be found in http://www.wxpython.org

### import costum modules and input files
import ExptModule
from ExptModule import Common_func as commonFunc # import common functions
from ExptModule.Dialog_classes import PopupDialog
import input.config # has 'self.settings'-dictionary; the overall setting for the experiment
import input.EventFile # has 'self.exptDetails'-dictionary; all the detailed-information for sections and trials

debugFlag = True

# --------------------------------------------------

def GNU_notice(idx=0):
    '''
      function for printing GNU copyright statements
    '''
    if idx == 0:
        print '''
Experimenter Copyright (c) 2014 Jinook Oh, W. Tecumseh Fitch for ERC Advanced Grant SOMACCA # 230604.
This program comes with ABSOLUTELY NO WARRANTY; for details run this program with the option `-w'.
This is free software, and you are welcome to redistribute it under certain conditions; run this program with the option `-c' for details.
'''
    elif idx == 1:
        print '''
THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
'''
    elif idx == 2:
        print '''
You can redistribute this program and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
'''

# ===========================================================

class ExperimenterApp(object):
    '''
      ExperimenterApp class initiates the experiment with set-up information 
      and initiating and connecting 'Experiment' and 'E_UI' classes
    '''

    def __init__(self):
        ### SETTING-UP the 2 main dictionaries
        self.settings = input.config.settings
        self.settings = commonFunc.uppercaseDict(self.settings) # make it to have upper-cases keys; so that it's case-insensitive.
        self.exptDetails = input.EventFile.exptDetails
        self.exptDetails = commonFunc.uppercaseDict(self.exptDetails) # make it to have upper-cases keys; so that it's case-insensitive.
        startNum = 0
        if self.exptDetails.has_key("-1") : startNum = -1
        for i in range(startNum, self.exptDetails["NUM_SECTIONS"]):
            self.exptDetails[str(i)] = commonFunc.uppercaseDict(self.exptDetails[str(i)]) # make it to have upper-cases keys; so that it's case-insensitive.
            for j in range(self.exptDetails[str(i)]["NUM_TRIALS"]):
                self.exptDetails[str(i)][str(j)] = commonFunc.uppercaseDict(self.exptDetails[str(i)][str(j)])
                for k in range(self.exptDetails[str(i)][str(j)]["NUM_STIMULI"]):
                    self.exptDetails[str(i)][str(j)][str(k)] = commonFunc.uppercaseDict(self.exptDetails[str(i)][str(j)][str(k)]) # make it to have upper-cases keys; so that it's case-insensitive.

        ### Other set-up
        self.input_path = self.settings["INPUT_PATH"]
        self.output_path = self.settings["OUTPUT_PATH"]
        self.file_AudFB_Pos = os.path.join("media", "AudFB_Pos.wav")
        self.file_AudFB_Neg = os.path.join("media", "AudFB_Neg.wav")
        self.file_pulse_sound = os.path.join("media", "trigger_pulse", "_pulse_signal.wav")
        self.logFilename = os.path.join(self.output_path, "Expt3Logfile.txt") # setting up logFile-name
        ### Setting-up variables for the 'display'-frame
        self.displayWidth = self.settings["DISPLAY_WIDTH"]; self.displayHeight = self.settings["DISPLAY_HEIGHT"]
        self.displayMiddle = int(self.displayWidth/2.0)
        ### Arduino set-up
        if self.settings["COMM_ARDUINO"]:
            import serial
            self.ARDUINO_USB_GLOB = "/dev/cu.usbmodem*" # this might be different depending on the Arduino type such as 'Aruduino Uno' or 'Arduino Duemilanove'.
            self.ARDUINO_PORT = "" # Name of the device for ARDUINO-chip
            # Try to connect to Arduino-chip
            for aConn in commonFunc.serial_scan(self.ARDUINO_USB_GLOB):
                self.ARDUINO_PORT = aConn.name
                self.aConn = aConn
            print str(self.ARDUINO_PORT) + " connected."

    # --------------------------------------------------

    def InitExpmt(self):
        ### Create Experiment and E_UI objects:
        self.expt = Experiment(debug=debugFlag)
        self.E_UI = E_UI(parent = None, debugFlag = debugFlag, title = "Experimenter-3")
        # Link Experiment and E_UI objects reciprocally:
        self.expt.E_UI = self.E_UI
        self.E_UI.expt = self.expt
        # Display the windows and initialize the experiment:
        self.E_UI.Show(True)
        self.expt.InitExpt()

# ===========================================================

class Experiment(object):
    '''
      Experiment class; to handle most of the experiment flow
    '''
    def __init__(self, debug = False): # initialize Experiment object
        self.exptRunning = False
        self.userTimedOut = False
        self.repeated_trial = False # indicating the current trial was repeated trial or not
        self.debug = debug        

    # --------------------------------------------------
        
    def InitExpt(self):
        if self.debug: print "Experiment.InitExpt"
        
        sInfo = self.GetSubjectInfo() # runs dialog and retrieve the subject's info
        self.subjectInfo = sInfo

        if sInfo != None:
            self.exptDateTime = time.asctime()
            
            ### Defining result-filename
            time_stamp = commonFunc.get_time_stamp()
            self.exptDataFileName = os.path.join(exptApp.output_path, time_stamp + ".csv")
            self.exptLogFileName = os.path.join(exptApp.output_path, time_stamp + ".log")
            msg = "* Time-stamp (year_month_day_hour_minute_second_microsecond) was obtained from built-in <datetime> function of Python.\n"
            msg += "Time-stamp, Log\n"
            msg += "----------------------------\n"
            commonFunc.writeFile(self.exptLogFileName, msg)
            # Just for the case the same file-name exists.
            while os.path.isfile(self.exptDataFileName): self.exptDataFileName = self.exptDataFileName.replace(".csv", "X.csv")
            
            # writing some info and header
            _txt = "Experiment started at, %s\n"%self.exptDateTime
            _txt += "Subject info: \n"
            for key in sInfo.iterkeys():
                _txt += "%s, %s\n"%(key, sInfo[key])
            _txt += "========================\n"
            commonFunc.writeFile(self.exptDataFileName, _txt)
            if exptApp.settings.has_key("RESULT_HEADER"): commonFunc.writeFile(self.exptDataFileName, exptApp.settings["RESULT_HEADER"] + "\n--------------------\n")
            else:  commonFunc.writeFile(self.exptDataFileName, "\n--------------------\n")
            
            if self.debug == True:
                print "Subject Info: ", sInfo
                print "Starting Experimenter Debugger"
            self.StartExpt()

    # --------------------------------------------------

    def GetSubjectInfo(self):
        if self.debug: print "Experiment.GetSubjectInfo"

        dlg = ExptModule.QuestionnaireDialog()
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            _sInfo = dlg.GetValues()
            dlg.Destroy()
            return _sInfo
        else:
            dlg.Destroy()
            self.E_UI.Destroy()

    # --------------------------------------------------

    def PreSection_SlideShow(self, preSectionType):
    # Process for the pre-section (Slide-Show) ; show images with the interval
        if self.debug: print "Experiment.PreSection_SlideShow"

        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.PreSection_SlideShow()\n"%commonFunc.get_time_stamp())
        
        trialInterval = exptApp.exptDetails["-1"]["TRIAL_INTERVAL"] / 1000 # trial-interval is in millisecond
        for i in range(exptApp.exptDetails["-1"]["NUM_TRIALS"]):
            self.currTrial = exptApp.exptDetails["-1"][str(i)]  # store stimuli-list to be displayed in this trial
            ### randomize the stimuli when the setting allows.
            self.stimuliIndices = range(self.currTrial["NUM_STIMULI"]) # indices of stimuli for this trial
            if exptApp.settings["RANDOMIZE_STIMULI"]: shuffle(self.stimuliIndices)
            self.E_UI.mediaPanel.showImage(self.currTrial) # show image
            wx.SafeYield()
            ### play the sound when it's applicable
            if preSectionType == "SLIDESHOW_WITH_SOUND":
                soundStim = self.currTrial[str(self.currTrial["NUM_STIMULI"]-1)] # the last one is sound-stimulus
                self.E_UI.mediaPanel.LoadSound(soundStim)
                self.E_UI.mediaPanel.PlaySound() # play it.
            time.sleep(trialInterval) # wait for the interval
        self.currTrial = ""
        self.stimuliIndices = []

    # --------------------------------------------------

    def StartExpt(self):
        if self.debug: print "Experiment.StartExpt"

        self.exptRunning = True
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.StartExpt()\n"%commonFunc.get_time_stamp())
        
        if exptApp.exptDetails.has_key("-1"): # There's some pre-section
            self.sectionCounter = -1
            preSectionType = exptApp.exptDetails["-1"]["SECTION_TYPE"].upper()
            if preSectionType == "SLIDESHOW" or preSectionType == "SLIDESHOW_WITH_SOUND": # This pre-section's type is 'SlideShow'
                self.PreSection_SlideShow(preSectionType)
                                    
        self.sectionCounter = 0
        self.sectionIndices = range(exptApp.exptDetails["NUM_SECTIONS"]) # indices of sections
        if exptApp.settings["RANDOMIZE_SECTIONS"]: shuffle(self.sectionIndices)  # randomize the sections when the setting allows.
        self.StartSection()

    # --------------------------------------------------

    def StartSection(self):
        if self.debug: print "Experiment.StartSection"
        
        self.currSectionIdx = self.sectionIndices[self.sectionCounter] # currently chosen section-index
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.StartSection(), section#%.2i\n"%(commonFunc.get_time_stamp(), self.currSectionIdx))
        self.trialCounter = 0
        self.trialIndices = range(exptApp.exptDetails[str(self.currSectionIdx)]["NUM_TRIALS"]) # indices of trials
        if exptApp.settings["RANDOMIZE_TRIALS"]: shuffle(self.trialIndices) # randomize the trials when the setting allows.
        
        ### show the section-title & section-description when it's applicable
        if exptApp.exptDetails[str(self.currSectionIdx)].has_key("SECTION_TITLE"): # if there's a section-title
            if len(exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_TITLE"].strip()) > 0 : # and it's not a blank
                msg = exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_TITLE"]
                if exptApp.exptDetails[str(self.currSectionIdx)].has_key("SECTION_DESC"): # if there's a section-description
                    if len(exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_DESC"].strip()) > 0 : # and it's not a blank
                        msg = msg + "\n" + exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_DESC"]
                dlg = PopupDialog(self.E_UI, -1, "Note", msg, None, (350, 200), cancel_btn=False)
                dlg.ShowModal()
                dlg.Destroy()

        if exptApp.exptDetails[str(self.currSectionIdx)].has_key("SECTION_TIMEOUT"):
        # if there's 'section_timeout', apply it
            self.timeoutTime = exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_TIMEOUT"]
        else:
            self.timeoutTime = None

        if exptApp.exptDetails[str(self.currSectionIdx)].has_key("SECTION_ITI"):
        # if there's 'section_iti' (InterTrialInterval; value in milliseconds from user response to next trial)
            self.ITI = exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_ITI"]
        else:
            self.ITI = None

        if exptApp.exptDetails[str(self.currSectionIdx)].has_key("SECTION_RTOI") and \
           exptApp.exptDetails[str(self.currSectionIdx)]["SECTION_RTOI"] == True:
        # if there's 'section_RTOI(REPEAT_TRIAL_ON_INCORRECT)', SECTION_RTOI gets applied rather than general 'REPEAT_TRIAL_ON_INCORRECT'.           
            self.REPEAT_TRIAL_ON_INCORRECT = True
        else:
            self.REPEAT_TRIAL_ON_INCORRECT = False

        # SECTION_FEEDBACK is used in the 'getFeedback()' in the E_UI class.
        
        self.StartTrial()

    # --------------------------------------------------

    def StartTrial(self):
        if self.debug: print "Experiment.StartTrial"

        try: self.exptApp.expt.ITI_timer.Stop()
        except: pass

        self.currTrialIdx = self.trialIndices[self.trialCounter]  # currently chosen trial-index
        self.currTrial = exptApp.exptDetails[str(self.currSectionIdx)][str(self.currTrialIdx)]  # store stimuli-list to be displayed in this trial

        ### randomize the stimuli when the setting allows.
        self.stimuliIndices = range(self.currTrial["NUM_STIMULI"]) # indices of stimuli for this trial
        if exptApp.settings["RANDOMIZE_STIMULI"] and self.repeated_trial == False: # RANDOMIZE_STIMULI is True and the current trials is NOT a repeated trial
            shuffle(self.stimuliIndices)
        self.currCorrectness = "None" # will be 'Correct' when 'correctResponse' matches with the actual response from the subject
        
        self.RT = None # Reaction time will be recorded in 'HandleGUIResponse' of the 'display'
        self.trialStartTime = None # trialStartTime init. It will be recorded after all the stimuli are presented.
        
        self.E_UI.mediaPanel.panel.Show() # show the panel for presenting stimulus
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.StartTrial(), trial#%.2i\n"%(commonFunc.get_time_stamp(), self.currTrialIdx))
        if exptApp.settings.has_key("PULSE_ON_TRIAL") and exptApp.settings["PULSE_ON_TRIAL"] == True:
            self.E_UI.play_pulse() # play a pulse-sound as a signal of the beginning of each trial
        wx.CallAfter(self.E_UI.Raise) # E_UI frame gets focus
        self.PresentStimulus()

        ### Hide cursor on the objects when the setting allows it.
        if exptApp.settings["HIDE_CURSOR"]:
            cursor = wx.StockCursor(wx.CURSOR_BLANK)
            wx.FutureCall(1, self.E_UI.set_cursor_on_objects, cursor)

    # --------------------------------------------------

    def PresentStimulus(self):
        if self.debug: print "Experiment.PresentStimulus"
        commonFunc.writeFile(self.exptLogFileName, "%s, Beginning of Experiment.PresentStimulus()\n"%commonFunc.get_time_stamp())
        ret_delay = self.E_UI.mediaPanel.presentStimulus(self.currTrial)
        '''
        if the the stimuli are sounds (or it needs some delay before accepting user-response for some reason), 
        the function should return the length of all the sounds to be played, 
        therefore trial_start_time and user_response is properly started in time.
        '''
        
        if ret_delay == None: # no delay indicated
            ### enable the user-response right away
            if self.timeoutTime != None: self.timeoutTimerSetUp() # TimeOut Setting
            self.trialStartTime = time.time() # record trial-starting-time
            self.E_UI.EnableResponseGUI()
        else:
            if exptApp.settings.has_key("ONSET_OF_RT_MEASUREMENT"):
                self.response_enabling_timer = wx.FutureCall(ret_delay + exptApp.settings["ONSET_OF_RT_MEASUREMENT"], self.OnEnableResponse)
            else:
                self.response_enabling_timer = wx.FutureCall(ret_delay, self.OnEnableResponse)
            self.E_UI.DisableResponseGUI()

        commonFunc.writeFile(self.exptLogFileName, "%s, End of Experiment.PresentStimulus()\n"%commonFunc.get_time_stamp())
        
    # --------------------------------------------------

    def ProcessGUIResponse(self, response):
        if self.debug: print "Experiment.ProcessGUIResponse"
        
        self.userTimedOut = False
        self.EndTrial(response)

    # --------------------------------------------------

    def EndTrial(self, response):
        if self.debug: print "Experiment.EndTrial"
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.EndTrial()\n"%commonFunc.get_time_stamp())
        
        if self.exptRunning == False:
            wx.MessageBox('The experiment is over!\nPlease inform your host.', 'Notice')
            return
        if self.userTimedOut == True:
            print " Time Out!"
        else:
            if self.timeoutTime != None:
                self.timeoutTimer.Stop()

        if response != 'CANCEL_RESPONSE': self.WriteResponse(response) # Store the result data
        # when the individual module has its own result data saving function, it sends the message, 'CANCEL_RESPONSE'
        
        ### Imply Post-Trial-Interval when it's applicable.
        if self.ITI == None or self.ITI == 0: # no inter-trial-interval
            self.repeat_trial_decision()
        else:
            self.ITI_timer = wx.FutureCall(self.ITI, self.repeat_trial_decision)
            '''
            ### OBSOLETE ###
            timerID_ITI = 97
            self.ITITimer = wx.Timer(self.E_UI, timerID_ITI) # parent needs to be a wx object
            self.ITITimer.Start(self.ITI, oneShot = True)
            wx.EVT_TIMER(self.E_UI, timerID_ITI, self.OnITITimer)
            '''

    # --------------------------------------------------

    def NextTrial(self):
        if self.debug: print "Experiment.NextTrial"
        
        self.trialCounter += 1
        if self.trialCounter < exptApp.exptDetails[str(self.currSectionIdx)]["NUM_TRIALS"]:
            self.StartTrial()
        else:
            self.EndSection()

    # --------------------------------------------------

    def repeat_trial_decision(self):
        if self.currCorrectness == 'Incorrect' and self.REPEAT_TRIAL_ON_INCORRECT == True:
        # got the incorrect answer and the config says the incorrect trial should be repeated,
            self.repeated_trial = True
            self.StartTrial() # go to the start-trial (repeat this trial)
        else:
            self.repeated_trial = False
            self.NextTrial()

    # --------------------------------------------------

    def Timeout(self):
        '''
          Function for processes on the time-out event.
        '''
        if self.debug: print "Experiment.Timeout"
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.Timeout()\n"%commonFunc.get_time_stamp())
        
        self.E_UI.DisableResponseGUI() # Disabling subject-input until the new-trial begins.
        self.E_UI.mediaPanel.panel.Hide() # Hide the panel containing the stimulus
        
        ### Giving a negative-feedback
        feedback = self.E_UI.getFeedback()
        if feedback != 'none' and feedback != None:
            if feedback == 'custom': # if feedback is customized
                self.E_UI.mediaPanel.presentFeedback("negative") # call the function in the mediaPanel
            else:
                result = self.E_UI.presentFeedback("negative", feedback) # call the regular function
                if result == 'delay': time.sleep(1.5)

        self.userTimedOut = True # timed out
        self.currCorrectness = 'Incorrect'
        self.RT = -1 # negative reaction-time
        self.EndTrial(response = None) # move to 'EndTrial'

    # --------------------------------------------------

    def timeoutTimerSetUp(self):
    # set-up for timeoutTimer for a trial
        if self.debug: print "Experiment.timeoutTimerSetUp"
        self.timeoutTimer = wx.FutureCall(self.timeoutTime, self.OnTimeoutTimer)

    # --------------------------------------------------

    def OnEnableResponse(self):
        if self.debug: print "Experiment.OnEnableResponse"
    
        if self.timeoutTime != None : self.timeoutTimerSetUp() # TimeOut Setting
        self.trialStartTime = time.time() # record trial-starting-time
        self.E_UI.EnableResponseGUI()

    # --------------------------------------------------

    def OnTimeoutTimer(self):
        if self.debug: print "Experiment.OnTimeoutTimer"

        self.Timeout()

    # --------------------------------------------------

    '''
    ### OBSOLETE ###
    def OnITITimer(self, event):
        if self.debug: print "Experiment.OnITITimer"
        self.repeat_trial_decision()
    '''

    # --------------------------------------------------

    def WriteResponse(self, response):
        if self.debug: print "Experiment.WriteResponse"
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.WriteResponse()\n"%commonFunc.get_time_stamp())
        
        if self.exptRunning == True:
            files = ''
            for i in range(self.currTrial["NUM_STIMULI"]): files += self.currTrial[str(i)]["FILEPATH"] + ' | '
            files = files.rstrip(' | ')
            correctResponse = "None"
            if self.currTrial.has_key("CORRECT_RESPONSE"): correctResponse = self.currTrial["CORRECT_RESPONSE"]
            responseString = ""
            if response == None: # user timed out
                if self.userTimedOut == True:
                    responseString = str(correctResponse) + ", timeout, timeout"
                else:
                    responseString = str(correctResponse) + ", None, None"
            else:
                response = str(response)
                responseString = str(correctResponse) + ", " + str(response) + ", " + self.currCorrectness                
            outString = "%i, %i, %.3f, %s, %s\n"% (self.currSectionIdx, self.currTrialIdx, self.RT, responseString, files)
            
            commonFunc.writeFile(self.exptDataFileName, outString)

    # --------------------------------------------------

    def EndSection(self):
        if self.debug: print "Experiment.EndSection"
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.EndSection()\n"%commonFunc.get_time_stamp())
        
        self.sectionCounter += 1
        if self.sectionCounter < exptApp.exptDetails["NUM_SECTIONS"]:        
            # when a Section ends, wait for the same amount of time for the 'ITI'-setting
            time.sleep(self.ITI/1000)
            self.StartSection()
        else:    
            self.EndExpt()

    # --------------------------------------------------

    def EndExpt(self):
        if self.debug: print "Experiment.EndExpt"
        commonFunc.writeFile(self.exptLogFileName, "%s, Experiment.EndExpt()\n"%commonFunc.get_time_stamp())
        
        self.exptRunning = False

        if exptApp.settings["POST_Q"]: # if there is a post-experiment Questionnaire
            post_Q_answer = self.E_UI.mediaPanel.show_post_Q()
            commonFunc.writeFile(self.exptDataFileName, post_Q_answer)

        wx.MessageBox('Experiment Finished.\nThank you for participating!', 'Acknowledgement')
        self.E_UI.OnCloseWindow(None)

# ===========================================================

class E_UI(wx.Frame):
    '''
      This class handles basic display and user interface setup (more detailed part should be handled by the individual experiment module)
    '''
    def __init__(self, parent, debugFlag, title = ""):
        self.exptApp = exptApp # connect exptApp to the E_UI class
        
        if wx.Display.GetCount() > 1 and exptApp.settings["2ND_MONITOR"]: # if there's more than one monitor, and want to use the 2nd monitor
            self.screenPos = (wx.Display(1).GetGeometry()[0], wx.Display(1).GetGeometry()[1]) # will be positioned on the 2nd monitor
            self.screenSize = (wx.Display(1).GetGeometry()[2], wx.Display(1).GetGeometry()[3]) # full-size will be the size of the 2nd monitor
        else:
            self.screenPos = (0, 0)
            self.screenSize = (wx.Display(0).GetGeometry()[2], wx.Display(0).GetGeometry()[3])
        
        ### define the style of the window
        frame_style = wx.DEFAULT_FRAME_STYLE
        if exptApp.settings["OPERATING_SYSTEM"] == 'mac':
            if exptApp.settings["WINDOW_STYLE"].upper() == 'MINIMIZE': frame_style = wx.MINIMIZE
        
        # Initialize the Frame
        wx.Frame.__init__(self, parent, -1, title, pos = self.screenPos, size = self.screenSize, style = frame_style)
       
        # When the 'fullscreen' is True, make it Full-Screen
        if exptApp.settings["FULLSCREEN"] :
            # When the secondary monitor is not used, make it to FullScreen-mode
            if not exptApp.settings["2ND_MONITOR"]: self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        else:
            self.SetSize((exptApp.displayWidth, exptApp.displayHeight))
        
        self.Center()
        
        self.debug = debugFlag
        
        self.mainPanel = wx.Panel(self, pos = self.screenPos, size = (self.GetSize()[0], self.GetSize()[1])) # main-panel set-up
        if exptApp.settings.has_key("MAINPANEL_BGCOLOR"):
            ### Change the background-color
            bgColor = exptApp.settings["MAINPANEL_BGCOLOR"].split("/")
            if len(bgColor) > 1: # this is Hexadecimal-code
                RGBcode = bgColor[1].split(",")
                for i in xrange(3):
                    RGBcode[i] = commonFunc.HexToDec(RGBcode[i]) # Converting the hexadecimal-code to the decimal number
                self.mainPanelColour = ( wx.Colour(RGBcode[0], RGBcode[1], RGBcode[2]) )
            else:
                self.mainPanelColour = bgColor[0].strip()
        else:
            self.mainPanelColour = self.GetBackgroundColour()
        self.mainPanel.SetBackgroundColour(self.mainPanelColour)

        # Monitoring.
        # Purpose : When the experiment is going on the 2nd monitor,
        # the experimenter can monitor certain things on the 1st monitor.
        if exptApp.settings["2ND_MONITOR"] and exptApp.settings.has_key("2ND_MONITOR_MONITORING"):
            if exptApp.settings["2ND_MONITOR_MONITORING"] == True: self.CreateMonitoringFrame(title)
        
        self.CreateMediaPanel() # panel for presenting stimuli. getting response depending on the experiment-type
                
        self.CreateResponder() # Connects the panel to receive the response from the subject
        
        ### Hide cursor on the panels when the setting allows it.
        if exptApp.settings.has_key("HIDE_CURSOR"):
            if exptApp.settings["HIDE_CURSOR"]:
                cursor = wx.StockCursor(wx.CURSOR_BLANK)
                self.set_cursor_on_panels(cursor)

        ### ButtonBox-setup when the setting allows it.
        if exptApp.settings.has_key("BUTTONBOX"):
            if exptApp.settings["BUTTONBOX"]: # only if the 'buttonBox' is True
                self.usbbox = ExptModule.USBBox()
                self.usbbox.commands.add_callback(ExptModule.REPORT.KEYDN , self.OnBBPress) # Binding the ButtonBox-press
                self.usbDeviceFlag = "open" # a flag to control the incoming information for the buttonbox
                self.pollButtonBox()

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        ### Connecting key-inputs with some functions      
        if exptApp.settings.has_key("KEY_BINDING"):
            accel_list = []
            for i in range(len(exptApp.settings["KEY_BINDING"])):
                _key = exptApp.settings["KEY_BINDING"][i][0].split(".")
                _bound_func = exptApp.settings["KEY_BINDING"][i][1].split(".")
                special_key = wx.ACCEL_NORMAL
                if _key[0].upper() == "CTRL": special_key = wx.ACCEL_CTRL
                elif _key[0].upper() == "ALT": special_key = wx.ACCEL_ALT
                if _key[1].upper().startswith('WXK'): key_string = eval('wx.%s'%_key[1].upper())
                else: key_string = ord(_key[1].upper())
                if _bound_func[0] == 'main': bound_function = eval('self.%s'%_bound_func[1])
                elif _bound_func[0] == 'expmt_module': bound_function = eval('self.mediaPanel.%s'%_bound_func[1])
                self.Bind(wx.EVT_MENU, bound_function, id=i)
                accel_list.append((special_key, key_string, i))
            accel_tbl = wx.AcceleratorTable(accel_list)
            self.SetAcceleratorTable(accel_tbl)

    # --------------------------------------------------

    def CreateMonitoringFrame(self, title):
        if self.debug: print "E_UI.CreateMonitoringFrame"
        size = (self.screenSize[0], self.screenSize[1])
        self.display_m = Display_monitoring(self, debugFlag, size, title + "_monitoring")
        self.display_m.Show(True)

    # --------------------------------------------------

    def CreateMediaPanel(self):
        '''
          Connects panel to present stimuli to the subject
        '''
        if self.debug: print "E_UI.CreateMediaPanel"
        
        if exptApp.settings.has_key("MEDIA_PANEL_PARAM"):
            self.mediaPanel = ExptModule.MediaPanel(self, exptApp.settings["MEDIA_PANEL_PARAM"])
        else:
            self.mediaPanel = ExptModule.MediaPanel(self)

    # --------------------------------------------------

    def CreateResponder(self):
        if self.debug: print "E_UI.CreateResponder"
        
        if exptApp.settings.has_key("RESPONSE_PANEL_PARAM"):
            self.responsePanel = ExptModule.ResponsePanel(self, exptApp.settings["RESPONSE_PANEL_PARAM"])
        else:
            self.responsePanel = ExptModule.ResponsePanel(self)
        ### Adjust the position of the responsePanel
        posX = self.GetSize()[0] * exptApp.settings["RESPONSE_PANEL_POSX"] - self.responsePanel.panel.GetSize()[0]/2
        posY = self.GetSize()[1] * exptApp.settings["RESPONSE_PANEL_POSY"] - self.responsePanel.panel.GetSize()[1]/2
        self.responsePanel.panel.SetPosition((posX, posY))

    # --------------------------------------------------

    def pollButtonBox(self):
        '''
          Function for collecting data from the ButtonBox
        '''
        self.usbbox.process_received_reports()
        wx.FutureCall(50, self.pollButtonBox)

    # --------------------------------------------------

    def OnBBPress(self, event):
        '''
          Function for ButtonBox press event
        '''
        if self.debug: print "E_UI.OnBBPress"

        value = None        
        if self.usbDeviceFlag == "open":
            if event.key_code == 3: value = "Button_Press_Left"
            elif event.key_code == 5: value = "Button_Press_Right"

            if value != None:            
                # check if 'onClick'-function exist in the 'mediaPanel'.
                # if it exists, call it.
                # else, calls the responsePanel's onClick
                if hasattr(self.mediaPanel, "OnClick"): self.mediaPanel.OnClick(value)
                else: self.responsePanel.OnClick(value)

    # --------------------------------------------------

    def HandleGUIResponse(self, value, additionalInfo = None):
        '''
          Function for getting response from the experiment module and proceed with it
        '''
        if self.debug: print "E_UI.HandleGUIResponse"
        commonFunc.writeFile(self.expt.exptLogFileName, "%s, E_UI.HandleGUIResponse()\n"%commonFunc.get_time_stamp())
        
        self.DisableResponseGUI() # Disabling subject-input until the new-trial begins.
        self.mediaPanel.panel.Hide() # Hide the panel containing the stimulus
        # If there's additionalInfo from the caller module, then put it after 'value'
        
        if value == 'CANCEL_RESPONSE':
            self.expt.ProcessGUIResponse(value) # Go to the next step right away
        else:
            if self.expt.RT == None: self.expt.RT = (time.time() - self.expt.trialStartTime) # Record the response-time
            # if 'self.expt.RT' is not None, it means RT was already recorded in the ResponsePanel for some reason.
            
            if self.expt.timeoutTime != None: self.expt.timeoutTimer.Stop()

            ### Decide 'correctness' when 'correctResponse'-key exists and it's not 'none'
            if self.expt.currTrial.has_key("CORRECT_RESPONSE") and self.expt.currTrial["CORRECT_RESPONSE"] != None and self.expt.currTrial["CORRECT_RESPONSE"].lower() <> 'none':
                correctResponse = []
                correctResponse = self.expt.currTrial["CORRECT_RESPONSE"].split("/") # there could be multiple correctResponses
                self.expt.currCorrectness = 'Incorrect'
                for i in range(len(correctResponse)):
                    # if any of correct-responses matches with the subject's response, then change the variable to the 'Correct'
                    if correctResponse[i].strip().lower() == value.lower(): self.expt.currCorrectness = 'Correct'
                    
            feedback = self.getFeedback()
            feedback_result = None
            if feedback != 'none' and feedback != None:
            # Giving a proper feedback when 'feedback'-key exists and it's not 'none'
                feedBackType = "negative"
                if self.expt.currCorrectness == 'Correct': feedBackType = "positive"
                if feedback == 'custom': # if feedback is customized
                    self.mediaPanel.presentFeedback(feedBackType) # call the function in the mediaPanel
                else:
                    feedback_result = self.presentFeedback(feedBackType, feedback) # call the regular function

            if additionalInfo != None: value = str(value) + ", " + str(additionalInfo)

            ### passes the GUI value back to the Expt object
            if feedback_result == 'delay': wx.FutureCall(1500, self.expt.ProcessGUIResponse, value)
            elif feedback_result == None: self.expt.ProcessGUIResponse(value)

    # --------------------------------------------------

    def getFeedback(self):
        feedback = None
        if exptApp.exptDetails[str(self.expt.currSectionIdx)].has_key("SECTION_FEEDBACK"):
            try: feedback = exptApp.exptDetails[str(self.expt.currSectionIdx)]["SECTION_FEEDBACK"].lower()
            except: pass
        return feedback

    # --------------------------------------------------   
 
    def presentFeedback(self, FB_Type, FB):
        '''
          Function for giving proper feedback
        '''
        if self.debug: print "E_UI.presentFeedback"

        FB_Type = FB_Type.lower()
        FB = FB.lower()
        ### set-up for negative visual feedback type
        negVisualFBType = "solid_color:red"
        if exptApp.settings.has_key("NEG_VISUAL_FB_TYPE"):
            negVisualFBType = exptApp.settings["NEG_VISUAL_FB_TYPE"].lower()
        
        if FB_Type == 'positive':
            sound = wx.Sound(os.path.join(exptApp.input_path, exptApp.file_AudFB_Pos))
            if FB == 'visual': pass
            elif FB == 'auditory': sound.Play(wx.SOUND_ASYNC)
            elif FB == 'both': sound.Play(wx.SOUND_ASYNC)
            if exptApp.settings["COMM_ARDUINO"]: # feedback through Arduino is True.
                self.commArduino() # sending signals to Arduino
        elif FB_Type == 'negative':
            sound = wx.Sound(os.path.join(exptApp.input_path, exptApp.file_AudFB_Neg))
            if FB == 'visual':
                if negVisualFBType.startswith('flicker'): self.flickerWindow(10, negVisualFBType.split(":")[1])
                elif negVisualFBType.startswith('solid_color'): self.negColorWindow(negVisualFBType.split(":")[1])
            elif FB == 'auditory': sound.Play(wx.SOUND_ASYNC)
            elif FB == 'both':
                sound.Play(wx.SOUND_ASYNC)
                if negVisualFBType.startswith('flicker'): self.flickerWindow(10, negVisualFBType.split(":")[1])
                elif negVisualFBType.startswith('solid_color'): self.negColorWindow(negVisualFBType.split(":")[1])
        if FB_Type == 'negative':
            if FB == 'both' or FB == 'visual': return 'delay' # pause for 1.5 sec. for showing negative color screen
            else: return None
        else:
            return None

    # --------------------------------------------------

    def commArduino(self):
        '''
          Function for sending signals to ARDUINO
        '''
        if self.debug: print "E_UI.commArduino"
        
        if exptApp.ARDUINO_PORT <> "": # If the ARDUINO-chip is connected
            ### Sending a signal to the Arduino-chip
            sendingData = bytearray(1)
            sendingData[0] = 1 # message will be '1'
            exptApp.aConn.write(sendingData) # send a signal to Arduino
            print exptApp.aConn.readline() # print a message from Arduino
            exptApp.aConn.flush() # flush the serial connection

    # --------------------------------------------------

    def negColorWindow(self, negColor):
        '''
          Function for showing negative-feedback screen
        '''
        if self.debug: print "E_UI.negColorWindow"
        
        negColor = negColor.split("/")
        if len(negColor) > 1: # this is Hexadecimal-code
            RGBcode = negColor[1].split(",")
            for i in xrange(3):
                RGBcode[i] = commonFunc.HexToDec(RGBcode[i]) # Converting the hexadecimal-code to the decimal number
            negColor = ( wx.Colour(RGBcode[0], RGBcode[1], RGBcode[2]) )
        else:
            negColor = negColor[0].strip()
        self.mainPanel.SetBackgroundColour(negColor)
        self.mainPanel.Refresh()
        wx.SafeYield()
        wx.FutureCall(1550, self.restore_original_bg_color)

    # --------------------------------------------------

    def restore_original_bg_color(self):
        if self.debug: print "E_UI.restore_original_bg_color"        
        self.mainPanel.SetBackgroundColour(self.mainPanelColour)
        self.mainPanel.Refresh()
        wx.SafeYield()

    # --------------------------------------------------

    def flickerWindow(self, times, negColor):
        '''
          Function for giving a flickering-effect as a negative-feedback
        '''
        if self.debug: print "E_UI.flickerWindow"
        
        negColor = negColor.split("/")
        if len(negColor) > 1: # this is Hexadecimal-code
            RGBcode = negColor[1].split(",")
            for i in xrange(3):
                RGBcode[i] = commonFunc.HexToDec(RGBcode[i]) # Converting the hexadecimal-code to the decimal number
            negColor = ( wx.Colour(RGBcode[0], RGBcode[1], RGBcode[2]) )
        else:
            negColor = negColor[0].strip()
        
        for i in range(times):
            self.mainPanel.SetBackgroundColour(negColor)
            wx.SafeYield()
            time.sleep(0.03)
            self.mainPanel.SetBackgroundColour('white')
            wx.SafeYield()
            time.sleep(0.03)
        self.mainPanel.SetBackgroundColour(self.mainPanelColour)

    # --------------------------------------------------

    def EnableResponseGUI(self):
        if self.debug: print "E_UI.EnableResponseGUI"
        
        self.responsePanel.Enable()
        if hasattr(self.mediaPanel, "Enable"): self.mediaPanel.Enable()
        if exptApp.settings["BUTTONBOX"]: # start ButtonBox again which was disabled when a response happened.
            self.usbDeviceFlag = "open"
            self.usbbox.reset_clock() # reset real time clock in button box

    # --------------------------------------------------

    def DisableResponseGUI(self):
        if self.debug: print "E_UI.DisableResponseGUI"
        
        self.responsePanel.Disable()
        if hasattr(self.mediaPanel, "Disable"): self.mediaPanel.Disable()
        if exptApp.settings["BUTTONBOX"]: self.usbDeviceFlag = "close"

    # --------------------------------------------------

    def play_pulse(self):
        '''
          play a pulse-sound as a signal
        '''
        if self.debug: print "E_UI.play_pulse"
        
        self.sound = wx.Sound(os.path.join(exptApp.input_path, exptApp.file_pulse_sound))
        self.sound.Play(wx.SOUND_ASYNC)
        commonFunc.writeFile(self.expt.exptLogFileName, "%s, A pluse sound was played\n"%commonFunc.get_time_stamp())

    # --------------------------------------------------

    def set_cursor_on_panels(self, cursor):
        self.mainPanel.SetCursor(cursor)
        self.mediaPanel.panel.SetCursor(cursor)
        self.responsePanel.panel.SetCursor(cursor)

    # --------------------------------------------------

    def set_cursor_on_objects(self, cursor):
        obj = wx.FindWindowById(0,)
        i = 0
        while obj is not None:
            obj.SetCursor(cursor)
            i += 1
            obj = wx.FindWindowById(i)

    # --------------------------------------------------

    def OnCloseWindow(self, event):
        if self.debug: print "E_UI.OnCloseWindow"
        self.Destroy()
        #sys.exit()

    # --------------------------------------------------
    
    def OnSave(self, event):
        if self.debug: print "E_UI.OnSave"
        fileName = commonFunc.save(exptApp, exptApp.output_path)
        msg = "Saving complete.\nGenerated file (in the output folder):\n%s.\n\nThe program will be closed."%(fileName)
        dlg = PopupDialog(self, -1, "Note", msg, None, (450, 250))
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()
        #sys.exit()

    # --------------------------------------------------

    def OnLoad(self, event):
        if self.debug: print "E_UI.OnLoad"

        ### Warning
        msg = "* If there's any, the data of the current session will be lost.\n\n"
        msg += "** It assumes that the subject's info, config.py\n"
        msg += " and EventFile.py are as same as when the saved file was made."
        dlg = PopupDialog(self, -1, "Note", msg, None, (450, 200))
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_CANCEL: return

        ### Loading
        f = commonFunc.chooseFile(self, "Please choose a file to load.", "sav")
        #f = raw_input("Input the file-path for loading: ").strip() # In a case that wx.FileDialog appears on the 2nd monitor which can't be checked by the user, this line can substitute the wx.FileDialog.

        if f != None:
            commonFunc.load(f, exptApp)
            try:
                self.expt.trialStartTime = None
                self.expt.timeoutTimer.Stop()
            except: pass

            ### Complete message
            msg = "Loading complete.\nThe trial(trial:%i, section:%i) will start."%(self.expt.trialCounter+1, self.expt.sectionCounter+1)
            dlg = PopupDialog(self, -1, "Note", msg, None, (350, 200))
            dlg.ShowModal()
            dlg.Destroy()

            self.DisableResponseGUI()
            if self.expt.trialCounter == 0:
                self.expt.StartSection()
            else:
                self.expt.currSectionIdx = self.expt.sectionIndices[self.expt.sectionCounter] # currently chosen section-index
                self.expt.StartTrial() # start the loaded session

# ===========================================================

class Display_monitoring(wx.Frame):
    '''
      This class is for monitor certain things on the 1st monitor
      when the experiment is going on the 2nd monitor.
    '''
    def __init__(self, parent, debugFlag, size, title=""):
        self.screenPos = (0, 0)
        self.screenSize = size
        wx.Frame.__init__(self, parent, -1, title, self.screenPos, self.screenSize, wx.DEFAULT_FRAME_STYLE)
        self.mainPanel = wx.Panel(self, pos = self.screenPos, size = self.screenSize) # panel set-up
        self.mainPanel.SetBackgroundColour(parent.mainPanelColour)

# ===========================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '-w': GNU_notice(1)
        elif sys.argv[1] == '-c': GNU_notice(2)
    else:
        GNU_notice(0)
        wxExptApp = wx.PySimpleApp()
        exptApp = ExperimenterApp()
        exptApp.InitExpmt()
        wxExptApp.MainLoop()
