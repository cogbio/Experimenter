# coding: UTF-8

'''
EventFile.py
  This file has information of detailed setup parameters for each sec-
  tion and its trials in Experimenter.
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

from os import path
from random import shuffle
from glob import glob

import input.config # has 'settings'-variable
import string
settings = input.config.settings
settings = dict( map (lambda (key, value): (string.upper(key), value) , settings.items() ) ) # make it to have upper-case keys; so it's case-insensitive
input_path = settings["INPUT_PATH"]

flag_debug = True # True: Generating a debugging text file which shows the some of the contents of the exptDetails dictionary.

num_of_sections = 2
section_title = ['Section-1', 'Section-2']
section_desc = ['Watch 3 images images to appear in a row. Select one when 2 other images appeared at bottom.', 
                'Watch 3 images images to appear in a row. Select one when 2 other images appeared at bottom.']
section_timeout = [10000, 10000] # 10 seconds timeout time
section_iti = [1000, 1000] # ITI : Inter Trial Interval
section_rtoi = [False, False] # RTOI : Repeat Trial On Incorrect-response
section_feedback = ["AUDITORY", "BOTH"]
num_of_trials = [1, 2] # the first section has 1 trial, the second section has 2 trails
num_of_stimuli = [6, 6]
media_dir = 'media_sample_expmt'
# All the visual stimuli in this sample experiment folder 
# are created by M.J. Martins for his experiment.
# Published in August 2014, NeuroImage Vol 96. p.300-308.
# Title: "Fractal image perception provides novel insights into hierarchical cognition", 
# Authors: M.J. Martins, F.P. Fischmeisterc, E. Puig-Waldmüller, J. Oh, A. Geißler, S. Robinson, W.T. Fitch, R. Beisteiner
# DOI: 10.1016/j.neuroimage.2014.03.064

### Make the exptDetails dictionary with above information
exptDetails = {}
exptDetails["NUM_SECTIONS"] = num_of_sections
for i in range(num_of_sections):
    exptDetails[str(i)] = {}
    exptDetails[str(i)]["NUM_TRIALS"] = num_of_trials[i]
    exptDetails[str(i)]["SECTION_TITLE"] = section_title[i]
    exptDetails[str(i)]["SECTION_DESC"] = section_desc[i]
    exptDetails[str(i)]["SECTION_ITI"] = section_iti[i]
    exptDetails[str(i)]["SECTION_RTOI"] = section_rtoi[i]
    exptDetails[str(i)]["SECTION_FEEDBACK"] = section_feedback[i]
    exptDetails[str(i)]["SECTION_TIMEOUT"] = section_timeout[i]
    for j in range(num_of_trials[i]):
        exptDetails[str(i)][str(j)] = {}
        exptDetails[str(i)][str(j)]["NUM_STIMULI"] = num_of_stimuli[i]
        trial_folder = 's%.2i_%.3i'%(i, j)
        for k, fp in enumerate( glob(path.join(input_path, media_dir, trial_folder, '*.*')) ):
            filename = path.split(fp)[1]
            exptDetails[str(i)][str(j)][str(k)] = {}
            exptDetails[str(i)][str(j)][str(k)]["FILEPATH"] = path.join(input_path, media_dir, trial_folder, filename)
            if '.png' in filename:
                if k == 1:
                    exptDetails[str(i)][str(j)][str(k)]["POSX"] = 0.25
                    exptDetails[str(i)][str(j)][str(k)]["POSY"] = 0.3
                elif k == 2:
                    exptDetails[str(i)][str(j)][str(k)]["POSX"] = 0.5
                    exptDetails[str(i)][str(j)][str(k)]["POSY"] = 0.3
                elif k == 3:
                    exptDetails[str(i)][str(j)][str(k)]["POSX"] = 0.75
                    exptDetails[str(i)][str(j)][str(k)]["POSY"] = 0.3
                elif k == 4:
                    exptDetails[str(i)][str(j)][str(k)]["POSX"] = 0.33
                    exptDetails[str(i)][str(j)][str(k)]["POSY"] = 0.7
                elif k == 5:
                    exptDetails[str(i)][str(j)][str(k)]["POSX"] = 0.66
                    exptDetails[str(i)][str(j)][str(k)]["POSY"] = 0.7
            if '_corr' in filename:
                exptDetails[str(i)][str(j)]["CORRECT_RESPONSE"] = filename
                # CORRECT_RESPONSE can be many. If there should be possible multiple correct responses, those responses should be concatenated with slash '/'.

if flag_debug:
    f = open("_debug_EventFile.txt", "w")
    f.write("<< exptDetails Dict >> --------------------------\n")
    f.write("----------------------\n\n")
    for i in range(num_of_sections):
        for j in range(num_of_trials[i]):
            f.write("* Session #%i, Trial #%i\n"%(i, j))
            f.write("Correct-response : %s\n"%exptDetails[str(i)][str(j)]["CORRECT_RESPONSE"])
            f.write("\n- Stimuli files ::\n")
            for k in range(num_of_stimuli[i]):
                f.write("%s\n"%exptDetails[str(i)][str(j)][str(k)]["FILEPATH"])
            f.write("\n-------------------\n\n")
        f.write("< End of a section > -------------\n----------------------------------\n\n")
    f.write("<< EOD >> ---------------------------------------")
