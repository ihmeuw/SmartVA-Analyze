#!/opt/local/bin/python

import os
import wx
import wx.html
import workerthread
import config

# TODO: pull out all strings
# TODO: why is the first button selected
# TODO: disable buttons when app is running

APP_EXIT = 1
APP_HELP = 2

APP_TITLE = "SmartVA"

class vaHelp(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=APP_TITLE + " Help", size=(600,600))
        html = wxHTML(self)
        html.SetStandardFonts()
        helpfile = 'res' +  str(os.path.sep) + 'help.html'
        html.LoadPage(os.path.join(config.basedir, helpfile))
 
class wxHTML(wx.html.HtmlWindow):
     
     def OnLinkClicked(self, link):
        LaunchDefaultBrowser(link.GetHref())
    
class vaUI(wx.Frame):

    def __init__(self, parent, title):
        super(vaUI, self).__init__(parent, title=title, 
            size=(550, 650),style=wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX)
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):

        self.inputFilePath = ""
        self.outputFolderPath = ""
        self.statusLog = ""
        self.hce = 'HCE'
        self.running = False
        self.worker = None
        self.helpWindow = None
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

        scaleSize = .35
        imageFilename = 'res' + str(os.path.sep) + 'logo.png'
        imageFile = os.path.join(config.basedir, imageFilename)
        image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
        scaled_image = image.Scale(image.GetWidth()*scaleSize, image.GetHeight()*scaleSize, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        

        r0 = wx.BoxSizer(wx.HORIZONTAL)

        r0.AddStretchSpacer()
        r0.Add(wx.StaticBitmap(self.parentPanel,-1,scaled_image),flag=wx.RIGHT, border=12)
        r0.AddStretchSpacer()


        r1 = wx.BoxSizer(wx.HORIZONTAL)

        helpButton = wx.Button(self.parentPanel, label="Help")
        quitButton = wx.Button(self.parentPanel, label="Quit")

        helpButton.Bind(wx.EVT_BUTTON, self.onHelp)
        quitButton.Bind(wx.EVT_BUTTON, self.onQuit)

        r1.AddStretchSpacer()
        r1.Add(helpButton, flag=wx.RIGHT, border=12)
        r1.Add(quitButton, flag=wx.RIGHT, border=12)

        r2 = wx.BoxSizer(wx.HORIZONTAL)
        r2sb1 = wx.StaticBox(self.parentPanel, label="1. Choose input file")
        r2sbs1 = wx.StaticBoxSizer(r2sb1, wx.HORIZONTAL)

        self.chooseFileButton = wx.Button(self.parentPanel, label="Choose file...")
        self.chooseFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.choosenFileText = wx.StaticText(self.parentPanel, label="",size=(367, -1))

        r2sbs1.Add(self.chooseFileButton, flag=wx.ALL, border=5)
        r2sbs1.Add(self.choosenFileText, proportion=1, flag=wx.ALL, border=5)
        r2.Add(r2sbs1)


        r3 = wx.BoxSizer(wx.HORIZONTAL)
        r3sb1 = wx.StaticBox(self.parentPanel, label="2. Choose output folder")
        r3sbs1 = wx.StaticBoxSizer(r3sb1, wx.HORIZONTAL)

        self.chooseFolderButton = wx.Button(self.parentPanel, label="Choose folder...")
        self.chooseFolderButton.Bind(wx.EVT_BUTTON, self.onOpenFolder)
        self.choosenFolderText = wx.StaticText(self.parentPanel, label="",size=(349, -1))

        r3sbs1.Add(self.chooseFolderButton, flag=wx.ALL, border=5)
        r3sbs1.Add(self.choosenFolderText, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        r3.Add(r3sbs1)


        r4 = wx.BoxSizer(wx.HORIZONTAL)        
        r4sb1 = wx.StaticBox(self.parentPanel, label="3. Set processing options")
        r4sbs1 = wx.StaticBoxSizer(r4sb1, wx.VERTICAL)

        self.hceCheckBox = wx.CheckBox(self.parentPanel, label="HCE variables")
        self.hceCheckBox.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.clickHCE, id=self.hceCheckBox.GetId())

        r4sbs1.Add(self.hceCheckBox, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.AddSpacer(3)
        r4.Add(r4sbs1,proportion=1,flag=wx.RIGHT, border=10)

        r5 = wx.BoxSizer(wx.HORIZONTAL)
        r5sb1 = wx.StaticBox(self.parentPanel, label="4. Start analysis")
        r5sbs1 = wx.StaticBoxSizer(r5sb1, wx.VERTICAL)
        
        self.statusTextCtrl = wx.TextCtrl(self.parentPanel,size=(475, 150),style=wx.TE_MULTILINE|wx.TE_CENTER)
        self.statusTextCtrl.SetEditable(False)
        self.statusTextCtrl.SetValue(self.statusLog)
        self.statusGauge = wx.Gauge(self.parentPanel,range=100,size=(375, -1))
        self.actionButton = wx.Button(self.parentPanel, label="Start")
        self.actionButton.Bind(wx.EVT_BUTTON, self.onAction)

        r6c1 = wx.BoxSizer(wx.HORIZONTAL);
        r6c1.Add(self.statusGauge,flag=wx.LEFT, border=7)
        r6c1.AddSpacer(10)
        r6c1.Add(self.actionButton,flag=wx.LEFT, border=5)

        r5sbs1.AddSpacer(5)
        r5sbs1.Add(r6c1)
        r5sbs1.AddSpacer(5)
        r5sbs1.Add(self.statusTextCtrl,flag=wx.ALL,border=5)
        r5sbs1.AddSpacer(5)
        r5.Add(r5sbs1)

        vbox.Add(r0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(r1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(r2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(3)
        vbox.Add(r3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(3)
        vbox.Add(r4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(3)
        vbox.Add(r5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

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
            #print "You chose the following file: " + self.inputFilePath
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
            self.choosenFolderText.SetLabel(self.shortenPath(self.outputFolderPath,42))
        dlg.Destroy()
    
    def onAction(self, e):
        if(self.actionButton.GetLabel() == "Start"):            
            # Make sure you have an input and output path
            if not self.inputFilePath:
                self.ShowErrorMessage("Error!","Please select an input file.")
            elif not self.outputFolderPath:
                self.ShowErrorMessage("Error!","Please select an output folder.")
            else:
                self.actionButton.SetLabel("Stop")
                self.addText("You selected the option " + self.selectedButton + "\n")
                self.running = True
                self.worker = workerthread.WorkerThread(self, self.inputFilePath, self.hce, self.selectedButton, self.outputFolderPath)
                self.EnableUI(False)
                          	
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
        quitDialog = wx.MessageDialog(self, 'Are you sure you want to Quit?', 'Exit Application?', wx.YES_NO | wx.NO_DEFAULT)
        pressed = quitDialog.ShowModal()
        
        if pressed == wx.ID_YES:
            self.OnAbort()
            self.Close()
            if self.helpWindow:
                self.helpWindow.Close()
        # do nothing
        #elif pressed == wx.ID_NO:
        #    print "NO"
        


    def onHelp(self, e):
        self.helpWindow = vaHelp(None)
        self.helpWindow.Centre()
        self.helpWindow.Show()

    def OnResult(self, event):
        if event.data is None:
            # If it's none we got an abort
            self.statusTextCtrl.AppendText("computation successfully aborted\n")
            self.actionButton.Enable(True)        
            self.running = False   
            self.statusGauge.SetValue(0)
            self.EnableUI(True)
        elif event.data is "Done":
            # if it's done, then the algorithm is complete
            self.statusGauge.SetValue(0)
            self.statusTextCtrl.AppendText("Process Complete\n")
            self.actionButton.SetLabel("Start")
            self.EnableUI(True)
        else:
            # everything else is update status text
            self.statusTextCtrl.AppendText(event.data)
            
    
    def OnProgress(self, event):
        if event.progress is None:
            # if it's none, we have no idea how long it takes
            self.statusGauge.Pulse()
        else:    
            # everything else gives us a progress and a max
            self.statusGauge.SetRange(event.progressmax)
            self.statusGauge.SetValue(event.progress)
        
    def OnAbort(self):
        if self.worker:
            # if the thread is running, don't just stop
            self.statusTextCtrl.AppendText("attempting to cancel, please wait...\n")
            self.worker.abort()
            self.actionButton.Enable(False)
            # do we need an else?  doesn't seem like it
        
    
    def EnableUI(self, enable):
        # Turns UI elements on an doff
        self.chooseFileButton.Enable(enable)
        self.hceCheckBox.Enable(enable)
        self.chooseFolderButton.Enable(enable)
            
  

if __name__ == '__main__':
    
    windebug = 0
    if windebug is 1:    
        try:
            app = wx.App()
            app.SetAppName(APP_TITLE)
            vaUI(None, title=APP_TITLE)
            app.MainLoop()
        except Exception as ex:
            print ex
            raw_input()
    else:
        app = wx.App()
        app.SetAppName(APP_TITLE)
        vaUI(None, title=APP_TITLE)
        app.MainLoop()