from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import wx
from wx import glcanvas
import wx.lib.agw.speedmeter as SM

import time,math,sys
import AbstractModel


### TODO: Think of pitch as the Phi in spherical coordinate, which has
### range 0 to pi (in my case -pi/2 to pi/2) !!!!!!!
### Model the whole airplane attitude using spherical coordinate!!!!



# Visualization of the Primary Flight Display part
class PrimaryFlightDisplay(wx.Panel):
    def __init__(self, parent, size, style, dataInput):
        super(PrimaryFlightDisplay, self).__init__(parent, size=size,
                                                   style=style)
        
        # the width and height of the draw-able area
        self.width, self.height = self.GetClientSizeTuple()
        
        # Create widgets to display altitude and speed
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
        
        hdgBox = wx.Panel(self, size=(150,50), style=wx.SIMPLE_BORDER)
        hdgBox.SetBackgroundColour(wx.BLACK)
        hdgBox.SetPosition((self.width/2-75,self.height*5/6))
        self.hdgText = wx.StaticText(hdgBox,-1,size=(150,50),style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.hdgText.SetForegroundColour(wx.WHITE)
        self.hdgText.SetFont(font)
        self.hdgText.SetPosition((0,8))
        
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
        self.pixelsPerPitch = self.height/40 # how many pixels per deg pitch
        # by "canvas" I mean the colored part. i.e. sky and ground
        self.canvasHeight = self.pixelsPerPitch * 210
        self.canvasWidth = self.width*3/4
    
    
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
        
        self.OnPaint()
        event.Skip()
    
    def OnInitGL(self):
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-320,320,240,-240,0,1)
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(2)
    
    ### Actually draw things here!! ###
    def OnPaint(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        # Rotate, and then Translate. That's what I want! #
        glRotatef(self.dataInput.readings["roll"],0,0,1)
        # Translate along the "rotated direction"
        glTranslatef(0, self.dataInput.readings["pitch"]*self.pixelsPerPitch,
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
                ### Using glutBitmapCharacter and manual matrix multiplication ###
                
                # Get the current modelview matrix
                matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
            
                glPushMatrix()
                glLoadIdentity()
                
                # Calculate the abosolute coordinate after rotation
                x,y,z,w = matrixMult(matrix, (-length-30, height, 0, 1))
                glRasterPos(x-6,y,z)
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('%d'%(drawDeg/10)))
                glRasterPos(x+6,y,z)
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('%d'%(drawDeg%10)))
                
                x,y,z,w = matrixMult(matrix, (length+20, height, 0, 1))
                glRasterPos(x-6,y,z)
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('%d'%(drawDeg/10)))
                glRasterPos(x+6,y,z)
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('%d'%(drawDeg%10)))
                
                glPopMatrix()
        
        glLineWidth(4)        
        barMaxLen = 80 # max length for the white pitch bars (divisible by 4)
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
        glLineWidth(2)
        
        #### Draw Static elements ####
        glLoadIdentity()
        
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
        
        # TODO
        def drawCompass():
            # glTranslatef(xxxx) move the compass to wherever I want.
            # glRotatef(xxxx) OFFSET rotation
            
            # draw the underlying circle and the outline dial ring,
            # rotated by OFFSET degrees
            
            # glRotatef(xxxx) ROLL rotation
            
            # draw the aircraft shape thing, rotated by ROLL degree on
            # top of OFFSET degrees.
            
            pass

        self.canvas.SwapBuffers()
    

