Experimenter
============
For running perceptual and cognitive experiments.

Developing 'Experimenter' was supported by ERC Advanced Grant SOMACCA # 230604. 

<img src="http://www.somacca.net/somacca/img/jaune.jpg" width=70, height=50> <img src="http://www.somacca.net/somacca/img/FP7-gen-RGB.jpg" width=70, height=50> [http://www.somacca.net](http://www.somacca.net)

-----------------------------------

If you download this repository and run 'Experimenter.py' with Python (tested with Python 2.6 and 2.7 from python.org), it should run a sample pseudo experiment, '_sample_expmt'. This experiment has 2 sections and 3 trials (1 trial for the 1st section, 2 trials for the 2nd section). Each trial has 6 stimuli (1 WAV file + 5 PNG files). It's a pseudo experiment just for showing how to set up 'config.py', 'EventFile.py', and code an experiment module to present stimuli and take responses from a participant.

-----------------------------------

For some structual understanding, please see README.png then, read the below.

1. Setting up 'config.py'

  "dialogClass": ['ExptModule.Dialog_classes', 'NameAgeDialog'], --> this will be used for the questionnaire-dialog at the beginning of the experiment. 'ExptModule(Folder-name).Dialog_classes(Python-file-name)', 'NameAgeDialog(Class-name of Dialog_classes)'

  "responsePanelClass" : ['ExptModule.R_ButtonPanelClass', 'Gesche_TwoButtonPanel'], --> this will be used for the response-panel. 'ExptModule(Folder-name).R_ButtonPanelClass(Python-file-name)', 'Gesche_TwoButtonPanel(Class-name)'

  "mediaPanelClass" : ['ExptModule.M_DisplayImageClass', 'DisplayImagePanel'], --> this will be used for the media-panel. 'ExptModule(Folder-name).M_DisplayImageClass(Python-file-name)', 'DisplayImagePanel(Class-name)'

  "operating_system": "mac", --> either mac, windows, or linux  

  "INPUT_PATH": "input/", --> input-folder path

  "OUTPUT_PATH": "output/", --> output-folder path

  "mainPanel_bgColor" : "hex/FF,FF,FF", --> Determine the background color in hexadecimal code.

  "hide_cursor" : True, --> Determine whether it'll hide the cursor on the screen or not.

  "window_style" : "normal", --> Determine the main window's style. 'normal' or 'minimize'. 'minimize' on MAC(OSX) will only show the contents of the window itself. It will not even show the title-bar. This 'minimize' effect can be done by setting 'fullscreen':True.

  "comm_Arduino" : False, --> When it's true, a feedback will be give through Arduino-chip such as one in the Feeder. Currently, the message going to the Arduino chip is simply '1' to activate a motor. It was implemented for giving a food reward to an animal by activating a motor of a feeder.

  "onset_of_RT_measurement" : 0, --> This item means that The activation of response panel and trial-start-time starts at the time which the value of the calculation, (length of the auditory stimulus + onset_of_RT_measurement)

  "fullscreen":False, --> decides full-screen-mode.

  "2nd_monitor" : True, --> using the secondary monitor or not

  "2nd_monitor_monitoring" : True, --> Init 'Display_monitoring' class to monitor certain things on the 1st monitor. if '2nd_monitor' is False, this option doesn't get applied.

  "displayWidth" : 1100, --> when the full-screen-mode is False, this will decide the width of the window.

  "displayHeight" : 700, --> when the full-screen-mode is False, this will decide the height of the window.

  "responsePanelPosX" : 0.5, --> the X-value of the responsePanel. 1 means the end of the window.

  "responsePanelPosY" : 0.85, --> the Y-value of the responsePanel. 1 means the end of the window.

  "buttonBox" : True, --> decide the usage of the ButtonBox. (ButtonBox module is not included in the distribution.)

  "neg_Visual_FB_Type" : "solid_color:hex/FF,00,00", --> if this starts "flicker", visual-negative-feedback will be flickering-window between the defined color and the white. if it starts with "solid_color", simplay show solid color for a second. In both cases, color followed after ':'-symbol will be the color of change. It could be either name of the color such as 'red' or 'blue', or hexadecimal code such as 'hex/FF,00,00'

  "post_Q" : False, --> If this is True, Experimenter will call 'show_post_Q' function of 'mediaPanel' to show questionnaire after the whole experiment session

  "key_binding" : [ ["None.1", "expmt_module.OnTest1"], ["None.2", "expmt_module.OnTest2"] ], --> List of key bindings. ex) ["None.1", "expmt_module.OnTest1"] : When '1' key is pressed, call the experiment module's 'OnTest1' function. ["Ctrl.S", "main.OnSave"] : When 'Ctrl+S' key is pressed, call 'E_UI' class's 'OnSave' Function.

  "randomizeSections" : False,

  "randomizeTrials" : True,

  "randomizeStimuli" : True,

  "resultHeader" : "Section, Trial, Reaction-Time, correctResponse, Response, Correctness, File-Names presented" --> This will be the header of the data-file (csv-format). If you want to add more values in 'Response' from the subject, for example - 'Choice, SelectedPosition, SelectedColor'. Specify resultHeader as "resultHeader" : "Section, Trial, Reaction-Time, correctResponse, Choice, SelectedPosition, SelectedColor, Correctness, File-Names presented". Then, you have to modify the class in your 'mediaPanel' (or 'responsePanel') to make it to send 'response' value as csv-format containing all those 3 fields. self.parent.HandleGUIResponse( str(Choice) + ", " + str(SelectedPosition) + ", " + str(Sele tedColor) )



