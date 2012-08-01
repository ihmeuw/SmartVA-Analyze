#!/usr/bin/python

import wx

APP_EXIT = 1

class vaUI(wx.Frame):
    
    def __init__(self, parent, title):
        super(vaUI, self).__init__(parent, title=title, 
            size=(550, 750),style=wx.CAPTION)
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        qmi = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        fileMenu.AppendItem(qmi)
        menubar.Append(fileMenu, '&File')
        
        self.Bind(wx.EVT_MENU, self.OnQuit, id=APP_EXIT)
        self.SetMenuBar(menubar)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        r = wx.BoxSizer(wx.HORIZONTAL)
        r0 = wx.BoxSizer(wx.HORIZONTAL)


       
        # actually you can load .jpg  .png  .bmp  or .gif files
        scaleSize = .35
        imageFile = '../res/logo.png'
        image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
        scaled_image = image.Scale(image.GetWidth()*scaleSize, image.GetHeight()*scaleSize, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        r.AddStretchSpacer()
        r.Add(wx.StaticBitmap(panel,-1,scaled_image),flag=wx.RIGHT|wx.BOTTOM, border=12)
        r.AddStretchSpacer()


        # r0.AddStretchSpacer()
        # r0.Add(wx.Button(panel, label="Help"), flag=wx.RIGHT, border=12)
        # r0.Add(wx.Button(panel, label="Quit"), flag=wx.RIGHT, border=12)
        # r0.AddStretchSpacer()

        r1 = wx.BoxSizer(wx.HORIZONTAL)

        r1sb1 = wx.StaticBox(panel, label="1. Input file")
        r1sbs1 = wx.StaticBoxSizer(r1sb1, wx.HORIZONTAL)
        r1sbs1.Add(wx.Button(panel, label="Choose file..."), flag=wx.ALL, border=5)
        r1sbs1.Add(wx.StaticText(panel, label="/Hard Drive/User/Documents/input.csv",size=(367, -1)), proportion=1, flag=wx.ALL, border=5)
        
        r1.Add(r1sbs1)


        r2 = wx.BoxSizer(wx.HORIZONTAL)        

        r2sb1 = wx.StaticBox(panel, label="2. Input type")
        r2sbs1 = wx.StaticBoxSizer(r2sb1, wx.VERTICAL)
        r2sbs1.Add(wx.RadioButton(panel, label="Adult"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs1.Add(wx.RadioButton(panel, label="Child"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs1.Add(wx.RadioButton(panel, label="Neonatal"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs1.AddSpacer(10) 
        r2sbs1.Add(wx.CheckBox(panel, label="HCE variables"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs1.AddSpacer(3)

        r2sb2 = wx.StaticBox(panel, label="3. Algorithm type",)
        r2sbs2 = wx.StaticBoxSizer(r2sb2, wx.VERTICAL)
        r2sbs2.Add(wx.RadioButton(panel, label="Tariff"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs2.Add(wx.RadioButton(panel, label="Random forest"), flag=wx.LEFT|wx.TOP, border=5)
        r2sbs2.AddSpacer(4)

        r2.Add(r2sbs1,proportion=1,flag=wx.RIGHT, border=10)
        r2.Add(r2sbs2,proportion=1,flag=wx.RIGHT, border=10)


        r3 = wx.BoxSizer(wx.HORIZONTAL)

        r3sb1 = wx.StaticBox(panel, label="4. Output folder")
        r3sbs1 = wx.StaticBoxSizer(r3sb1, wx.HORIZONTAL)
        r3sbs1.Add(wx.Button(panel, label="Choose folder..."), flag=wx.ALL, border=5)
        r3sbs1.Add(wx.StaticText(panel, label="/Hard Drive/User/Documents",size=(348, -1)), proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        
        r3.Add(r3sbs1)


        r4 = wx.BoxSizer(wx.HORIZONTAL)

        r4sb1 = wx.StaticBox(panel, label="5. Analysis status")
        r4sbs1 = wx.StaticBoxSizer(r4sb1, wx.VERTICAL)
        r4e1 = wx.TextCtrl(panel,size=(475, 150),style=wx.TE_MULTILINE|wx.TE_CENTER)
        r4e1.SetEditable(False)
        r4e1.SetValue("Data validation complete.\n\nProcessing row 1...\nProcessing row 2...")
        r4sbs1.Add(r4e1,flag=wx.ALL,border=5)
        r4sbs1.AddSpacer(5)
        r4e2 = wx.Gauge(panel,range=100,size=(471, -1))
        r4e2.SetValue(40)
        r4sbs1.Add(r4e2,flag=wx.RIGHT|wx.LEFT, border=7)
        r4sbs1.AddSpacer(10)
        r4sbs1.Add(wx.Button(panel, label="Stop"),flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=5)

        r4.Add(r4sbs1)


#        r5 = wx.StaticText(panel, label="http://www.healthmetricsandevaluation.org", style=wx.ALIGN_RIGHT)
#        r5.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
#        hbox.Add(r5)

        vbox.Add(r,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        # vbox.Add(r0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add(r1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.AddSpacer(10)
        vbox.Add(r4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # add link to ihme
        # add imhe logo
        # add help

        panel.SetSizer(vbox)

        
    def OnQuit(self, e):
        self.Close()

if __name__ == '__main__':
  
    app = wx.App()
    vaUI(None, title='SmartVA by IHME')
    app.MainLoop()