from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import wx
from wx import glcanvas

import math
from PrimaryFlightDisplay import drawRotatedLine
import glFreeType

# Some Macro definitions
METER_PER_SECOND = True
KM_PER_HOUR = False

#def drawFilledCircle(cx, cy, r, segment):
#    step = int(360.0/segment)
#    glBegin(GL_TRIANGLE_FAN)
#    glVertex2f(cx, cy)
#    for angle in xrange(0, 360, step):
#        glVertex2f(cx + math.sin(angle)*r, cy + math.cos(angle)*r)
#    glEnd()

# Visualization of the Navigation Display part
class NavigationDisplay(wx.Panel):
    def __init__(self, parent, size, style, dataInput):
        wx.Panel.__init__(self, parent, size=size, style=style)
        
        # the width and height of the draw-able area
        self.width, self.height = self.GetClientSizeTuple()
        self.hwidth, self.hheight = self.width/2, self.height/2

        # A class that handles data inputs
        self.dataInput = dataInput
        self.hasInit = False
    
        attribList = (glcanvas.WX_GL_RGBA, # RGBA
              glcanvas.WX_GL_DOUBLEBUFFER, # Double Buffered
              glcanvas.WX_GL_DEPTH_SIZE, 24) # 24 bit

        # Create GL Canvas
        self.canvas = glcanvas.GLCanvas(self, attribList=attribList,
                                        size=size)
        self.context = glcanvas.GLContext(self.canvas)

        # Bind events handlers
        self.canvas.Bind(wx.EVT_ERASE_BACKGROUND, self.processEraseBackgroundEvent)
        self.canvas.Bind(wx.EVT_PAINT, self.processPaintEvent)

        # distance (in pixels) between the white rings
        self.ringMarginPix = 110

        # offset of the concentric center of the circles
        self.shiftDown = 100

        ################ Customizable Settings ###############

        # list of scale in meters/ringMargin
        self.scales = [30.0, 50.0, 100.0, 200.0, 500.0] # in meters
        
        self.scaleSelect = 1 # by default select the 50 meters scale
        self.pixelsPerMeter = self.ringMarginPix / self.scales[self.scaleSelect]
        self.maxDistance = self.scales[self.scaleSelect] * 3
        
        self.groundspeedUnit = METER_PER_SECOND

    def setScale(self, scale):
        self.scaleSelect = scale
        self.pixelsPerMeter = self.ringMarginPix / self.scales[self.scaleSelect]
        self.maxDistance = self.scales[self.scaleSelect] * 3

    # Do nothing, just to prevent flicker
    def processEraseBackgroundEvent(self, event):
        pass
    
    # Need to be called regularly (by calling Refresh() in main timer)
    def processPaintEvent(self, event):
        self.canvas.SetCurrent(self.context)
        
        # This is the perfect time to initialize OpenGL
        if not self.hasInit:
            self.OnInitGL()
            self.hasInit = True
        
        # TODO: Redraw on demand
        self.OnPaint()
        
        self.canvas.SwapBuffers()
        event.Skip()
    
    def OnInitGL(self):
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Middle of the canvas is the origin
        glOrtho(-self.hwidth,self.hwidth,self.hheight,-self.hheight,0,1)
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(2)

        # enable the alpha channel
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # enable line smoothing
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
        
        # quadric for drawing circles
        self.quadric = gluNewQuadric()

        ### NOTE: the coordinate origin of the glPrint function is
        ### at the bottom-left corner. Be aware of it !!!
        self.myFont = glFreeType.font_data(self.dataInput.cwd+"\Font.ttf", 30)
        self.myCompassFont = glFreeType.font_data(self.dataInput.cwd+"\Font.ttf", 25)
        self.smallFont = glFreeType.font_data(self.dataInput.cwd+"\Font.ttf", 16)

    ### Actually draw things here!! ###
    def OnPaint(self):
        # reset
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # draw the BlackBackground
        glBegin(GL_QUADS)
        glColor(0, 0, 0)
        glVertex2f(-self.hwidth, -self.hheight)
        glVertex2f(self.hwidth, -self.hheight)
        glVertex2f(self.hwidth, self.hheight)
        glVertex2f(-self.hwidth, self.hheight)
        glEnd()

        # draw the Course-Over-Ground box and digits
        glTranslatef(0, -self.hheight, 0)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        glColor(1, 1, 1)
        glVertex2f(-30, 0)
        glVertex2f(-30, 30)
        glVertex2f(30, 30)
        glVertex2f(30, 0)
        glEnd()

        # draw the Ground Speed (GS) text and COG text
        glLoadIdentity()
        glColor(1, 1, 1)
        glTranslatef(10, self.height-25, 0)
        self.myCompassFont.glPrint(0,0,"GS")
        glTranslatef(35, 0, 0)
        glColor(104/255.0, 202/255.0, 93/255.0)
        if self.groundspeedUnit == METER_PER_SECOND:
            self.myFont.glPrint(0,0,"%2.1f"%(self.dataInput.data["groundspeed"]/10.0))
        elif self.groundspeedUnit == KM_PER_HOUR:
            mpers = self.dataInput.data["groundspeed"]/10.0
            kmh = 3.6 * mpers
            self.myFont.glPrint(0,0,"%d"%kmh)
        glTranslatef(332, 5, 0) # bad style. Magic number
        glColor(1, 1, 1)
        self.myCompassFont.glPrint(0, 0, "%03d"%self.dataInput.data["course"])


        # move a little bit down
        glLoadIdentity()
        shiftDown = self.shiftDown
        glTranslate(0, shiftDown, 0)

        radius = self.ringMarginPix * 3 # radius of the outmost ring
        glColor(104/255.0, 202/255.0, 93/255.0)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f(0, 0)
        glVertex2f(0, -radius)
        glEnd()
        #glColor(250/255.0, 246/255.0, 90/255.0) # yellow for the tip marker
        glBegin(GL_TRIANGLES)
        glVertex2f(0, -radius)
        glVertex2f(-10, -radius + 15)
        glVertex2f(10, -radius + 15)
        glEnd()

        # setup Stencil Buffer to limit drawing area to be inside the outer
        # circle.
        glEnable(GL_STENCIL_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glStencilFunc(GL_NEVER, 1, 0xFF)
        glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)
        glStencilMask(0xFF)
        glClear(GL_STENCIL_BUFFER_BIT)
        gluPartialDisk(self.quadric, 0, radius-2, 45, 1, 0, 360) # stencil pattern
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glStencilMask(0x00)
        # draw things where stencil's value is 0
        glStencilFunc(GL_EQUAL, 0, 0xFF)

        # draw the out most ring
        glColor(1, 1, 1)
        gluPartialDisk(self.quadric, radius, radius+1, 45, 1, 30, 300)

        # draw the markings on the outer ring
        glRotatef(-self.dataInput.data["course"], 0, 0, 1)
        for deg in xrange(0, 360, 10):
            drawRotatedLine(180+deg, radius+14, radius)
            
        for deg in xrange(0, 360, 10):
            drawRotatedLine(185+deg, radius+7, radius)

        # prepare to draw compass digits
        glLoadIdentity()
        glTranslatef(self.hwidth, self.hheight-shiftDown, 0)
        for deg in xrange(0, 360, 30):
            glPushMatrix()
            glRotatef(self.dataInput.data["course"]-deg, 0, 0, 1)
            if (deg < 100): shiftLeft = -8
            else: shiftLeft = -10
            glTranslatef(shiftLeft, radius+20, 0)
            glColor(250/255.0, 246/255.0, 90/255.0) # yellow for letters
            if (deg == 0):
                word = "N"
                font = self.myFont
            elif (deg == 90):
                word = "E"
                font = self.myFont
            elif (deg == 180):
                word = "S"
                font = self.myFont
            elif (deg == 270):
                word = "W"
                font = self.myFont
            else:
                glColor(1, 1, 1)
                word = "%d"%(deg/10)
                font = self.myCompassFont
            font.glPrint(0,0,word)
            glPopMatrix()

        ################## STENCIL BUFFER ENABLED BELOW ######################

        # enable stencil buffer
        # draw things where stencil's value is 1
        glStencilFunc(GL_EQUAL, 1, 0xFF) 

        # draw the internal rings  
        glLoadIdentity()
        glTranslate(0, shiftDown, 0)    
        radius0 = self.ringMarginPix
        gluPartialDisk(self.quadric, radius0, radius0+1, 35, 1, 0, 360)
        radius1 = self.ringMarginPix * 2
        gluPartialDisk(self.quadric, radius1, radius1+1, 40, 1, 0, 360)

        # draw beacons
        self.drawBeaconList()

        # draw the scale text on the rings
        glLoadIdentity()
        glColor(0, 0, 0)
        glTranslatef(-radius0, shiftDown, 0)
        glBegin(GL_QUADS)
        glVertex2f(-2, -15)
        glVertex2f(2, -15)
        glVertex2f(2, 15)
        glVertex2f(-2, 15)
        glEnd()
        glTranslatef(-radius0, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(-2, -15)
        glVertex2f(2, -15)
        glVertex2f(2, 15)
        glVertex2f(-2, 15)
        glEnd()
        glLoadIdentity()
        glColor(68/255.0, 176/255.0, 248/255.0)
        glTranslatef(self.hwidth-15, self.hheight-shiftDown-7, 0)
        glTranslatef(-radius0, 0, 0)
        self.myCompassFont.glPrint(0, 0, 
            "%d"%(self.scales[self.scaleSelect]))
        glTranslatef(-radius0, 0, 0)
        self.myCompassFont.glPrint(0, 0, 
            "%d"%(2*self.scales[self.scaleSelect]))

        # draw the yellow aircraft shape
        glColor(250/255.0, 246/255.0, 90/255.0)
        glLineWidth(3)
        glLoadIdentity()
        glTranslatef(0, shiftDown, 0)
        glBegin(GL_LINES)
        glVertex2f(0, 15)
        glVertex2f(0, -15)
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(-15, -3)
        glVertex2f(15, -3)
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(-7, 12)
        glVertex2f(7, 12)
        glEnd()

        glDisable(GL_STENCIL_TEST)

    # x,y is relative to the shifted origin (the yellow aircraft)
    # pos-x is right and pos-y is down
    def drawBeacon(self, x, y, text, outOfBound=False):
        glLoadIdentity()
        glTranslatef(0, self.shiftDown, 0)

        s = 5
        if outOfBound:
            glColor(1, 1, 0)
        else:
            glColor(0, 1, 1)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x-s, y-s)
        glVertex2f(x+s, y-s)
        glVertex2f(x+s, y+s)
        glVertex2f(x-s, y+s)
        glEnd()

        # the font thing use different coordinate system
        glLoadIdentity()
        glTranslatef(self.hwidth-5*len(text), self.hheight-self.shiftDown-18, 0)
        glTranslatef(x, -y, 0)
        self.smallFont.glPrint(0, 0, text)

    # draw all the beacons in the beacon list
    # if a beacon is out of range (i.e. cannot be displayed in the NavD), it will
    # still be displayed at the edge of the map, but the color will change to yellow.
    def drawBeaconList(self):
        if self.dataInput.beacons != []:
            for b in self.dataInput.beacons:
                # direction is in degrees. 0 points forward and CW is positive
                # distance is in meters
                name, direction, distance = b
                direction = math.radians(direction) # change to radians first
                outOfBound = False # check if the beacon is out of bound
                if distance > self.maxDistance: 
                    distance = self.maxDistance
                    outOfBound = True
                x = math.sin(direction) * distance * self.pixelsPerMeter
                y = -math.cos(direction) * distance * self.pixelsPerMeter
                self.drawBeacon(x, y, name, outOfBound)
