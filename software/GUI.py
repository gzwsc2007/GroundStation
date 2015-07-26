from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import wx
from wx import glcanvas
import wx.lib.agw.speedmeter as SM

import time,math,sys
import AbstractModel
import glFreeType

import PrimaryFlightDisplay
import NavigationDisplay

# names for the ND scale choices
ND_SCALE_CHOICE_LIST = ["30 m/div", "50 m/div", "100 m/div", "200 m/div", "500 m/div"]

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
        intervals = range(0, 51, 10)
        self.crtMeter.SetIntervals(intervals)

        # Assign The Same Colours To All Sectors (We Simulate A Car Control For Speed)
        # Usually This Is Black
        self.crtMeter.SetIntervalColours([self.GetBackgroundColour()]*4+[wx.RED])

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



# The overall GUI that integrates several parts to a whole.
class GroundStationGUI(wx.Frame):
    def __init__(self, parent, title, dataInput):
        # create a Non-resizable, auto-size frame
        wx.Frame.__init__(self, parent, title=title,
                          style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX |
                          wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                          wx.CLIP_CHILDREN)

        # Setting up the menu object
        LogMenu = wx.Menu() # The abstract menu
        LogMenu.Append(101, "Start/Stop Log", "Start or Stop logging data", wx.ITEM_CHECK)

        # Calibration menu
        CalMenu = wx.Menu()
        CalMenu.Append(201, "Start/Stop Mag Cal", "Start or Stop Magnetometer Calibration", wx.ITEM_CHECK)
        CalMenu.Append(202, "Airspeed Cal", "Perform airspeed zero calibration", wx.ITEM_NORMAL)
        CalMenu.Append(203, "Altimeter Cal", "Perform altimeter zero calibration", wx.ITEM_NORMAL)
        CalMenu.Append(204, "Trim Value Cal", "Remember the current trim values on Aileron, Elevator and Rudder", wx.ITEM_NORMAL)

        # System Identification menu
        SysidMenu = wx.Menu()
        SysidMenu.Append(301, "Start/Stop manual", "Start or Stop manual (free-running) system id mode", wx.ITEM_CHECK)
        SysidMenu.Append(302, "Aileron mode (LF)", "Start experiment sequence on the aileron control surface (low frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(303, "Aileron mode (HF)", "Start experiment sequence on the aileron control surface (high frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(304, "Elevator mode (LF)", "Start experiment sequence on the elevator control surface (low frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(305, "Elevator mode (HF)", "Start experiment sequence on the elevator control surface (high frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(306, "Rudder mode (LF)", "Start experiment sequence on the rudder control surface (low frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(307, "Rudder mode (HF)", "Start experiment sequence on the rudder control surface (high frequency)", wx.ITEM_NORMAL)
        SysidMenu.Append(308, "Reset modes", "Reset local system mode to MANUAL", wx.ITEM_NORMAL)

        # Creating the menu bar
        menuBar = wx.MenuBar() # The visible menu bar
        menuBar.Append(LogMenu, "&Log")
        menuBar.Append(CalMenu, "&Calibration")
        menuBar.Append(SysidMenu, "&SystemIdent")

        self.SetMenuBar(menuBar)

        # create the underlying panel
        bgPanel = wx.Panel(self)

        # create a button to reset the altitude offset
        buttonAltReset = wx.Button(bgPanel, 1, "Zero Altitude")
        # create a button to set HOME
        buttonSetHome = wx.Button(bgPanel, 2, "SetHome")
        # create a button to reset airspeed
        buttonAspdReset = wx.Button(bgPanel, 3, "Zero Airspeed")

        # create a choice menu to select scale for the Navigation Display
        scaleChoice = wx.Choice(bgPanel, 1, name="Scale", choices=ND_SCALE_CHOICE_LIST)
        scaleChoice.SetSelection(1) # default 30 m/div

        # create a spin control to set Home Bearing
        spinControl = wx.SpinCtrl(bgPanel, 1, "HomeBearing")
        spinControl.SetRange(-360,360)
        spinControl.SetValue(0)

        # create a custom panel for Primary Flight Display
        self.PFD = PrimaryFlightDisplay.PrimaryFlightDisplay(bgPanel,
                                        size=(800,850),
                                        style=wx.SIMPLE_BORDER,
                                        dataInput=dataInput)
        boxPFD = wx.StaticBox(bgPanel, -1, "Primary Flight Display",size=(800,850))
        boxPFDSizer = wx.StaticBoxSizer(boxPFD, wx.VERTICAL)
        boxPFDSizer.Add(self.PFD, 0, wx.EXPAND|wx.ALL, border=5)

        # create a custom panel for Auxilary readings Display
        self.AD = AuxiliaryDisplay(bgPanel, size=(800,100), style=wx.SIMPLE_BORDER,
                                   dataInput=dataInput)

        # create a custom panel for Navigation Display
        self.ND = NavigationDisplay.NavigationDisplay(bgPanel, size=(700,600),
                                                      style=wx.SIMPLE_BORDER,
                                                      dataInput=dataInput)
        boxND = wx.StaticBox(bgPanel, -1, "Navigation Display", size=(700,600))
        boxNDSizer = wx.StaticBoxSizer(boxND, wx.VERTICAL)
        boxNDSizer.Add(self.ND, 0, wx.EXPAND|wx.ALL, border=5)

        hbtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        hbtnSizer.Add(buttonAltReset, 0, wx.ALL, border=5)
        hbtnSizer.Add(buttonAspdReset, 0, wx.ALL, border=5)
        hbtnSizer.Add(buttonSetHome, 0, wx.ALL, border=5)
        hbtnSizer.Add(scaleChoice, 0, wx.ALL, border=5)
        hbtnSizer.Add(spinControl, 0, wx.ALL, border=5)

        boxNDSizer.Add(hbtnSizer, 0, wx.ALL, border=0)
        boxNDSizer.Add(self.AD, 0, wx.EXPAND|wx.ALL, border=5)

        self.Bind(wx.EVT_BUTTON, self.OnClick, buttonAltReset)
        self.Bind(wx.EVT_BUTTON, self.OnClick, buttonAspdReset)
        self.Bind(wx.EVT_BUTTON, self.OnClick, buttonSetHome)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, scaleChoice)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, spinControl)

        # bind menu items
        self.Bind(wx.EVT_MENU, self.OnLogClick, id=101)

        self.Bind(wx.EVT_MENU, self.OnCalClick, id=201)
        self.Bind(wx.EVT_MENU, self.OnCalClick, id=202)
        self.Bind(wx.EVT_MENU, self.OnCalClick, id=203)
        self.Bind(wx.EVT_MENU, self.OnCalClick, id=204)

        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=301)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=302)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=303)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=304)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=305)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=306)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=307)
        self.Bind(wx.EVT_MENU, self.OnSysIdClick, id=308)

        # sizers for overall layout
        v2sizer = wx.BoxSizer(wx.VERTICAL)
        v2sizer.Add(boxNDSizer, 0, wx.ALL, border=5)
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

    def OnCalClick(self, evt):
        evt_ID = evt.GetId()

        if (evt_ID == 201):
            if (evt.IsChecked()): self.PFD.dataInput.startMagCal()
            else: self.PFD.dataInput.stopMagCal()
        elif (evt_ID == 202):
            self.PFD.dataInput.doAirspeedCal()
        elif (evt_ID == 203):
            self.PFD.dataInput.doBaroCal()
        elif (evt_ID == 204):
            self.PFD.dataInput.doTrimValCal()

    def OnLogClick(self, evt):
        if (evt.IsChecked()): self.PFD.dataInput.startLogging()
        else: self.PFD.dataInput.stopLogging()

    def OnSysIdClick(self, evt):
        evt_ID = evt.GetId()

        if (evt_ID == 301):
            if (evt.IsChecked()): self.PFD.dataInput.startSysIdManual()
            else: self.PFD.dataInput.stopSysIdManual()
        elif (evt_ID == 302):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_LOWER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_AILERON)
        elif (evt_ID == 303):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_HIGHER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_AILERON)
        elif (evt_ID == 304):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_LOWER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_ELEVATOR)
        elif (evt_ID == 305):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_HIGHER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_ELEVATOR)
        elif (evt_ID == 306):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_LOWER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_RUDDER)
        elif (evt_ID == 307):
            self.PFD.dataInput.startSysIdExperiment(AbstractModel.HACS_Proxy.HACS_SYSID_FREQ_HIGHER, AbstractModel.HACS_Proxy.HACS_SYSID_MODE_RUDDER)
        elif (evt_ID == 308):
            self.PFD.dataInput.HACS_mode = AbstractModel.HACS_Proxy.HACS_MODE_MANUAL

    def OnSpin(self, evt):
        evt_ID = evt.GetId()
        obj = evt.GetEventObject()

        if (evt_ID == 1): # select HOME bearing
            val = obj.GetValue()
            val = (val + 360) % 360
            self.PFD.dataInput.homeBearing = val
            obj.SetValue(val)

    def OnChoice(self, evt):
        evt_ID = evt.GetId()
        choice = evt.GetEventObject().GetCurrentSelection()

        if (evt_ID == 1): # select ND scale
            self.ND.setScale(choice)

    def OnTimer(self, event):
        self.PFD.Refresh()
        self.ND.Refresh()
        # update altitude, heading and speed text
        #self.PFD.altText.SetLabel("%3d m"%self.PFD.dataInput.data["altitude"])
        #self.PFD.spdText.SetLabel("%2d m/s"%self.PFD.dataInput.data["airspeed"])
        self.AD.mAhText.SetLabel("%4d"%self.PFD.dataInput.data["mAh"])
        self.AD.volText.SetLabel("%4.2f"%self.PFD.dataInput.data["battV"])
        self.AD.tmpText.SetLabel("%3.1f"%self.PFD.dataInput.data["temperature"])
        # update amperemeter reaidng
        self.AD.crtMeter.SetSpeedValue(self.PFD.dataInput.data["battI"])
        # update mah reading
        self.AD.mAhIndicator.SetSpeedValue(self.PFD.dataInput.data["mAh"]*4.0/self.PFD.dataInput.batt_capacity)
        # update voltage text color
        if (self.PFD.dataInput.data["battV"] - 15.00 <= 0):
            self.AD.volText.SetForegroundColour(wx.RED)
        else:
            self.AD.volText.SetForegroundColour(wx.GREEN)

    def OnClick(self, event):
        id = event.GetId()
        if (id == 1): # altitude reset
            # switch between absolute and relative altitude
            if(self.PFD.dataInput.EN_ALT_OFFSET == False):
                self.PFD.dataInput.altitudeOffset = self.PFD.dataInput.altitude
                self.PFD.dataInput.EN_ALT_OFFSET = True
            else:
                self.PFD.dataInput.altitudeOffset = 0
                self.PFD.dataInput.EN_ALT_OFFSET = False
        elif (id == 2): # set home
            # set HOME
            self.PFD.dataInput.homeCoordRad = (math.radians(self.PFD.dataInput.data["longitude"]), \
                                                  math.radians(self.PFD.dataInput.data["latitude"]))
            self.PFD.dataInput.homeCoordDeg = self.PFD.dataInput.data["longitude"], \
                                                  self.PFD.dataInput.data["latitude"]
            self.PFD.dataInput.updateBeacons()
        elif (id == 3): # airspeed reset
            self.PFD.dataInput.aspdOffset = self.PFD.dataInput.data["airspeed"] + self.PFD.dataInput.aspdOffset

    def OnClose(self, event):
        self.PFD.dataInput.exitFlag = True
        self.timer.Stop()
        if (self.PFD.dataInput.logEnable): self.PFD.dataInput.stopLogging()
        self.Destroy()

# Note: OpenGL matrix is column major. (Deprecated)
#def matrixMult(m, v):
#    r = [0,0,0,0]
#    r[0] = m[0][0]*v[0]+m[1][0]*v[1]+m[2][0]*v[2]+m[3][0]*v[3]
#    r[1] = m[0][1]*v[0]+m[1][1]*v[1]+m[2][1]*v[2]+m[3][1]*v[3]
#    r[2] = m[0][2]*v[0]+m[1][2]*v[1]+m[2][2]*v[2]+m[3][2]*v[3]
#    r[3] = m[0][3]*v[0]+m[1][3]*v[1]+m[2][3]*v[2]+m[3][3]*v[3]
#    return r[0],r[1],r[2],r[3]

app = wx.App(False)
dataInput = AbstractModel.DataInput()
f = GroundStationGUI(None, "Ground Station Beta", dataInput)
app.MainLoop()