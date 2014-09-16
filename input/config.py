'''
config.py
  This file has information of general setup parameters for initiating
  an experiment in Experimenter.
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

settings = {
    "dialog_Class": ['ExptModule.Dialog_classes', 'NameAgeDialog'],
    "response_Panel_Class" : ['ExptModule.BlankPanel', 'BlankPanel'],
    "media_Panel_Class" : ['ExptModule._sample_expmt._sample_expmt', 'SampleExpmtPanel'],
    "operating_system": "mac",
    "INPUT_PATH": "input/",
    "OUTPUT_PATH": "output/",
    "mainPanel_bgColor" : "hex/FF,FF,FF",
    "hide_cursor" : False,
    "window_style" : "minimize",
    "comm_Arduino" : False,
    "pulse_on_trial" : False,
    "onset_of_RT_measurement" : 0,
    "fullscreen" : True,
    "2nd_monitor" : False,
    "2nd_monitor_monitoring" : False, 
    "display_Width" : 800,
    "display_Height" : 600,
    "response_Panel_PosX" : 0.5,
    "response_Panel_PosY" : 0.85,
    "buttonBox" : False,
    "neg_Visual_FB_Type" : "solid_color:red",
    "post_Q" : False,
    "key_binding" : [ ["Ctrl.Q", "main.OnCloseWindow"], 
                      ["Ctrl.S", "main.OnSave"],
                      ["Ctrl.L", "main.OnLoad"],
                      ["None.T", "expmt_module.OnTest"] ],
    "randomize_Sections" : False,
    "randomize_Trials" : True,
    "randomize_Stimuli" : False,
    "result_Header" : "Section, Trial, Reaction-Time, correctResponse, Response, Correctness, File-Names presented"

    }
