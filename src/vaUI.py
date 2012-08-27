#!/opt/local/bin/python

import os
import wx
from wx import *
import pyvaPackage
from Tkinter import *
import workerthread

# TODO: pull out all strings
# TODO: why is the first button selected
# TODO: disable buttons when app is running

if getattr(sys, 'frozen', None):
     basedir = sys._MEIPASS
else:
     basedir = os.path.dirname(__file__)

APP_EXIT = 1
APP_HELP = 2

APP_TITLE = "SmartVA"

class vaHelp(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=APP_TITLE + " Help", size=(600,600))
        html = wxHTML(self)
        html.SetStandardFonts()
        html.LoadPage(os.path.join(basedir, '../res/help.html'))
 
class wxHTML(wx.html.HtmlWindow):
     
     def OnLinkClicked(self, link):
        LaunchDefaultBrowser(link.GetHref())
    
class vaUI(wx.Frame):

    def __init__(self, parent, title):
        super(vaUI, self).__init__(parent, title=title, 
            size=(550, 760),style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX)
            
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

        self.parentPanel = wx.Panel(self)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        r0 = wx.BoxSizer(wx.HORIZONTAL)
        r1 = wx.BoxSizer(wx.HORIZONTAL)

        scaleSize = .35
        imageFile = os.path.join(basedir, '../res/logo.png')
        image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
        scaled_image = image.Scale(image.GetWidth()*scaleSize, image.GetHeight()*scaleSize, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        r0.AddStretchSpacer()
        r0.Add(wx.StaticBitmap(self.parentPanel,-1,scaled_image),flag=wx.RIGHT, border=12)
        r0.AddStretchSpacer()


        r1.AddStretchSpacer()

        helpButton = wx.Button(self.parentPanel, label="Help")
        r1.Add(helpButton, flag=wx.RIGHT, border=12)
        helpButton.Bind(wx.EVT_BUTTON, self.onHelp)

        quitButton = wx.Button(self.parentPanel, label="Quit")
        r1.Add(quitButton, flag=wx.RIGHT, border=12)
        r2 = wx.BoxSizer(wx.HORIZONTAL)
        
        quitButton.Bind(wx.EVT_BUTTON, self.onQuit)

        r2sb1 = wx.StaticBox(self.parentPanel, label="1. Input file")
        r2sbs1 = wx.StaticBoxSizer(r2sb1, wx.HORIZONTAL)

        self.chooseFileButton = wx.Button(self.parentPanel, label="Choose file...")
        self.chooseFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        r2sbs1.Add(self.chooseFileButton, flag=wx.ALL, border=5)

        self.choosenFileText = wx.StaticText(self.parentPanel, label="",size=(367, -1))
        r2sbs1.Add(self.choosenFileText, proportion=1, flag=wx.ALL, border=5)
        
        r2.Add(r2sbs1)


        r4 = wx.BoxSizer(wx.HORIZONTAL)        

        r4sb1 = wx.StaticBox(self.parentPanel, label="2. Input type")
        r4sbs1 = wx.StaticBoxSizer(r4sb1, wx.VERTICAL)

        self.adultRadioButton = wx.RadioButton(self.parentPanel, label="Adult", style=wx.RB_GROUP)
        self.adultRadioButton.SetValue(True)
        self.childRadioButton = wx.RadioButton(self.parentPanel, label="Child")
        self.neonatalRadioButton = wx.RadioButton(self.parentPanel, label="Neonatal")
        self.hceCheckBox = wx.CheckBox(self.parentPanel, label="HCE variables")
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

        r4sb2 = wx.StaticBox(self.parentPanel, label="3. Algorithm type",)
        r4sbs2 = wx.StaticBoxSizer(r4sb2, wx.VERTICAL)
        r4sbs2.AddSpacer(50)

        r4.Add(r4sbs1,proportion=1,flag=wx.RIGHT, border=10)
        r4.Add(r4sbs2,proportion=1,flag=wx.RIGHT, border=10)

        # Bug in radio grouping requires two panels in OS X 10.8
        # http://trac.wxwidgets.org/ticket/14605
        self.algorithmPanel = wx.Panel(self.parentPanel, size=(200,40))
        self.algorithmPanel.SetPosition((298,243))

        self.randomForestRadioButton = wx.RadioButton(self.algorithmPanel, label='Random forest', style=wx.RB_GROUP)
        self.randomForestRadioButton.SetValue(True)
        self.tariffRadioButton = wx.RadioButton(self.algorithmPanel, label='Tariff (future feature)',pos=(-1, 22))
        self.tariffRadioButton.Enable(False)

        r5 = wx.BoxSizer(wx.HORIZONTAL)

        r5sb1 = wx.StaticBox(self.parentPanel, label="4. Output folder")
        r5sbs1 = wx.StaticBoxSizer(r5sb1, wx.HORIZONTAL)

        self.chooseFolderButton = wx.Button(self.parentPanel, label="Choose folder...")
        self.chooseFolderButton.Bind(wx.EVT_BUTTON, self.onOpenFolder)
        r5sbs1.Add(self.chooseFolderButton, flag=wx.ALL, border=5)

        self.choosenFolderText = wx.StaticText(self.parentPanel, label="",size=(349, -1))
        r5sbs1.Add(self.choosenFolderText, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        
        r5.Add(r5sbs1)


        r6 = wx.BoxSizer(wx.HORIZONTAL)

        r6sb1 = wx.StaticBox(self.parentPanel, label="5. Analysis status")
        r6sbs1 = wx.StaticBoxSizer(r6sb1, wx.VERTICAL)
        
        self.statusTextCtrl = wx.TextCtrl(self.parentPanel,size=(475, 150),style=wx.TE_MULTILINE|wx.TE_CENTER)
        self.statusTextCtrl.SetEditable(False)
        self.statusTextCtrl.SetValue(self.statusLog)

        r6sbs1.Add(self.statusTextCtrl,flag=wx.ALL,border=5)
        r6sbs1.AddSpacer(5)

        self.statusGauge = wx.Gauge(self.parentPanel,range=100,size=(472, -1))
        r6sbs1.Add(self.statusGauge,flag=wx.RIGHT|wx.LEFT, border=7)
        r6sbs1.AddSpacer(10)

        self.actionButton = wx.Button(self.parentPanel, label="Start")
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

        self.parentPanel.SetSizer(vbox)

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
            self.choosenFileText.SetLabel(self.shortenPath(self.inputFilePath,42))

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
            self.choosenFolderText.SetLabel(self.shortenPath(self.outputFolderPath,42))

        dlg.Destroy()
    
    def onAction(self, e):
        if(self.actionButton.GetLabel() == "Start"):
            #self.statusGauge.SetValue(20)
            
            # Make sure you have an input and output path
            if not self.inputFilePath:
                self.ShowErrorMessage("Error!","Please select an input file.")
            elif not self.outputFolderPath:
                self.ShowErrorMessage("Error!","Please select an output folder.")
            else:
                self.actionButton.SetLabel("Stop")
                self.addText("You selected the option " + self.selectedButton + "\n")
                print "You selected the option " + self.selectedButton
                self.running = True
                self.worker = workerthread.WorkerThread(self, self.inputFilePath, self.hce, self.selectedButton)
                #self.toggleControls(False)
                          	
        elif (self.actionButton.GetLabel() == "Stop"):
            self.actionButton.SetLabel("Start")
            self.statusGauge.SetValue(0)
            self.OnAbort()
            #self.toggleControls(True)
            
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
    
    def ShowErrorMessage(self, title, message):
        dialog = wx.MessageDialog(None, message, title, 
            wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    def toggleControls(self,enabled):
        self.chooseFileButton.Enable(enabled);

        self.adultRadioButton.Enable(enabled);
        self.childRadioButton.Enable(enabled);
        self.neonatalRadioButton.Enable(enabled);
        self.hceCheckBox.Enable(enabled);
        self.randomForestRadioButton.Enable(enabled);
        
        self.chooseFolderButton.Enable(enabled);
  
    def onQuit(self, e):
        #todo:  are you sure?
        self.Close()
        
        # is the help window open?
        if hasattr(self,'helpWindow'):
            self.helpWindow.Close()

    def onHelp(self, e):
        self.helpWindow = vaHelp(None)
        self.helpWindow.Centre()
        self.helpWindow.Show()

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
    app.SetAppName(APP_TITLE)
    vaUI(None, title=APP_TITLE)
    app.MainLoop()