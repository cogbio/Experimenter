'''
__init__.py
  This is for initiating ExptModule module for Experimenter.
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

import input.config # has 'settings'-variable
import string

settings = input.config.settings
settings = dict( map (lambda (key, value): (string.upper(key), value) , settings.items() ) ) # make it to have upper-case keys; so it's case-insensitive

### Import experiment-specific-classes
QuestionnaireDialog = __import__(name = settings["DIALOG_CLASS"][0], fromlist = settings["DIALOG_CLASS"][1])
QuestionnaireDialog = eval("QuestionnaireDialog." + settings["DIALOG_CLASS"][1])
ResponsePanel = __import__(name = settings["RESPONSE_PANEL_CLASS"][0], fromlist = [settings["RESPONSE_PANEL_CLASS"][1]])
ResponsePanel = eval("ResponsePanel." + settings["RESPONSE_PANEL_CLASS"][1])
MediaPanel = __import__(name = settings["MEDIA_PANEL_CLASS"][0], fromlist = [settings["MEDIA_PANEL_CLASS"][1]])
MediaPanel = eval("MediaPanel." + settings["MEDIA_PANEL_CLASS"][1])

# import Button-Box control only when the setting allows
if settings["BUTTONBOX"]: from ButtonBox_ioLabs import USBBox, REPORT