2. Setting up 'EventFile.py'

  'EventFile.py' file has a set of variables to form a python dictionary, which contains information of all the sections, trials, and stimuli.

  Please modify included 'EventFile.py', which works with included '_sample_expmt' to make it to work with your own experiment design.



3. Stimuli files

  Put stimuli files into a folder in 'input' folder. These files' names should match with the code in 'EventFile.py', collecting these file paths.



4. Individual experiment module

  Modify included file, 'ExptModule/_sample_expmt/_sample_expmt.py'.

  Short descriptions of modules, which can be used in an experiment module, are as following.

  'Common_func.py'
    - (Function) get_time_stamp : returns a timestamp string, formatted as 'yyyy_MM_dd_hh_mm_ss_SSSSSS'
    - (Function) writeFile : writing text in a given file path
    - (Function) uppsercaseTuples & uppercaseDict : passed dictionary will be returned with upper-case key
    - (Function) HexToDec : convert hexadecimal code to decimanl number
    - (Function) try_open & serial_scan : for a connection with Arduino-chip
    - (Function) chooseFile : choosing a file using wx.FileDialog
    - (Function) generateHash : generates a unique ID
    - (Function) destroy_objects : destorys all the objects with consecutive IDs
    - (Function) GridCoordToIndex & GridIndexToCoord : conversion between index number and western reading standard coordinates
    - (Function) dgreesToRadians & radiansToDegrees : conversion between degrees and radians
    - (Function) change_bg_color : changing the background colour of a givien panel (wx.Panel)
    - (Function) monitoring_func : for monitoring the main monitor in the secondary monitor, when the experimenter has to monitor the participant's clicks while the primary monitor is not visible to the experimenter
    - (Function) save : save the important variables such as section index, trial index, whole exptDetails dictionary.
    - (Function) load : load the saved file

  'Dialog_classes.py'
    - (Class) PopupDialog : shows a short message
    - (Class) NameAgeDialog : for asking name and age before starting an experiment session
    - (Class) Post_Q_Dialog : for asking a set of questions after an experiment session

  'MAS.py'
    - (Function) load_sound : returns the length of the sound and the loaded wx.Sound object
    - (Class) Output_AudioData : class for selecting and opening streams using device name, loading sound files, and playing with Thread. pyAudio is used.
    - (Class) Input_AudioData : class for listening from a microphone and recording it to WAV file. pyAudio is used.

  'MOPSI.py'
    - (Class) MOP_NodeBox_Functions : class for drawing using wx.ClientDC. functions in this class are similar to the NodeBox functions

  'MVS.py'
    - (Function) load_img : returns loaded image (wx.StaticBitmap)
    - (Function) load_movie : returns loaded movie (wx.media.MediaCtrl)
    - (Function) load_crosshair : returns a loaded crosshair image at the center of the screen
    - (Function) img2buffer : returns width, height, and RGB(A) data of input image (wx.Image)

  'Validator_classes.py'
    - (Class) TextValidator : made to connect with wx.TextCtrl for accepting only letters
    - (Class) NumberValidator : made to connect with wx.TextCtrl for accepting only natural numbers
    - (Class) CharValidator : made to connect with wx.TextCtrl for validating every character input with a flag ('no-letter' or 'no-digit')

  'WXCOG.py'
    - (Function) generate_button : returns a wx.Button
    - (Function) generate_button_likert_scale : returns a list of wx.Buttons to form a Likert-scale
    - (Class) TimeoutBar : generates a timeout bar using wx.Gauge
    - (Class) Slider_class : generates a slider as a user-input

-----------------------------------



