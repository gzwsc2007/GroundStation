from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import wx, time
from wx import glcanvas

import glFreeType
import math

# draw a rotated line. (Mainly used to draw markings on the roll ring)
        # rotateDeg - degree
        # lineStart - pixel
        # lineEnd - pixel
def drawRotatedLine(rotateDeg, lineStart, lineEnd):
    glPushMatrix()
    
    glRotatef(rotateDeg,0,0,1)
    glBegin(GL_LINES)
    glVertex2f(0, lineStart)
    glVertex2f(0, lineEnd)
    glEnd()
    
    glPopMatrix()

# Visualization of the Primary Flight Display part
# NOTE: should call self.GoToOrigin() instead of glLoadIdentity()
class PrimaryFlightDisplay(wx.Panel):
    def __init__(self, parent, size, style, dataInput):
        super(PrimaryFlightDisplay, self).__init__(parent, size=size,
                                                   style=style)
        
        # the width and height of the draw-able area
        self.width, self.height = self.GetClientSizeTuple()
        self.hwidth, self.hheight = self.width/2, self.height/2
        
        # Create widgets to display altitude and speed
        """
        altitudeBox = wx.Panel(self, size=(100,50), style=wx.SIMPLE_BORDER)
        altitudeBox.SetBackgroundColour(wx.BLACK)
        altitudeBox.SetPosition((self.width*4/5,self.height/2-25))
        self.altText = wx.StaticText(altitudeBox,-1,size=(100,50),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.altText.SetForegroundColour(wx.WHITE)
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        font.SetWeight(wx.BOLD)
        self.altText.SetFont(font)
        self.altText.SetPosition((0,8))
        
        spdBox = wx.Panel(self, size=(100,50), style=wx.SIMPLE_BORDER)
        spdBox.SetBackgroundColour(wx.BLACK)
        spdBox.SetPosition((self.width/5-100,self.height/2-25))
        self.spdText = wx.StaticText(spdBox,-1,size=(100,50),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.spdText.SetForegroundColour(wx.WHITE)
        self.spdText.SetFont(font)
        self.spdText.SetPosition((0,8))
        """

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
        
        # define parameters for drawing
        self.pixelsPerPitch = self.height/100 # how many pixels per deg pitch
        # by "canvas" I mean the colored part. i.e. sky and ground
        self.canvasHeight = self.pixelsPerPitch * 210
        self.canvasWidth = self.width
    
        self.windowOffset = self.height/10 # center offset for attitude indicator
        self.windowHorzOffset = -30

        self.pixelsPerTenMeters = 80 # altitude box
        self.pixelsPerTenKph = 60 # airspeed box

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
        self.OnAttitudePaint()
        self.OnAltitudePaint()
        self.OnVerticalSpeedPaint()
        self.OnAirspeedPaint()
        self.OnCompassPaint()
        
        self.canvas.SwapBuffers()
        event.Skip()
    
    def OnInitGL(self):
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.hwidth,self.hwidth,self.hheight,-self.hheight,0,1)
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(2)
        self.quadric = gluNewQuadric()
        self.quadric2 = gluNewQuadric()
        # enable the alpha channel
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # enable line smoothing
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
        
        ### NOTE: the coordinate origin of the glPrint function is
        ### at the bottom-left corner. Be aware of it !!!
        self.myFont = glFreeType.font_data(self.dataInput.cwd+"\Font.ttf", 30)
        self.myCompassFont = glFreeType.font_data(self.dataInput.cwd+"\Font.ttf", 22)
    
    # Go to a self-defined origin that's consistent throughout this class.
    # glLoadIdentity() will take me to the center of the canvas (the true origin
    # as defined in OnInitGL). Then I will call glTranslatef to add my own offset.
    def GoToOrigin(self, drawingFont=False):
        glLoadIdentity()
        # Translate up 1/5 of the window height, so that we are centered upward
        if not drawingFont:
            glTranslatef(self.windowHorzOffset, -self.windowOffset, 0)
        else:
            glTranslatef(self.windowHorzOffset, self.windowOffset, 0)

    ### Actually draw things here!! ###
    def OnAttitudePaint(self):
        rollRotation = self.dataInput.data["roll"]

        glClear(GL_COLOR_BUFFER_BIT)
        self.GoToOrigin()
        # Rotate, and then Translate. That's what I want! #
        glRotatef(rollRotation,0,0,1)
        # Translate along the "rotated direction"
        glTranslatef(0, self.dataInput.data["pitch"]*self.pixelsPerPitch,
                     0) 
        
        ####################################
        ####      Draw Stuff Here       ####
        ####################################
        
        #### Draw Sky ####
        glBegin(GL_QUADS)
        glColor(0.00392, 0.333, 0.616)
        glVertex2f(-self.canvasWidth, -self.canvasHeight)
        glVertex2f(self.canvasWidth, -self.canvasHeight)
        glVertex2f(self.canvasWidth, 0)
        glVertex2f(-self.canvasWidth,0)
        glEnd()
        
        #### Draw Ground ####
        glBegin(GL_QUADS)
        glColor(0.722, 0.208, 0)
        glVertex2f(-self.canvasWidth,0)
        glVertex2f(self.canvasWidth,0)
        glVertex2f(self.canvasWidth,self.canvasHeight)
        glVertex2f(-self.canvasWidth,self.canvasHeight)
        glEnd()
        
        #### Draw Horizon ####
        glBegin(GL_LINES)
        glColor(1, 1, 1)
        glVertex2f(-self.canvasWidth,0)
        glVertex2f(self.canvasWidth,0)
        glEnd()
        
        # to make lines thicker, use glLineWidth(2)
        #### Draw Pitch Lines ####
        
        # sky is a boolean value, used to determine whether I am drawing
        # lines in the sky or on the ground.
        def drawLine(length, sky, drawDeg=0):
            glBegin(GL_LINES)
            glColor(1,1,1)
            height = -deg*self.pixelsPerPitch/10 if sky else deg*self.pixelsPerPitch/10
            glVertex2f(-length, height)
            glVertex2f(length, height)
            glEnd()
            
            if drawDeg != 0:
                ### draw the degree text ####
                ### Using techniques from Nehe tutorial lesson43.py ###
                ### Need to install PIL and Pillow ###
                glPushMatrix()
                self.GoToOrigin(True)

                glTranslatef(centerX, centerY, 0)
                glRotatef(-rollRotation,0,0,1)
                glTranslatef(0, -self.dataInput.data["pitch"]*self.pixelsPerPitch,0) 
                glTranslatef(length+30, height-5, 0)
                self.myFont.glPrint(0, 0, "%d"%drawDeg)
                glTranslatef(-2*length-90, 0, 0)
                self.myFont.glPrint(0, 0, "%d"%drawDeg)
                
                glPopMatrix()
        
        # Draw pitch bars
        centerX = self.hwidth
        centerY = self.hheight
        glScissor(centerX-180+self.windowHorzOffset,centerY-200+self.windowOffset,360,400)
        glEnable(GL_SCISSOR_TEST)
        
        glLineWidth(3)
        barMaxLen = 60 # max length for the white pitch bars (divisible by 4)
        for deg in xrange(25, 1151, 25): # deg*10
            if deg <= 900:
                if deg%100 == 0:
                    # draw on the sky
                    drawLine(barMaxLen, True, deg/10)
                    # draw on the ground
                    drawLine(barMaxLen, False, deg/10)
                elif deg%50 == 0:
                    # draw on the sky
                    drawLine(barMaxLen/2, True)
                    # draw on the ground
                    drawLine(barMaxLen/2, False)
                elif deg%25 == 0:
                    # draw on the sky
                    drawLine(barMaxLen/4, True)
                    # draw on the ground
                    drawLine(barMaxLen/4, False)
            # continue to draw lines when deg > 90, to make transition better0
            else:
                if deg%100 == 0:
                    # draw on the sky
                    drawLine(barMaxLen, True, (900 - (deg - 900))/10)
                    # draw on the ground
                    drawLine(barMaxLen, False, (900 - (deg - 900))/10)
                elif deg%50 == 0:
                    # draw on the sky
                    drawLine(barMaxLen/2, True)
                    # draw on the ground
                    drawLine(barMaxLen/2, False)
                elif deg%25 == 0:
                    # draw on the sky
                    drawLine(barMaxLen/4, True)
                    # draw on the ground
                    drawLine(barMaxLen/4, False)
        glDisable(GL_SCISSOR_TEST)
        glLineWidth(2)
        
        #### Draw Static elements ####
        self.GoToOrigin()
        
        # Draw the roll indicator
        glPushMatrix()
        glRotatef(rollRotation,0,0,1)
        ringInner = 253
        ringOuter = 255
        #gluPartialDisk(self.quadric, ringInner, ringOuter, 20, 5, 120, 120)
        gluPartialDisk(self.quadric, ringInner, ringOuter, 20, 5, 135, 90)

        # draw markings on the roll indicator
        glLineWidth(3)
        ##drawRotatedLine(120, ringInner, ringOuter + 30)
        drawRotatedLine(135, ringInner, ringOuter + 15)
        drawRotatedLine(150, ringInner, ringOuter + 30)
        drawRotatedLine(160, ringInner, ringOuter + 15)
        drawRotatedLine(170, ringInner, ringOuter + 15)
        drawRotatedLine(190, ringInner, ringOuter + 15)
        drawRotatedLine(200, ringInner, ringOuter + 15)
        drawRotatedLine(210, ringInner, ringOuter + 30)
        drawRotatedLine(225, ringInner, ringOuter + 15)
       # drawRotatedLine(240, ringInner, ringOuter + 30)
        # draw the triangular center marking
        glBegin(GL_TRIANGLES)
        glVertex2f(0, -ringInner)
        glVertex2f(-8, -ringOuter-20)
        glVertex2f(8, -ringOuter-20)
        glEnd()
        
        glPopMatrix()
        
        # draw the static triangle tip for roll indication
        glBegin(GL_TRIANGLES)
        glVertex2f(0, -ringInner)
        glVertex2f(-10, -ringInner+22)
        glVertex2f(10, -ringInner+22)
        glEnd()
        
        def drawRect(x0,y0,x1,y1):
            # draw white outline
            glColor(1,1,1)
            glBegin(GL_QUADS)
            glVertex2f(x0,y0)
            glVertex2f(x1,y0)
            glVertex2f(x1,y1)
            glVertex2f(x0,y1)
            glEnd()
            # draw black body
            glColor(0,0,0)
            glBegin(GL_QUADS)
            glVertex2f(x0+1,y0+1)
            glVertex2f(x1-1,y0+1)
            glVertex2f(x1-1,y1-1)
            glVertex2f(x0+1,y1-1)
            glEnd()
        
        def drawRectNoOutline(x0, y0, x1, y1, RGB):
            glColor(RGB[0],RGB[1],RGB[2])
            glBegin(GL_QUADS)
            glVertex2f(x0+1,y0+1)
            glVertex2f(x1-1,y0+1)
            glVertex2f(x1-1,y1-1)
            glVertex2f(x0+1,y1-1)
            glEnd()
        
        #### Draw attitude reference ####
        # left and right limit of the whole reference bar
        left = -self.width/5
        right = self.width/5
        drawRect(left,-4,-40,4) # draw left bar
        drawRect(-48, -4, -40, (-left+40)/10) # draw left vertical bar
        drawRectNoOutline(left,-4,-40,4,(0,0,0))
        drawRect(40,-4,right,4) # draw right bar
        drawRect(40, -4, 48, (right+40)/10) # draw left vertical bar
        drawRectNoOutline(40,-4,right,4,(0,0,0))
        drawRect(-5,-5,5,5)     # draw center dot

        #### Draw HACS mode text ####
        #drawRect(self.hwidth-self.windowHorzOffset-120, -self.hheight+self.windowOffset+10, self.hwidth-self.windowHorzOffset-20, -self.hheight+self.windowOffset+50)
        self.GoToOrigin(True)
        glTranslatef(self.hwidth-40, self.hheight + 310, 0)
        glColor3f(1.0, 1.0, 1.0)
        self.myFont.glPrint(0,0, self.dataInput.getModeText())
        
    def OnCompassPaint(self):
        self.GoToOrigin()
        diskYOffset = -50

        # glTranslatef(xxxx) move the compass to wherever I want.
        ringOuter = 350
        glTranslatef(0, self.height/2 + ringOuter+diskYOffset, 0)
        
        # draw the underlying circle and the outline dial ring,
        # rotated by OFFSET degrees
        glColor4f(4/255.0,10/255.0,10/255.0,118/255.0)
        gluPartialDisk(self.quadric2, 0, ringOuter, 20, 5, 100, 160)
        
        # draw markings
        glRotatef(-self.dataInput.data["yaw"], 0, 0, 1)
        glLineWidth(2)
        glColor3f(1,1,1)
        degText = 0
        for deg in xrange(0, 360, 10):
            drawRotatedLine(180+deg, ringOuter-17, ringOuter)
            
        for deg in xrange(0, 360, 10):
            drawRotatedLine(185+deg, ringOuter-10, ringOuter)
        
        # prepare to draw compass digits
        self.GoToOrigin(True)
        glColor3f(1,1,1)
        glTranslatef(self.width/2, -ringOuter-diskYOffset, 0)
        for deg in xrange(0, 360, 10):
            glPushMatrix()
            glRotatef(self.dataInput.data["yaw"]-deg, 0, 0, 1)
            if (deg < 100): shiftLeft = -5
            else: shiftLeft = -10
            glTranslatef(shiftLeft, ringOuter-38, 0)
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
        
        # draw the HDG text box
        self.GoToOrigin()
        glColor4f(4/255.0,10/255.0,10/255.0,190/255.0)
        glTranslatef(0, self.height/2 + diskYOffset, 0)
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 0)
        glVertex2f(-8, -8)
        glVertex2f(8, -8)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(-40, -8)
        glVertex2f(-40, -45)
        glVertex2f(40, -45)
        glVertex2f(40, -8)
        glEnd()

        # draw the outline for the above box
        glColor3f(1,1,1)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(-8, -8)
        glVertex2f(-40, -8)
        glVertex2f(-40, -45)
        glVertex2f(40, -45)
        glVertex2f(40, -8)
        glVertex2f(8, -8)
        glEnd()

        # draw the HDG text
        self.GoToOrigin(True)
        glTranslatef(self.width/2 - 26, -diskYOffset+17, 0)
        self.myFont.glPrint(0,0, "%03d"%self.dataInput.data["yaw"])

    # Vertical Speed Indicator
    def OnVerticalSpeedPaint(self):
        self.GoToOrigin()
        glColor4f(4/255.0,10/255.0,10/255.0,220/255.0)

        boxWidth = 50
        leftBoxHalfHeight = 225
        RightBoxHalfHeight = 160

        # Left edge
        x0, y0 = self.VSBoxLeftEdgeX, -leftBoxHalfHeight # top left corner
        y1 = leftBoxHalfHeight
        x2, y2 = x0 + boxWidth, RightBoxHalfHeight
        y3 = -RightBoxHalfHeight

        # draw the VSI box
        glBegin(GL_QUADS)
        glVertex2f(x0, y0)
        glVertex2f(x0, y1)
        glVertex2f(x2, y2)
        glVertex2f(x2, y3)
        glEnd()
        glColor3f(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x0, y0)
        glVertex2f(x0, y1)
        glVertex2f(x2, y2)
        glVertex2f(x2, y3)
        glEnd()

        # draw markings
        xMarkLeft = x0 + 20
        xMarkRight = xMarkLeft + 10

        yMark1 = 58
        yMark2 = 116
        yMark3 = 145
        yMark4 = 174

        glBegin(GL_LINES)
        glVertex2f(xMarkLeft, 0)
        glVertex2f(xMarkRight, 0)
        glVertex2f(xMarkLeft, yMark1)
        glVertex2f(xMarkRight, yMark1)
        glVertex2f(xMarkLeft, -yMark1)
        glVertex2f(xMarkRight, -yMark1)
        glVertex2f(xMarkLeft, yMark2)
        glVertex2f(xMarkRight, yMark2)
        glVertex2f(xMarkLeft, -yMark2)
        glVertex2f(xMarkRight, -yMark2)
        glVertex2f(xMarkLeft, yMark3)
        glVertex2f(xMarkRight, yMark3)
        glVertex2f(xMarkLeft, -yMark3)
        glVertex2f(xMarkRight, -yMark3)
        glVertex2f(xMarkLeft, yMark4)
        glVertex2f(xMarkRight, yMark4)
        glVertex2f(xMarkLeft, -yMark4)
        glVertex2f(xMarkRight, -yMark4)
        glEnd()

        xFont = self.hwidth + self.VSBoxLeftEdgeX + 6
        yFont = self.hheight + self.windowOffset + self.windowOffset - 6

        self.myCompassFont.glPrint(xFont, yFont, "0")
        self.myCompassFont.glPrint(xFont, yFont + yMark1, "1")
        self.myCompassFont.glPrint(xFont, yFont - yMark1, "1")
        self.myCompassFont.glPrint(xFont, yFont + yMark2, "2")
        self.myCompassFont.glPrint(xFont, yFont - yMark2, "2")
        self.myCompassFont.glPrint(xFont, yFont + yMark3, "5")
        self.myCompassFont.glPrint(xFont, yFont - yMark3, "5")
        self.myCompassFont.glPrint(xFont, yFont + yMark4, "8")
        self.myCompassFont.glPrint(xFont, yFont - yMark4, "8")

        # draw the needle
        vs = abs(self.dataInput.data["verticalspeed"])
        if (vs < 2.0): 
            needleY = (vs / 2.0) * yMark2
        else:
            needleY = yMark2 + ((vs - 2.0) / 6.0) * (yMark4 - yMark2)

        yFontUp = self.hheight + self.windowOffset + self.windowOffset + leftBoxHalfHeight + 6
        yFontDn = self.hheight + self.windowOffset + self.windowOffset - leftBoxHalfHeight - 16

        if (self.dataInput.data["verticalspeed"] > 0):
            needleY = -needleY
            if (self.dataInput.data["verticalspeed"] > 0.2):
                self.myCompassFont.glPrint(xFont, yFontUp , "%0.1f"%self.dataInput.data["verticalspeed"])
        elif self.dataInput.data["verticalspeed"] < -0.2:
            self.myCompassFont.glPrint(xFont, yFontDn , "%0.1f"%abs(self.dataInput.data["verticalspeed"]))

        glLineWidth(5)
        glBegin(GL_LINES)
        glVertex2f(x2-3, 0)
        glVertex2f(xMarkLeft, needleY)
        glEnd()

    # The sliding altitude indicator
    def OnAltitudePaint(self):
        self.GoToOrigin()
        #glTranslatef(0, 100, 0)
        glColor4f(4/255.0,10/255.0,10/255.0,180/255.0)

        boxWidth, halfBoxHeight = 100, 225
        edgeMargin = 50
        x0, y0 = self.hwidth-boxWidth-edgeMargin, -halfBoxHeight
        x1, y1 = self.hwidth-edgeMargin, halfBoxHeight

        # parameters to be used by the VSI box
        self.VSBoxLeftEdgeX = x0 + boxWidth + 20

        # draw the altitude box
        glBegin(GL_QUADS)
        glVertex2f(x0, y0) # top left corner
        glVertex2f(x1, y0) # top right corner
        glVertex2f(x1, y1+5) # bottome right
        glVertex2f(x0, y1+5) # bottom left
        glEnd()
        glColor3f(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x0, y0) # top left corner
        glVertex2f(x1, y0) # top right corner
        glVertex2f(x1, y1+5) # bottome right
        glVertex2f(x0, y1+5) # bottom left
        glEnd()

        # draw altitude markers
        self.GoToOrigin()
        alt = self.dataInput.data["altitude"]
        xLeft = x0
        xRight = xLeft + boxWidth / 6
        barStartAlt = math.floor(alt / 10.0) * 10
        barStart = int((alt % 10) * self.pixelsPerTenMeters / 10.0)

        glBegin(GL_LINES)
        tempAlt = barStartAlt # tempAlt is used to draw the alt texts
        # draw bars downward
        for y in xrange(barStart, halfBoxHeight, self.pixelsPerTenMeters): 
            if tempAlt < 0: break
            glVertex2f(xLeft, y)
            glVertex2f(xRight, y)
            tempAlt -= 10
        # draw bars upward
        tempAlt = barStartAlt
        for y in xrange(barStart-self.pixelsPerTenMeters, -halfBoxHeight, -self.pixelsPerTenMeters):
            glVertex2f(xLeft, y)
            glVertex2f(xRight, y)
            tempAlt += 10
            if tempAlt < 0: continue
        glEnd()

        # find out the coordinates relative to the bottom-left corner
        xFont = self.hwidth + xRight + 10
        yFontBase = self.hheight + self.windowOffset + self.windowOffset - 8

        # draw texts downward
        tempAlt = barStartAlt # tempAlt is used to draw the alt texts
        for y in xrange(-barStart, -halfBoxHeight, -self.pixelsPerTenMeters):
            if tempAlt < 0: break
            self.myCompassFont.glPrint(xFont, yFontBase+y, "%d"%tempAlt)
            tempAlt -= 10
        # draw texts upward
        tempAlt = barStartAlt + 10
        for y in xrange(-barStart+self.pixelsPerTenMeters, halfBoxHeight, self.pixelsPerTenMeters):
            if tempAlt < 0: 
                tempAlt += 10
                continue
            self.myCompassFont.glPrint(xFont, yFontBase+y, "%d"%tempAlt)
            tempAlt += 10

        # draw the static box holding exact altitude text
        glColor4f(4/255.0,10/255.0,10/255.0,180/255.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(xRight, 0)
        glVertex2f(xRight+8, -8)
        glVertex2f(xRight+8, 8)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(xRight+8, -22)
        glVertex2f(xRight+8, 22)
        glVertex2f(x1+10, 22)
        glVertex2f(x1+10, -22)
        glEnd()

        # draw the outline for the above box
        glColor3f(1,1,1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(xRight, 0)
        glVertex2f(xRight+8, -8)
        glVertex2f(xRight+8, -22)
        glVertex2f(x1+10, -22)
        glVertex2f(x1+10, 22)
        glVertex2f(xRight+8, 22)
        glVertex2f(xRight+8, 8)
        glEnd()

        self.myFont.glPrint(xFont+7, yFontBase, "%d"%alt)

    # TODO: make the sliding airspeed indicator
    def OnAirspeedPaint(self):
        self.GoToOrigin()
        glColor4f(4/255.0,10/255.0,10/255.0,180/255.0)

        boxWidth, halfBoxHeight = 100, 225
        edgeMargin = 50
        x0, y0 = self.hwidth-boxWidth-edgeMargin, -halfBoxHeight
        x1, y1 = self.hwidth-edgeMargin, halfBoxHeight
        x0 = -x0
        x1 = -x1

        # draw the altitude box
        glBegin(GL_QUADS)
        glVertex2f(x0, y0) # top left corner
        glVertex2f(x1, y0) # top right corner
        glVertex2f(x1, y1+5) # bottome right
        glVertex2f(x0, y1+5) # bottom left
        glEnd()
        glColor3f(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x0, y0) # top left corner
        glVertex2f(x1, y0) # top right corner
        glVertex2f(x1, y1+5) # bottome right
        glVertex2f(x0, y1+5) # bottom left
        glEnd()

        # draw airspeed markers
        self.GoToOrigin()
        aspd = self.dataInput.data["airspeed"] * 3.6
        xRight = x0
        xLeft = xRight - boxWidth / 6
        barStartAspd = math.floor(aspd / 10.0) * 10
        barStart = int((aspd % 10) * self.pixelsPerTenKph / 10.0)

        glBegin(GL_LINES)
        tempAspd = barStartAspd # tempAspd is used to draw the airspeed texts
        # draw bars downward
        for y in xrange(barStart, halfBoxHeight, self.pixelsPerTenKph): 
            if tempAspd < 0: break
            glVertex2f(xLeft, y)
            glVertex2f(xRight, y)
            tempAspd -= 10
        # draw bars upward
        tempAspd = barStartAspd + 10
        for y in xrange(barStart-self.pixelsPerTenKph, -halfBoxHeight, -self.pixelsPerTenKph):
            if tempAspd < 0: 
                tempAspd += 10
                continue
            glVertex2f(xLeft, y)
            glVertex2f(xRight, y)
            tempAspd += 10
        glEnd()

        # find out the coordinates relative to the bottom-left corner
        charWidth = 14
        xFont = self.hwidth + xRight - 35
        yFontBase = self.hheight + self.windowOffset + self.windowOffset - 8

        # draw texts downward
        tempAspd = barStartAspd # tempAspd is used to draw the airspeed texts
        for y in xrange(-barStart, -halfBoxHeight, -self.pixelsPerTenKph):
            if tempAspd < 0: break
            if tempAspd >= 10 and tempAspd <= 99:
                self.myCompassFont.glPrint(xFont-charWidth, yFontBase+y, "%d"%tempAspd)
            elif tempAspd >= 100 or tempAspd < 0:
                self.myCompassFont.glPrint(xFont-charWidth-charWidth, yFontBase+y, "%d"%tempAspd)
            else:
                self.myCompassFont.glPrint(xFont, yFontBase+y, "%d"%tempAspd)
            tempAspd -= 10
        # draw texts upward
        tempAspd = barStartAspd + 10
        for y in xrange(-barStart+self.pixelsPerTenKph, halfBoxHeight, self.pixelsPerTenKph):
            if tempAspd < 0: 
                tempAspd += 10
                continue
            if tempAspd >= 10 and tempAspd <= 99:
                self.myCompassFont.glPrint(xFont-charWidth, yFontBase+y, "%d"%tempAspd)
            elif tempAspd >= 100 or tempAspd < 0:
                self.myCompassFont.glPrint(xFont-charWidth-charWidth, yFontBase+y, "%d"%tempAspd)
            else:
                self.myCompassFont.glPrint(xFont, yFontBase+y, "%d"%tempAspd)
            tempAspd += 10
        
        # draw the static box holding exact airspeed text
        glColor4f(4/255.0,10/255.0,10/255.0,230/255.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(xLeft, 0)
        glVertex2f(xLeft-8, -8)
        glVertex2f(xLeft-8, 8)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(xLeft-8, -22)
        glVertex2f(xLeft-8, 22)
        glVertex2f(x1, 22)
        glVertex2f(x1, -22)
        glEnd()

        # draw the outline for the above box
        glColor3f(1,1,1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(xLeft, 0)
        glVertex2f(xLeft-8, -8)
        glVertex2f(xLeft-8, -22)
        glVertex2f(x1, -22)
        glVertex2f(x1, 22)
        glVertex2f(xLeft-8, 22)
        glVertex2f(xLeft-8, 8)
        glEnd()

        # exact airspeed text
        bigCharWidth = 18
        if aspd >= 10 and aspd < 100:
            self.myFont.glPrint(xFont-15-bigCharWidth, yFontBase, "%d"%int(aspd))
        elif aspd >= 100 or aspd < -1:
            self.myFont.glPrint(xFont-15-bigCharWidth-bigCharWidth, yFontBase, "%d"%int(aspd))
        else:
            self.myFont.glPrint(xFont-15, yFontBase, "%d"%int(aspd))