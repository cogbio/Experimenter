'''
MOPSI.py
  MOPSI; Methods Of Production Software Interface
  This is a module for Experimenter to accept instant drawing in a 
  trial.
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

# ===========================================================

class MOP_NodeBox_Functions(object):
    '''
      this Class has functions acting similar with functions of the NodeBox
    '''
    def __init__(self, win = None):
        self.win = win
        self.canvas = wx.ClientDC(self.win)
        self.pen_width = 1
        self.pen_color = wx.Colour(0, 0, 0)
        self.brush_color = wx.Colour(0, 0, 0)
        self.path = []
        self.curr_pt = []
        self.offset = [0, 0]

    # --------------------------------------------------

    def translate(self, x, y):
        self.offset = [x, y]

    # --------------------------------------------------

    def stroke(self, r = None, g = None, b = None):
        if r != None and g == None and b == None: g = b = r
        # when there's only one color, it means greyscale color so that RGB gets the same intensity.
        self.pen_color = wx.Colour(r * 255, g * 255, b * 255)
        self.canvas.SetPen(wx.Pen(self.pen_color, self.pen_width))

    # --------------------------------------------------

    def strokewidth(self, w):
        self.pen_width = w
        self.canvas.SetPen(wx.Pen(self.pen_color, self.pen_width))
    
    # --------------------------------------------------

    def fill(self, r = None, g = None, b = None):
        if r != None and g == None and b == None: g = b = r
        # when there's only one color, it means greyscale color so that RGB gets the same intensity.
        self.brush_color = wx.Colour(r * 255, g * 255, b * 255)
        self.canvas.SetBrush(wx.Brush(self.brush_color))

    # --------------------------------------------------

    def rect(self, x, y, w, h):
        x += self.offset[0]
        y += self.offset[1]
        self.canvas.DrawRectangle(x, y, w, h)
        #self.canvas.EndDrawing()

    # --------------------------------------------------

    def beginpath(self, x, y, polygon = False):
        x += self.offset[0]
        y += self.offset[1]
        if polygon: self.path.append((x,y))
        else: self.curr_pt = [x, y]     

    # --------------------------------------------------

    def moveto(self, x, y):
        x += self.offset[0]
        y += self.offset[1]
        self.curr_pt = [x, y]

    # --------------------------------------------------

    def lineto(self, x, y, polygon = False):
        x += self.offset[0]
        y += self.offset[1]
        if polygon: self.path.append((x,y))
        else:
            self.path.append((self.curr_pt[0], self.curr_pt[1], x, y))
            self.curr_pt = [x, y]

    # --------------------------------------------------

    def curveto(self, h1x, h1y, h2x, h2y, x, y):
        x += self.offset[0]
        y += self.offset[1]
        self.path.append(("curve", self.curr_pt[0], self.curr_pt[1], h1x, h1y, h2x, h2y, x, y))
        self.curr_pt = [x, y]
        if self.path != 'including_curve': self.path.insert(0, 'including_curve')

    # --------------------------------------------------

    def drawpath(self, path_list = [], polygon = False):
        if polygon: self.canvas.DrawPolygon(path_list)
        else:
            if path_list[0] == 'including_curve':
                for i in range(1, len(path_list)):
                    if path_list[i][0] == 'curve': self.drawcurve(path_list[i][1], path_list[i][2], path_list[i][3], path_list[i][4], path_list[i][5], path_list[i][6], path_list[i][7], path_list[i][8])
                    else: self.canvas.DrawLine(path_list[i][0], path_list[i][1], path_list[i][2], path_list[i][3])
            else: self.canvas.DrawLineList(path_list)

    # --------------------------------------------------

    def endpath(self, draw = True, polygon = False):
        if draw:
            if polygon: self.drawpath(self.path, polygon)
            else: self.drawpath(self.path)
            self.path = []          
        else:
            path = list(self.path)
            self.path = []
            return path

    # --------------------------------------------------

    def oval(self, x, y, w, h):
        x += self.offset[0]
        y += self.offset[1]
        self.canvas.DrawEllipse(x, y, w, h)

    # --------------------------------------------------

    def drawcurve(self, origX, origY, h1x, h1y, h2x, h2y, destX, destY):
        '''
          Draw a Bezier curve.
          Used for drawing a line whose coordinates are defined with the 'curveto' function.
        '''
        ### applying offset
        origX += self.offset[0]
        origY += self.offset[1]
        h1x += self.offset[0]
        h1y += self.offset[1]
        h2x += self.offset[0]
        h2y += self.offset[1]
        destX += self.offset[0]
        destY += self.offset[1]

        p0p1X_step = (h1x - origX) / 100.0
        p0p1Y_step = (h1y - origY) / 100.0
        p1p2X_step = (h2x - h1x) / 100.0
        p1p2Y_step = (h2y - h1x) / 100.0
        p2p3X_step = (destX - h2x) / 100.0
        p2p3Y_step = (destY - h2y) / 100.0
        for i in range(100):
            p0p1X = origX + p0p1X_step * i # q0 x
            p0p1Y = origY + p0p1Y_step * i # q0 y
            p1p2X = h1x + p1p2X_step * i # q1 x
            p1p2Y = h1y + p1p2Y_step * i # q1 y
            p2p3X = h2x + p2p3X_step * i # q2 x
            p2p3Y = h2y + p2p3Y_step * i # q2 y
            q0q1X_step = (p1p2X - p0p1X) / 100.0
            q0q1Y_step = (p1p2Y - p0p1Y) / 100.0
            q1q2X_step = (p2p3X - p1p2X) / 100.0
            q1q2Y_step = (p2p3Y - p1p2Y) / 100.0
            q0q1X = p0p1X + q0q1X_step * i # r0 x
            q0q1Y = p0p1Y + q0q1Y_step * i # r0 y
            q1q2X = p1p2X + q1q2X_step * i # r1 x
            q1q2Y = p1p2Y + q1q2Y_step * i # r1 y
            r0r1X_step = (q1q2X - q0q1X) / 100.0
            r0r1Y_step = (q1q2Y - q0q1Y) / 100.0
            r0r1X = int(q0q1X + r0r1X_step * i)
            r0r1Y = int(q0q1Y + r0r1Y_step * i)
            if i > 0: self.canvas.DrawLine(prevX, prevY, r0r1X, r0r1Y)
            prevX = int(r0r1X)
            prevY = int(r0r1Y)





        
