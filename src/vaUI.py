#!/opt/virtualenvs/ihme-va/bin/pythonw

import os
import wx
from wx import *
import pyvaPackage
from Tkinter import *
import workerthread

# TODO: help should pop up window
# TODO: bug in radio grouping
# TODO: pull out all strings
# TODO: why is the first button selected
# TODO: disable start until all options are selected


APP_EXIT = 1
APP_HELP = 2

class vaUI(wx.Frame):
    
    def __init__(self, parent, title):
        super(vaUI, self).__init__(parent, title=title, 
            size=(550, 760),style=wx.CAPTION)
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):

        self.inputFilePath = ""
        self.outputFolderPath = ""
        self.statusLog = ""
        self.selectedButton = "Adult" # default selection
        self.hce = 'HCE'
        self.running = False
        workerthread.EVT_RESULT(self,self.OnResult)
        workerthread.EVT_PROGRESS(self, self.OnProgress)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        qmi = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        hmi = wx.MenuItem(helpMenu, APP_HELP, '&Help')
        fileMenu.AppendItem(qmi)
        helpMenu.AppendItem(hmi)
        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')
        
        self.Bind(wx.EVT_MENU, self.onQuit, id=APP_EXIT)
        self.SetMenuBar(menubar)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        r0 = wx.BoxSizer(wx.HORIZONTAL)
        r1 = wx.BoxSizer(wx.HORIZONTAL)

        scaleSize = .35
        imageFile = '../res/logo.png'
        image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
        scaled_image = image.Scale(image.GetWidth()*scaleSize, image.GetHeight()*scaleSize, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        r0.AddStretchSpacer()
        r0.Add(wx.StaticBitmap(panel,-1,scaled_image),flag=wx.RIGHT, border=12)
        r0.AddStretchSpacer()


        r1.AddStretchSpacer()
        r1.Add(wx.Button(panel, label="Help"), flag=wx.RIGHT, border=12)
        quitButton = wx.Button(panel, label="Quit")
        r1.Add(quitButton, flag=wx.RIGHT, border=12)
        r2 = wx.BoxSizer(wx.HORIZONTAL)
        
        quitButton.Bind(wx.EVT_BUTTON, self.onQuit)

        r2sb1 = wx.StaticBox(panel, label="1. Input file")
        r2sbs1 = wx.StaticBoxSizer(r2sb1, wx.HORIZONTAL)

        chooseFileButton = wx.Button(panel, label="Choose file...")
        chooseFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        r2sbs1.Add(chooseFileButton, flag=wx.ALL, border=5)

        self.choosenFileText = wx.StaticText(panel, label="",size=(367, -1))
        r2sbs1.Add(self.choosenFileText, proportion=1, flag=wx.ALL, border=5)
        
        r2.Add(r2sbs1)


        r4 = wx.BoxSizer(wx.HORIZONTAL)        

        r4sb1 = wx.StaticBox(panel, label="2. Input type")
        r4sbs1 = wx.StaticBoxSizer(r4sb1, wx.VERTICAL)

        self.adultRadioButton = wx.RadioButton(panel, label="Adult", style=wx.RB_GROUP)
        self.adultRadioButton.SetValue(True)
        self.childRadioButton = wx.RadioButton(panel, label="Child")
        self.neonatalRadioButton = wx.RadioButton(panel, label="Neonatal")
        self.hceCheckBox = wx.CheckBox(panel, label="HCE variables")
        self.hceCheckBox.SetValue(True)
        
        r4sbs1.Add(self.adultRadioButton, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.Add(self.childRadioButton, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.Add(self.neonatalRadioButton, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.AddSpacer(10) 
        r4sbs1.Add(self.hceCheckBox, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.AddSpacer(3)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.clickAdultButton, id=self.adultRadioButton.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.clickChildButton, id=self.childRadioButton.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.clickNeonatalButton, id=self.neonatalRadioButton.GetId())
        self.Bind(wx.EVT_CHECKBOX, self.clickHCE, id=self.hceCheckBox.GetId())

        r4sb2 = wx.StaticBox(panel, label="3. Algorithm type",)
        r4sbs2 = wx.StaticBoxSizer(r4sb2, wx.VERTICAL)

        self.randomForestRadioButton = wx.RadioButton(panel, label="Random forest", style=wx.RB_GROUP)
        self.randomForestRadioButton.SetValue(True)
        self.tariffRadioButton = wx.RadioButton(panel, label="Tariff (future feature)")
        self.tariffRadioButton.Enable(False)

        r4sbs2.Add(self.randomForestRadioButton, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs2.Add(self.tariffRadioButton, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs2.AddSpacer(4)

        r4.Add(r4sbs1,proportion=1,flag=wx.RIGHT, border=10)
        r4.Add(r4sbs2,proportion=1,flag=wx.RIGHT, border=10)


        r5 = wx.BoxSizer(wx.HORIZONTAL)

        r5sb1 = wx.StaticBox(panel, label="4. Output folder")
        r5sbs1 = wx.StaticBoxSizer(r5sb1, wx.HORIZONTAL)

        chooseFolderButton = wx.Button(panel, label="Choose folder...")
        chooseFolderButton.Bind(wx.EVT_BUTTON, self.onOpenFolder)
        r5sbs1.Add(chooseFolderButton, flag=wx.ALL, border=5)

        self.choosenFolderText = wx.StaticText(panel, label="",size=(349, -1))
        r5sbs1.Add(self.choosenFolderText, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        
        r5.Add(r5sbs1)


        r6 = wx.BoxSizer(wx.HORIZONTAL)

        r6sb1 = wx.StaticBox(panel, label="5. Analysis status")
        r6sbs1 = wx.StaticBoxSizer(r6sb1, wx.VERTICAL)
        
        self.statusTextCtrl = wx.TextCtrl(panel,size=(475, 150),style=wx.TE_MULTILINE|wx.TE_CENTER)
        self.statusTextCtrl.SetEditable(False)
        self.statusTextCtrl.SetValue(self.statusLog)

        r6sbs1.Add(self.statusTextCtrl,flag=wx.ALL,border=5)
        r6sbs1.AddSpacer(5)

        self.statusGauge = wx.Gauge(panel,range=100,size=(472, -1))
        r6sbs1.Add(self.statusGauge,flag=wx.RIGHT|wx.LEFT, border=7)
        r6sbs1.AddSpacer(10)

        self.actionButton = wx.Button(panel, label="Start")
        self.actionButton.Bind(wx.EVT_BUTTON, self.onAction)


        r6sbs1.Add(self.actionButton,flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=5)

        r6.Add(r6sbs1)

        vbox.Add(r0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(r1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add(r2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r6, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        panel.SetSizer(vbox)

    def shortenPath(self,path, maxLength):
        pathLength = 0
        pathLengthMax = maxLength
        shortenedPathList = []
        
        # split path into list
        splitPathList = path.split(os.path.sep) 
        
        # start from end and iterate through each path element,
        for pathItem in reversed(splitPathList):
            # sum the lenth of the path so far
            pathLength += len(pathItem)
            # if less than max
            if pathLength <= pathLengthMax:
                # create shorted path
                shortenedPathList.append(pathItem)
            else:
                # no need to go through the loop
                break
        
        # reverse the shortened path, convert to a string
        shortenedPathList.reverse()
        shortenedPath = os.path.sep.join(shortenedPathList)
        # for shorter path, add ...
        if (not shortenedPath.startswith(os.path.sep)):
            return ".." + os.path.sep + shortenedPath 
        else:
            return shortenedPath

    def onOpenFile(self, e):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard="*.*",
            style=wx.OPEN | wx.CHANGE_DIR
            )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.inputFilePath = dlg.GetPath()
            print "You chose the following file: " + self.inputFilePath
            self.choosenFileText.SetLabel(self.shortenPath(self.inputFilePath,45))

        dlg.Destroy()
    
    def onOpenFolder(self, e):
        """
        Create and show the Open DirDialog
        """
        dlg = wx.DirDialog(
            self, message="Choose a folder",
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.outputFolderPath = dlg.GetPath()
            print "You chose the following folder: " + self.outputFolderPath
            self.choosenFolderText.SetLabel(self.shortenPath(self.outputFolderPath,45))

        dlg.Destroy()
    
    def onAction(self, e):
        if(self.actionButton.GetLabel() == "Start"):
            #self.statusGauge.SetValue(20)
            
            # make sure something is selected
            if self.inputFilePath:
                self.actionButton.SetLabel("Stop")
                self.addText("You selected the option " + self.selectedButton + "\n")
                print "You selected the option " + self.selectedButton
                self.running = True
                self.worker = workerthread.WorkerThread(self, self.inputFilePath, self.hce, self.selectedButton)
            else:
                print "error, no file selected. make a popup"
                          	
        elif (self.actionButton.GetLabel() == "Stop"):
            self.actionButton.SetLabel("Start")
            self.statusGauge.SetValue(0)
            self.OnAbort()
            
    def clickAdultButton(self, event):
        self.selectedButton = "Adult"
    
    def clickChildButton(self, event):
        self.selectedButton = "Child"
    
    def clickNeonatalButton(self, event):
        self.selectedButton = "Neonate"
    
    def clickHCE(self, event):
        # just a toggle
        if self.hce is 'HCE':
            self.hce = None
        else:
            self.hce = "HCE"
        
    def addText(self, newText):
        self.statusTextCtrl.AppendText(newText)
        #self.statusTextCtrl.Refresh()
        
  

    def onQuit(self, e):
        #todo:  are you sure?
        self.Close()
        
    def OnResult(self, event):
        if event.data is None:
            self.statusTextCtrl.AppendText("computation successfully aborted\n")
            self.actionButton.Enable(True)        
            self.running = False    
        else :
            print "got an update... " + event.data
            self.statusTextCtrl.AppendText(event.data)
            #TODO.  Need a "done" event
    
    def OnProgress(self, event):
        if event.progress is None:
            self.statusGauge.Pulse()
        else:    
            self.statusGauge.SetRange(event.progressmax)
            self.statusGauge.SetValue(event.progress)
        
    def OnAbort(self):
        if self.worker:
            self.statusTextCtrl.AppendText("attempting to cancel, please wait...\n")
            print "trying to cancel, please wait"
            self.worker.abort()
            self.actionButton.Enable(False)
        else:
            print "no worker?"
        
        
  

if __name__ == '__main__':
  
    app = wx.App()
    vaUI(None, title='SmartVA by IHME')
    app.MainLoop()