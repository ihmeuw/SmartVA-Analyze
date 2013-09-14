#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import os
import wx
import wx.html
import workerthread
import config
import re

# TODO: pull out all strings
# TODO: why is the first button selected
# TODO: disable buttons when app is running

APP_EXIT = 1
APP_HELP = 2

APP_TITLE = 'SmartVA'

COUNTRY_DEFAULT = u'Unknown'
COUNTRIES = [COUNTRY_DEFAULT,u'Afghanistan (AFG)',u'Åland Islands (ALA)',u'Albania (ALB)',u'Algeria (DZA)',u'American Samoa (ASM)',u'Andorra (AND)',u'Angola (AGO)',u'Anguilla (AIA)',u'Antarctica (ATA)',u'Antigua and Barbuda (ATG)',u'Argentina (ARG)',u'Armenia (ARM)',u'Aruba (ABW)',u'Australia (AUS)',u'Austria (AUT)',u'Azerbaijan (AZE)',u'Bahamas (BHS)',u'Bahrain (BHR)',u'Bangladesh (BGD)',u'Barbados (BRB)',u'Belarus (BLR)',u'Belgium (BEL)',u'Belize (BLZ)',u'Benin (BEN)',u'Bermuda (BMU)',u'Bhutan (BTN)',u'Bolivia, Plurinational State of (BOL)',u'Bosnia and Herzegovina (BIH)',u'Botswana (BWA)',u'Bouvet Island (BVT)',u'Brazil (BRA)',u'British Indian Ocean Territory (IOT)',u'Brunei Darussalam (BRN)',u'Bulgaria (BGR)',u'Burkina Faso (BFA)',u'Burundi (BDI)',u'Cambodia (KHM)',u'Cameroon (CMR)',u'Canada (CAN)',u'Cape Verde (CPV)',u'Cayman Islands (CYM)',u'Central African Republic (CAF)',u'Chad (TCD)',u'Chile (CHL)',u'China (CHN)',u'Christmas Island (CXR)',u'Cocos (Keeling) Islands (CCK)',u'Colombia (COL)',u'Comoros (COM)',u'Congo (COG)',u'Congo, the Democratic Republic of the (COD)',u'Cook Islands (COK)',u'Costa Rica (CRI)',u'Côte d\'Ivoire (CIV)',u'Croatia (HRV)',u'Cuba (CUB)',u'Cyprus (CYP)',u'Czech Republic (CZE)',u'Denmark (DNK)',u'Djibouti (DJI)',u'Dominica (DMA)',u'Dominican Republic (DOM)',u'Ecuador (ECU)',u'Egypt (EGY)',u'El Salvador (SLV)',u'Equatorial Guinea (GNQ)',u'Eritrea (ERI)',u'Estonia (EST)',u'Ethiopia (ETH)',u'Falkland Islands (Malvinas) (FLK)',u'Faroe Islands (FRO)',u'Fiji (FJI)',u'Finland (FIN)',u'France (FRA)',u'French Guiana (GUF)',u'French Polynesia (PYF)',u'French Southern Territories (ATF)',u'Gabon (GAB)',u'Gambia (GMB)',u'Georgia (GEO)',u'Germany (DEU)',u'Ghana (GHA)',u'Gibraltar (GIB)',u'Greece (GRC)',u'Greenland (GRL)',u'Grenada (GRD)',u'Guadeloupe (GLP)',u'Guam (GUM)',u'Guatemala (GTM)',u'Guernsey (GGY)',u'Guinea (GIN)',u'Guinea-Bissau (GNB)',u'Guyana (GUY)',u'Haiti (HTI)',u'Heard Island and McDonald Islands (HMD)',u'Holy See (Vatican City State) (VAT)',u'Honduras (HND)',u'Hong Kong (HKG)',u'Hungary (HUN)',u'Iceland (ISL)',u'India (IND)',u'Indonesia (IDN)',u'Iran, Islamic Republic of (IRN)',u'Iraq (IRQ)',u'Ireland (IRL)',u'Isle of Man (IMN)',u'Israel (ISR)',u'Italy (ITA)',u'Jamaica (JAM)',u'Japan (JPN)',u'Jersey (JEY)',u'Jordan (JOR)',u'Kazakhstan (KAZ)',u'Kenya (KEN)',u'Kiribati (KIR)',u'Korea, Democratic People\'s Republic of (PRK)',u'Korea, Republic of (KOR)',u'Kuwait (KWT)',u'Kyrgyzstan (KGZ)',u'Lao People\'s Democratic Republic (LAO)',u'Latvia (LVA)',u'Lebanon (LBN)',u'Lesotho (LSO)',u'Liberia (LBR)',u'Libyan Arab Jamahiriya (LBY)',u'Liechtenstein (LIE)',u'Lithuania (LTU)',u'Luxembourg (LUX)',u'Macao (MAC)',u'Macedonia, the former Yugoslav Republic of (MKD)',u'Madagascar (MDG)',u'Malawi (MWI)',u'Malaysia (MYS)',u'Maldives (MDV)',u'Mali (MLI)',u'Malta (MLT)',u'Marshall Islands (MHL)',u'Martinique (MTQ)',u'Mauritania (MRT)',u'Mauritius (MUS)',u'Mayotte (MYT)',u'Mexico (MEX)',u'Micronesia, Federated States of (FSM)',u'Moldova, Republic of (MDA)',u'Monaco (MCO)',u'Mongolia (MNG)',u'Montenegro (MNE)',u'Montserrat (MSR)',u'Morocco (MAR)',u'Mozambique (MOZ)',u'Myanmar (MMR)',u'Namibia (NAM)',u'Nauru (NRU)',u'Nepal (NPL)',u'Netherlands (NLD)',u'Netherlands Antilles (ANT)',u'New Caledonia (NCL)',u'New Zealand (NZL)',u'Nicaragua (NIC)',u'Niger (NER)',u'Nigeria (NGA)',u'Niue (NIU)',u'Norfolk Island (NFK)',u'Northern Mariana Islands (MNP)',u'Norway (NOR)',u'Oman (OMN)',u'Pakistan (PAK)',u'Palau (PLW)',u'Palestinian Territory, Occupied (PSE)',u'Panama (PAN)',u'Papua New Guinea (PNG)',u'Paraguay (PRY)',u'Peru (PER)',u'Philippines (PHL)',u'Pitcairn (PCN)',u'Poland (POL)',u'Portugal (PRT)',u'Puerto Rico (PRI)',u'Qatar (QAT)',u'Réunion (REU)',u'Romania (ROU)',u'Russian Federation (RUS)',u'Rwanda (RWA)',u'Saint Barthélemy (BLM)',u'Saint Helena, Ascension and Tristan da Cunha (SHN)',u'Saint Kitts and Nevis (KNA)',u'Saint Lucia (LCA)',u'Saint Martin (French part) (MAF)',u'Saint Pierre and Miquelon (SPM)',u'Saint Vincent and the Grenadines (VCT)',u'Samoa (WSM)',u'San Marino (SMR)',u'Sao Tome and Principe (STP)',u'Saudi Arabia (SAU)',u'Senegal (SEN)',u'Serbia (SRB)',u'Seychelles (SYC)',u'Sierra Leone (SLE)',u'Singapore (SGP)',u'Slovakia (SVK)',u'Slovenia (SVN)',u'Solomon Islands (SLB)',u'Somalia (SOM)',u'South Africa (ZAF)',u'South Georgia and the South Sandwich Islands (SGS)',u'Spain (ESP)',u'Sri Lanka (LKA)',u'Sudan (SDN)',u'Suriname (SUR)',u'Svalbard and Jan Mayen (SJM)',u'Swaziland (SWZ)',u'Sweden (SWE)',u'Switzerland (CHE)',u'Syrian Arab Republic (SYR)',u'Taiwan, Province of China (TWN)',u'Tajikistan (TJK)',u'Tanzania, United Republic of (TZA)',u'Thailand (THA)',u'Timor-Leste (TLS)',u'Togo (TGO)',u'Tokelau (TKL)',u'Tonga (TON)',u'Trinidad and Tobago (TTO)',u'Tunisia (TUN)',u'Turkey (TUR)',u'Turkmenistan (TKM)',u'Turks and Caicos Islands (TCA)',u'Tuvalu (TUV)',u'Uganda (UGA)',u'Ukraine (UKR)',u'United Arab Emirates (ARE)',u'United Kingdom (GBR)',u'United States (USA)',u'United States Minor Outlying Islands (UMI)',u'Uruguay (URY)',u'Uzbekistan (UZB)',u'Vanuatu (VUT)',u'Venezuela, Bolivarian Republic of (VEN)',u'Viet Nam (VNM)',u'Virgin Islands, British (VGB)',u'Virgin Islands, U.S. (VIR)',u'Wallis and Futuna (WLF)',u'Western Sahara (ESH)',u'Yemen (YEM)',u'Zambia (ZMB)',u'Zimbabwe (ZWE)']