class AuxiliaryDisplay(wx.Panel):
    def __init__(self, parent, size, style, dataInput):
        wx.Panel.__init__(self, parent, size=size, style=style)
        self.SetBackgroundColour("#444444")
        
        # The instantaneous current meter
        self.initCurrentMeter()
        
        # The mAh indicator
        self.initMAhIndicator()
        
        # text display
        mAhLabel = wx.StaticText(self,-1,size=(40,50),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        mAhLabel.SetForegroundColour(wx.WHITE)
        mAhLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        mAhLabel.SetLabel("Used:")
        volLabel = wx.StaticText(self,-1,size=(40,50),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        volLabel.SetForegroundColour(wx.WHITE)
        volLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        volLabel.SetLabel("Batt:")
        tmpLabel = wx.StaticText(self,-1,size=(40,50),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        tmpLabel.SetForegroundColour(wx.WHITE)
        tmpLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        tmpLabel.SetLabel("Temp:")
        
        mAhUnit = wx.StaticText(self,-1,size=(35,30),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        mAhUnit.SetForegroundColour(wx.WHITE)
        mAhUnit.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        mAhUnit.SetLabel("mAh")
        volUnit = wx.StaticText(self,-1,size=(35,30),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        volUnit.SetForegroundColour(wx.WHITE)
        volUnit.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        volUnit.SetLabel("V")
        tmpUnit = wx.StaticText(self,-1,size=(35,30),style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        tmpUnit.SetForegroundColour(wx.WHITE)
        tmpUnit.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        tmpUnit.SetLabel("`C")
        
        self.mAhText = wx.StaticText(self,-1,size=(60,50),style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.mAhText.SetForegroundColour(wx.GREEN)
        font = wx.Font(15, wx.SWISS, wx.NORMAL, wx.NORMAL)
        font.SetWeight(wx.BOLD)
        self.mAhText.SetFont(font)
        self.volText = wx.StaticText(self,-1,size=(60,50),style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.volText.SetForegroundColour(wx.GREEN)
        self.volText.SetFont(font)
        self.tmpText = wx.StaticText(self,-1,size=(60,50),style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.tmpText.SetForegroundColour(wx.WHITE)
        font = wx.Font(15, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.tmpText.SetFont(font)
        
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer1.Add(mAhLabel, 0, wx.ALL, border=5)
        hsizer1.Add(self.mAhText, 0, wx.ALL, border=5)
        hsizer1.Add(mAhUnit, 0, wx.ALL, border=5)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(volLabel, 0, wx.ALL, border=5)
        hsizer2.Add(self.volText, 0, wx.ALL, border=5)
        hsizer2.Add(volUnit, 0, wx.ALL, border=5)
        hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer3.Add(tmpLabel, 0, wx.ALL, border=5)
        hsizer3.Add(self.tmpText, 0, wx.ALL, border=5)
        hsizer3.Add(tmpUnit, 0, wx.ALL, border=5)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer1, 0, wx.ALL, border=0)
        vsizer.Add(hsizer2, 0, wx.ALL, border=0)
        vsizer.Add(hsizer3, 0, wx.ALL, border=0)
        
        #### Sizers ####
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.crtMeter, 0, wx.ALL, border=10)
        hsizer.Add(self.mAhIndicator, 0, wx.ALL, border=10)
        hsizer.Add(vsizer, 0, wx.TOP | wx.LEFT, border=25)
        self.SetSizer(hsizer)
        self.Fit()
    
    def initCurrentMeter(self):
        # SM_DRAW_HAND: We Want To Draw The Hand (Arrow) Indicator
        # SM_DRAW_SECTORS: Full Sectors Will Be Drawn, To Indicate Different Intervals
        # SM_DRAW_MIDDLE_TEXT: We Draw Some Text In The Center Of SpeedMeter
        # SM_DRAW_SECONDARY_TICKS: We Draw Secondary (Intermediate) Ticks Between
        #                          The Main Ticks (Intervals)
        
        self.crtMeter = SM.SpeedMeter(self, size=(200,200), agwStyle=SM.SM_DRAW_HAND |
                                      SM.SM_DRAW_PARTIAL_SECTORS |
                                      SM.SM_DRAW_MIDDLE_TEXT |
                                      SM.SM_DRAW_SECONDARY_TICKS)
        
        # Set The Region Of Existence Of SpeedMeter (Always In Radians!!!!
        self.crtMeter.SetAngleRange(-math.pi/4, math.pi*5/4)
        
        # Create The Intervals That Will Divide Our SpeedMeter In Sectors
        intervals = range(0, 21, 5)
        self.crtMeter.SetIntervals(intervals)
        
        # Assign The Same Colours To All Sectors (We Simulate A Car Control For Speed)
        # Usually This Is Black
        self.crtMeter.SetIntervalColours([self.GetBackgroundColour()]*3+[wx.RED])
        
        # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        ticks = ['  '+str(interval)+' ' for interval in intervals]
        self.crtMeter.SetTicks(ticks)
        # Set The Ticks/Tick Markers Colour
        self.crtMeter.SetTicksColour(wx.WHITE)#"#EDDE07")
        # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.crtMeter.SetNumberOfSecondaryTicks(3)
        
        # Set The Font For The Ticks Markers
        self.crtMeter.SetTicksFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Set The Text In The Center Of SpeedMeter
        self.crtMeter.SetMiddleText("A")
        # Assign The Colour To The Center Text
        self.crtMeter.SetMiddleTextColour(wx.WHITE)
        # Assign A Font To The Center Text
        self.crtMeter.SetMiddleTextFont(wx.Font(15, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Set The Colour For The Hand Indicator
        self.crtMeter.SetHandColour(wx.Colour(255, 50, 0))

        # Do Not Draw The External (Container) Arc. Drawing The External Arc May
        # Sometimes Create Uglier Controls. Try To Comment This Line And See It
        # For Yourself!
        self.crtMeter.DrawExternalArc(False)
        
        # Set background color
        self.crtMeter.SetSpeedBackground(self.GetBackgroundColour())
        
        # Set The Current Value For The SpeedMeter
        self.crtMeter.SetSpeedValue(0)
    
    def initMAhIndicator(self):
        self.mAhIndicator = SM.SpeedMeter(self, size=(200,200), agwStyle=SM.SM_DRAW_HAND |
                                      SM.SM_DRAW_PARTIAL_SECTORS)
        
        self.mAhIndicator.SetAngleRange(-math.pi/3,math.pi/3)
        
        intervals = range(0, 5)
        self.mAhIndicator.SetIntervals(intervals)
        
        self.mAhIndicator.SetIntervalColours([self.GetBackgroundColour()]*3+[wx.RED])
        
        ticks = ["F  ", "", "", "", "E  "]
        self.mAhIndicator.SetTicks(ticks)
        self.mAhIndicator.SetTicksColour(wx.WHITE)
        
        self.mAhIndicator.SetHandColour(wx.RED)
        
        self.mAhIndicator.DrawExternalArc(False)
        self.mAhIndicator.SetSpeedBackground(self.GetBackgroundColour())
        
        
# Visualization of the Nautical Display part
class NauticalDisplay(wx.Panel):
    def __init__(self, parent, size, style, dataInput):
        wx.Panel.__init__(self, parent, size=size, style=style)
        
        ### TODO: Remove me!! I am temp !!! ###
        text = wx.StaticText(self, -1, "\n\n\n\n\nUnder Construction", size=size,
                             style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        text.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))
    
    # Do other stuff here
    

# The overall GUI that integrates several parts to a whole.
class GroundStationGUI(wx.Frame):
    def __init__(self, parent, title, dataInput):
        # create a Non-resizable, auto-size frame
        wx.Frame.__init__(self, parent, title=title,
                          style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX |
                          wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                          wx.CLIP_CHILDREN)
        
        # Setting up the menu object
        Settingmenu = wx.Menu() # The abstract menu
        
        # Creating the menu bar
        menuBar = wx.MenuBar() # The visible menu bar
        menuBar.Append(Settingmenu, "&Settings")
        self.SetMenuBar(menuBar)
        
        # create the underlying panel
        bgPanel = wx.Panel(self)
        
        # create a custom panel for Primary Flight Display
        self.PFD = PrimaryFlightDisplay(bgPanel, size=(800,600),
                                        style=wx.SIMPLE_BORDER,
                                        dataInput=dataInput)
        boxPFD = wx.StaticBox(bgPanel, -1, "Primary Flight Display",size=(800,600))
        boxPFDSizer = wx.StaticBoxSizer(boxPFD, wx.VERTICAL)
        boxPFDSizer.Add(self.PFD, 0, wx.EXPAND|wx.ALL, border=5)
        
        # create a custom panel for Auxilary readings Display
        self.AD = AuxiliaryDisplay(bgPanel, size=(800,120), style=wx.SIMPLE_BORDER,
                                   dataInput=dataInput)
        boxPFDSizer.Add(self.AD, 0, wx.EXPAND|wx.ALL, border=5)
        
        # create a custom panel for Nautical Display
        self.ND = NauticalDisplay(bgPanel, size=(800,600),
                                  style=wx.SIMPLE_BORDER,
                                  dataInput=dataInput)
        boxND = wx.StaticBox(bgPanel, -1, "Nautical Display", size=(800,600))
        boxNDSizer = wx.StaticBoxSizer(boxND, wx.VERTICAL)
        boxNDSizer.Add(self.ND, 0, wx.EXPAND|wx.ALL, border=5)
        
        # create a button to reset the altitude offset
        buttonAltReset = wx.Button(bgPanel, 1, "Abs/Rel Altitude")
        
        self.Bind(wx.EVT_BUTTON, self.OnClick, buttonAltReset)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # sizers for overall layout
        v2sizer = wx.BoxSizer(wx.VERTICAL)
        v2sizer.Add(boxNDSizer, 0, wx.ALL, border=5)
        v2sizer.Add(buttonAltReset, 0, wx.ALL, border=5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(boxPFDSizer, 0, wx.ALL, border=5) # Set border width between ND and PFD
        hsizer.Add(v2sizer, 0, wx.ALL, border=5)
        
        # Auto size the frame and show
        bgPanel.SetSizer(hsizer)
        bgPanel.Fit()
        self.Fit()
        self.Show(True)
        
        # set off the timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(30) # ms
    
    def OnTimer(self, event):
        self.PFD.Refresh()
        # update altitude, heading and speed text
        self.PFD.altText.SetLabel("%3d m"%self.PFD.dataInput.altitude)
        self.PFD.spdText.SetLabel("N/A")
        self.PFD.hdgText.SetLabel("%d Deg"%self.PFD.dataInput.readings["heading"])
        self.AD.mAhText.SetLabel("%4d"%self.PFD.dataInput.readings["mAh"])
        self.AD.volText.SetLabel("%4.2f"%self.PFD.dataInput.readings["voltage"])
        self.AD.tmpText.SetLabel("%3.1f"%self.PFD.dataInput.readings["temperature"])
        # update amperemeter reaidng
        self.AD.crtMeter.SetSpeedValue(self.PFD.dataInput.readings["current"])
        # update mah reading
        self.AD.mAhIndicator.SetSpeedValue(self.PFD.dataInput.readings["mAh"]*4.0/self.PFD.dataInput.batt_capacity)
        # update voltage text color
        if (self.PFD.dataInput.readings["voltage"] - 11.20 <= 0):
            self.AD.volText.SetForegroundColour(wx.RED)
        else:
            self.AD.volText.SetForegroundColour(wx.GREEN)
    
    def OnClick(self, event):
        id = event.GetId()
        if (id == 1):
            # switch between absolute and relative altitude
            if(self.PFD.dataInput.EN_ALT_OFFSET == False):
                self.PFD.dataInput.altitudeOffset = self.PFD.dataInput.altitude
                self.PFD.dataInput.EN_ALT_OFFSET = True
            else:
                self.PFD.dataInput.altitudeOffset = 0
                self.PFD.dataInput.EN_ALT_OFFSET = False
    
    def OnClose(self, event):
        self.PFD.dataInput.exitFlag = True
        self.timer.Stop()
        self.Destroy()

# Note: OpenGL matrix is column major
def matrixMult(m, v):
    r = [0,0,0,0]
    r[0] = m[0][0]*v[0]+m[1][0]*v[1]+m[2][0]*v[2]+m[3][0]*v[3]
    r[1] = m[0][1]*v[0]+m[1][1]*v[1]+m[2][1]*v[2]+m[3][1]*v[3]
    r[2] = m[0][2]*v[0]+m[1][2]*v[1]+m[2][2]*v[2]+m[3][2]*v[3]
    r[3] = m[0][3]*v[0]+m[1][3]*v[1]+m[2][3]*v[2]+m[3][3]*v[3]
    return r[0],r[1],r[2],r[3]

app = wx.App(False)
dataInput = AbstractModel.DataInput()
f = GroundStationGUI(None, "Ground Station Beta", dataInput)
app.MainLoop()