class vaHelp(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=APP_TITLE + ' Help', size=(600,600))
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
        
        #TODO: make both of these empty when done
        #self.inputFilePath = '/Users/carlhartung/Desktop/runva/before.csv'
        #self.outputFolderPath = '/Users/carlhartung/Desktop/runva'
        self.inputFilePath = ''
        self.outputFolderPath = ''
        self.statusLog = ''
        self.hce = 'hce'
        self.freetext = 'freetext'
        self.country = None
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

        helpButton = wx.Button(self.parentPanel, label='Help')
        quitButton = wx.Button(self.parentPanel, label='Quit')

        helpButton.Bind(wx.EVT_BUTTON, self.onHelp)
        quitButton.Bind(wx.EVT_BUTTON, self.onQuit)

        r1.AddStretchSpacer()
        r1.Add(helpButton, flag=wx.RIGHT, border=12)
        r1.Add(quitButton, flag=wx.RIGHT, border=12)

        r2 = wx.BoxSizer(wx.HORIZONTAL)
        r2sb1 = wx.StaticBox(self.parentPanel, label='1. Choose input file')
        r2sbs1 = wx.StaticBoxSizer(r2sb1, wx.HORIZONTAL)

        self.chooseFileButton = wx.Button(self.parentPanel, label='Choose file...')
        self.chooseFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.choosenFileText = wx.StaticText(self.parentPanel, label='',size=(367, -1))

        r2sbs1.Add(self.chooseFileButton, flag=wx.ALL, border=5)
        r2sbs1.Add(self.choosenFileText, proportion=1, flag=wx.ALL, border=5)
        r2.Add(r2sbs1)

        r3 = wx.BoxSizer(wx.HORIZONTAL)
        r3sb1 = wx.StaticBox(self.parentPanel, label='2. Choose output folder')
        r3sbs1 = wx.StaticBoxSizer(r3sb1, wx.HORIZONTAL)

        self.chooseFolderButton = wx.Button(self.parentPanel, label='Choose folder...')
        self.chooseFolderButton.Bind(wx.EVT_BUTTON, self.onOpenFolder)
        self.choosenFolderText = wx.StaticText(self.parentPanel, label='',size=(349, -1))

        r3sbs1.Add(self.chooseFolderButton, flag=wx.ALL, border=5)
        r3sbs1.Add(self.choosenFolderText, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        r3.Add(r3sbs1)

        r4 = wx.BoxSizer(wx.HORIZONTAL)        
        r4sb1 = wx.StaticBox(self.parentPanel, label='3. Set processing options')
        r4sbs1 = wx.StaticBoxSizer(r4sb1, wx.VERTICAL)

        self.countryLabel = wx.StaticText(self.parentPanel, label='Country where data collected')
        self.countryComboBox = wx.ComboBox(self.parentPanel, choices=COUNTRIES, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.changeCountry)

        r4bs2 = wx.BoxSizer(wx.HORIZONTAL)
        r4bs2.Add(self.countryLabel,flag=wx.TOP|wx.RIGHT,border=5)
        r4bs2.Add(self.countryComboBox)

        self.hceCheckBox = wx.CheckBox(self.parentPanel, label='Include Health Care Experience (HCE) variables')
        self.hceCheckBox.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.toggleHCE, id=self.hceCheckBox.GetId())

        self.freetextCheckBox = wx.CheckBox(self.parentPanel, label='Include free text variables')
        self.freetextCheckBox.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.toggleFreetext, id=self.freetextCheckBox.GetId())

        r4sbs1.Add(r4bs2)
        r4sbs1.AddSpacer(5)
        r4sbs1.Add(self.hceCheckBox, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.AddSpacer(3)
        r4sbs1.Add(self.freetextCheckBox, flag=wx.LEFT|wx.TOP, border=5)
        r4sbs1.AddSpacer(3)

        r4.Add(r4sbs1,proportion=1,flag=wx.RIGHT, border=10)

        r5 = wx.BoxSizer(wx.HORIZONTAL)
        r5sb1 = wx.StaticBox(self.parentPanel, label='4. Start analysis')
        r5sbs1 = wx.StaticBoxSizer(r5sb1, wx.VERTICAL)
        
        self.statusTextCtrl = wx.TextCtrl(self.parentPanel,size=(475, 150),style=wx.TE_MULTILINE|wx.TE_LEFT)
        self.statusTextCtrl.SetEditable(False)
        self.statusTextCtrl.SetValue(self.statusLog)
        self.statusGauge = wx.Gauge(self.parentPanel,range=100,size=(375, -1))
        self.actionButton = wx.Button(self.parentPanel, label='Start')
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
            return '..' + os.path.sep + shortenedPath 
        else:
            return shortenedPath

    def onOpenFile(self, e):
        '''
        Create and show the Open FileDialog
        '''
        dlg = wx.FileDialog(
            self, message='Choose a file',
            defaultFile='',
            wildcard='*.*',
            style=wx.OPEN | wx.CHANGE_DIR
            )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.inputFilePath = dlg.GetPath()
            #print 'You chose the following file: ' + self.inputFilePath
            self.choosenFileText.SetLabel(self.shortenPath(self.inputFilePath,42))
        dlg.Destroy()
    
    def onOpenFolder(self, e):
        '''
        Create and show the Open DirDialog
        '''
        dlg = wx.DirDialog(
            self, message='Choose a folder',
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.outputFolderPath = dlg.GetPath()
            self.choosenFolderText.SetLabel(self.shortenPath(self.outputFolderPath,42))
        dlg.Destroy()
    
    def onAction(self, e):
        if(self.actionButton.GetLabel() == 'Start'):            
            # Make sure you have an input and output path
            if not self.inputFilePath:
                self.ShowErrorMessage('Error!','Please select an input file.')
            elif not self.outputFolderPath:
                self.ShowErrorMessage('Error!','Please select an output folder.')
            else:
                self.actionButton.SetLabel('Stop')
                self.statusGauge.Pulse()
                self.running = True
                self.worker = workerthread.WorkerThread(self, self.inputFilePath, self.hce, self.outputFolderPath, self.freetext)
                self.EnableUI(False)
                          	
        elif (self.actionButton.GetLabel() == 'Stop'):
            self.actionButton.SetLabel('Start')
            self.statusGauge.SetValue(0)
            self.OnAbort()
    
    def toggleHCE(self, event):
        # just a toggle
        if self.hce is 'hce':
            self.hce = None
        else:
            self.hce = 'hce'
    
    def toggleFreetext(self, event):
        # just a toggle
        if self.freetext is 'freetext':
            self.freetext = None
        else:
            self.freetext = 'freetext'

    def changeCountry(self,event):
        if (event.GetString() != COUNTRY_DEFAULT):
            match = re.search('\(([A-Z]{3})\)$',event.GetString())
            self.country = match.group(1)
        else:
            self.country = None

    def addText(self, newText):
        self.statusTextCtrl.AppendText(newText)
    
    def ShowErrorMessage(self, title, message):
        dialog = wx.MessageDialog(None, message, title, 
            wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    def toggleControls(self,enabled):
        self.chooseFileButton.Enable(enabled);
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
        #    print 'NO'

    def onHelp(self, e):
        self.helpWindow = vaHelp(None)
        self.helpWindow.Centre()
        self.helpWindow.Show()

    def OnResult(self, event):
        if event.data is None:
            # If it's none we got an abort
            self.statusTextCtrl.AppendText('computation successfully aborted\n')
            self.actionButton.Enable(True)        
            self.running = False   
            self.statusGauge.SetValue(0)
            self.EnableUI(True)
        elif event.data is 'Done':
            # if it's done, then the algorithm is complete
            self.statusGauge.SetValue(0)
            self.statusTextCtrl.AppendText('Process Complete\n')
            self.actionButton.SetLabel('Start')
            self.EnableUI(True)
        else:
            # everything else is update status text
            self.statusTextCtrl.AppendText(event.data)

    def OnProgress(self, event):
        self.statusGauge.Pulse()
        
    def OnAbort(self):
        if self.worker:
            # if the thread is running, don't just stop
            self.statusTextCtrl.AppendText('attempting to cancel, please wait...\n')
            self.worker.abort()
            self.actionButton.Enable(False)
            # do we need an else?  doesn't seem like it
    
    def EnableUI(self, enable):
        # Turns UI elements on and off
        self.chooseFileButton.Enable(enable)
        self.chooseFolderButton.Enable(enable)
        self.countryComboBox.Enable(enable)
        self.hceCheckBox.Enable(enable)
        self.freetextCheckBox.Enable(enable)
  

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