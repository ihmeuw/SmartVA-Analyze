# coding=utf-8

import io
import logging
import re
import os
import platform
import threading

import wx
import wx.html

from smartva import config
from smartva import prog_name
from smartva import utils
from smartva import workerthread
from smartva.countries import COUNTRY_DEFAULT, COUNTRIES
from smartva.gui.prompting_combo_box import PromptingComboBox
from smartva.loggers import status_logger


# TODO: pull out all strings
# TODO: why is the first button selected

APP_QUIT = wx.ID_EXIT
APP_ABOUT = wx.ID_ABOUT
APP_DOCS = wx.NewId()
OPT_HCE = wx.NewId()
OPT_FREE_TEXT = wx.NewId()

APP_TITLE = prog_name

MAX_PATH_LENGTH = 55

WINDOW_WIDTH = 560
WINDOW_HEIGHT = 690

# OS dependant configuration.
if platform.system().lower() == 'windows':
    # Windows uses \r\n
    LINE_DELIM_LEN = 2
else:
    # Everyone else uses \n
    LINE_DELIM_LEN = 1

COMBO_BOX_STYLE = wx.CB_DROPDOWN
if platform.system().lower() != 'darwin':
    # Mac does not support sort style
    COMBO_BOX_STYLE |= wx.CB_SORT


class TextEntryStream(io.TextIOBase):
    def __init__(self, text_entry_widget):
        """
        The TextEntryStream will write to any widget that extends the `TextEntryBase` class or implements the
        `AppendText(str)` method.
        :type text_entry_widget: wx.TextCtrl
        """
        io.TextIOBase.__init__(self)
        self._text_entry = text_entry_widget

    def readable(self):
        return False

    def seekable(self):
        return False

    def write(self, msg):
        wx.CallAfter(self._write, msg)

    def _write(self, msg):
        # If processing, overwrite previous line.
        # TODO - Figure out if this is the appropriate way to overwrite a line. It seems convoluted.
        if re.match(r'(Adult|Child|Neonate) :: Processing \d+', msg):
            last_line = self._text_entry.GetLineText(long(self._text_entry.GetNumberOfLines() - 2))
            if re.match(r'(Adult|Child|Neonate) :: Processing \d+', last_line):
                # replace
                position = self._text_entry.GetLastPosition()
                self._text_entry.Replace(position - len(last_line) - LINE_DELIM_LEN, position, msg)
            else:
                self._text_entry.AppendText(msg)
        else:
            self._text_entry.AppendText(msg)

    def flush(self):
        pass


class vaAbout(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title='About ' + APP_TITLE, size=(400, 500))
        html = wxHTML(self)
        html.SetStandardFonts()
        about = 'res' + str(os.path.sep) + 'about.html'
        html.LoadPage(os.path.join(config.basedir, about))


class vaDocs(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=APP_TITLE + ' Documentation', size=(400, 500))
        html = wxHTML(self)
        html.SetStandardFonts()
        about = 'res' + str(os.path.sep) + 'documentation.htm'
        html.LoadPage(os.path.join(config.basedir, about))


class wxHTML(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


class vaUI(wx.Frame):
    def __init__(self, parent, title):
        super(vaUI, self).__init__(parent, title=title, size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                                   style=(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU |
                                          wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.CLIP_CHILDREN))

        self.input_file_path = ''
        self.output_folder_path = ''
        self.hce = True
        self.free_text = True
        self.malaria = True
        self.country = None
        self.running = False
        self.worker = None
        self.docs_window = None
        self.about_window = None

        self.enabled_widgets = []

        self.chosen_file_text = None
        self.chosen_folder_text = None

        self.status_gauge = None
        self.action_button = None

        self._init_menu_bar()
        self._init_ui()

        self.Center()
        self.Show()

    def _init_menu_bar(self):
        menu_bar = wx.MenuBar()
        self.SetMenuBar(menu_bar)

        # File Menu
        file_menu = wx.Menu()
        menu_bar.Append(file_menu, title='&File')

        quit_menu_item = wx.MenuItem(file_menu, id=APP_QUIT, text='&Quit\tCtrl+Q')
        self.Bind(wx.EVT_MENU, handler=self.on_quit, id=quit_menu_item.GetId())
        file_menu.AppendItem(quit_menu_item)

        # Help Menu
        help_menu = wx.Menu()
        menu_bar.Append(help_menu, title='&About')

        about_menu_item = wx.MenuItem(help_menu, id=APP_ABOUT, text='&About ' + APP_TITLE)
        self.Bind(wx.EVT_MENU, handler=self.on_about, id=about_menu_item.GetId())
        help_menu.AppendItem(about_menu_item)

        docs_menu_item = wx.MenuItem(help_menu, id=APP_DOCS, text='&Documentation')
        self.Bind(wx.EVT_MENU, handler=self.on_docs, id=docs_menu_item.GetId())
        help_menu.AppendItem(docs_menu_item)

        # Options Menu
        options_menu = wx.Menu()
        menu_bar.Append(options_menu, title='&Options')

        hce_menu_item = wx.MenuItem(options_menu, id=OPT_HCE, text='Use &Health Care Experience (HCE) variables',
                                    kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_hce, id=hce_menu_item.GetId())
        options_menu.AppendItem(hce_menu_item)
        hce_menu_item.Check(check=self.hce)
        self.enabled_widgets.append(hce_menu_item)

        free_text_menu_item = wx.MenuItem(options_menu, id=OPT_FREE_TEXT, text='Use &Free text variables',
                                          kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_free_text, id=free_text_menu_item.GetId())
        options_menu.AppendItem(free_text_menu_item)
        free_text_menu_item.Check(self.free_text)
        self.enabled_widgets.append(free_text_menu_item)

    def _init_ui(self):
        self.Bind(wx.EVT_CLOSE, self.on_quit)

        parent_panel = wx.ScrolledWindow(self)
        parent_panel.SetScrollbars(1, 1, 1, 1)

        parent_box_sizer = wx.BoxSizer(wx.VERTICAL)

        # logo
        scale_size = .35
        logo_file_path = os.path.join(config.basedir, 'res' + str(os.path.sep) + 'logo.png')
        logo = wx.Image(logo_file_path, wx.BITMAP_TYPE_ANY)
        scaled_image = logo.Scale(logo.GetWidth() * scale_size, logo.GetHeight() * scale_size,
                                  wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()

        logo_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        logo_box_sizer.AddStretchSpacer()
        logo_box_sizer.Add(wx.StaticBitmap(parent_panel, -1, scaled_image), flag=wx.RIGHT, border=12)
        logo_box_sizer.AddStretchSpacer()

        # choose input file
        choose_input_static_box = wx.StaticBox(parent_panel, label='1. Choose input file')
        choose_input_static_box_sizer = wx.StaticBoxSizer(choose_input_static_box, wx.HORIZONTAL)

        choose_file_button = wx.Button(parent_panel, label='Choose file...')
        choose_file_button.Bind(wx.EVT_BUTTON, self.on_open_file)
        self.chosen_file_text = wx.StaticText(parent_panel, label='', size=(-1, -1))
        self.enabled_widgets.append(choose_file_button)

        choose_file_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        choose_file_box_sizer.Add(choose_file_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=0)
        choose_file_box_sizer.Add(self.chosen_file_text, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                  border=5)

        choose_input_static_box_sizer.Add(choose_file_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        # choose output folder
        choose_output_static_box = wx.StaticBox(parent_panel, label='2. Choose output folder')
        choose_output_static_box_sizer = wx.StaticBoxSizer(choose_output_static_box, wx.HORIZONTAL)

        choose_folder_button = wx.Button(parent_panel, label='Choose folder...')
        choose_folder_button.Bind(wx.EVT_BUTTON, self.on_open_folder)
        self.chosen_folder_text = wx.StaticText(parent_panel, label='', size=(-1, -1))
        self.enabled_widgets.append(choose_folder_button)

        choose_folder_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        choose_folder_box_sizer.Add(choose_folder_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=0)
        choose_folder_box_sizer.Add(self.chosen_folder_text, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                    border=5)

        choose_output_static_box_sizer.Add(choose_folder_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        # set processing options
        set_options_static_box = wx.StaticBox(parent_panel, label='3. Choose geography')
        set_options_static_box_sizer = wx.StaticBoxSizer(set_options_static_box, wx.VERTICAL)

        country_label = wx.StaticText(parent_panel, label='Data origin (country)')
        country_combo_box = PromptingComboBox(parent_panel, value=COUNTRY_DEFAULT, choices=COUNTRIES, style=COMBO_BOX_STYLE)
        self.Bind(wx.EVT_COMBOBOX, handler=self.change_country, id=country_combo_box.GetId())
        self.enabled_widgets.append(country_combo_box)

        country_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        country_box_sizer.Add(country_label, flag=wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        country_box_sizer.Add(country_combo_box)

        malaria_check_box = wx.CheckBox(parent_panel, label='Malaria region')
        malaria_check_box.SetValue(self.malaria)
        self.Bind(wx.EVT_CHECKBOX, self.toggle_malaria, id=malaria_check_box.GetId())
        self.enabled_widgets.append(malaria_check_box)

        set_options_static_box_sizer.Add(country_box_sizer)
        set_options_static_box_sizer.AddSpacer(5)
        set_options_static_box_sizer.Add(malaria_check_box, flag=wx.LEFT | wx.TOP, border=5)
        set_options_static_box_sizer.AddSpacer(3)

        # start analysis
        start_analysis_box = wx.StaticBox(parent_panel, label='4. Start analysis')
        start_analysis_box_sizer = wx.StaticBoxSizer(start_analysis_box, wx.VERTICAL)

        # Define the status text control widget.
        status_text_ctrl = wx.TextCtrl(parent_panel, size=(-1, 200), style=wx.TE_MULTILINE | wx.TE_LEFT)
        status_text_ctrl.SetEditable(False)
        status_text_ctrl.SetValue('')

        # Send INFO level log messages to the status text control widget
        gui_log_handler = logging.StreamHandler(TextEntryStream(status_text_ctrl))
        gui_log_handler.setLevel(logging.INFO)
        status_logger.addHandler(gui_log_handler)

        self.status_gauge = wx.Gauge(parent_panel, range=100, size=(-1, -1))
        self.action_button = wx.Button(parent_panel, label='Start')
        self.action_button.Bind(wx.EVT_BUTTON, self.on_action)

        status_gauge_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_gauge_box_sizer.Add(self.status_gauge, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        status_gauge_box_sizer.Add(self.action_button, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        start_analysis_box_sizer.Add(status_gauge_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        start_analysis_box_sizer.Add(status_text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # build ui
        parent_box_sizer.Add(logo_box_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        parent_box_sizer.Add(choose_input_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        parent_box_sizer.Add(choose_output_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        parent_box_sizer.Add(set_options_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        parent_box_sizer.Add(start_analysis_box_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        parent_panel.SetSizer(parent_box_sizer)

    def on_open_file(self, event):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message='Choose a file',
            defaultFile='',
            wildcard='*.*',
            style=wx.OPEN | wx.CHANGE_DIR
        )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.input_file_path = dlg.GetPath()
            # print 'You chose the following file: ' + self.inputFilePath
            self.chosen_file_text.SetLabel(utils.shorten_path(self.input_file_path, MAX_PATH_LENGTH))
        dlg.Destroy()

    def on_open_folder(self, event):
        """
        Create and show the Open DirDialog
        """
        dlg = wx.DirDialog(
            self, message='Choose a folder',
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.output_folder_path = dlg.GetPath()
            self.chosen_folder_text.SetLabel(utils.shorten_path(self.output_folder_path, MAX_PATH_LENGTH))
        dlg.Destroy()

    def on_action(self, event):
        if self.action_button.GetLabel() == 'Start':
            # Make sure you have an input and output path
            if not self.input_file_path:
                self.show_error_message('Error', 'Please select an input file.')
            elif not self.output_folder_path:
                self.show_error_message('Error', 'Please select an output folder.')
            else:
                self.action_button.SetLabel('Stop')
                self.running = True
                self.worker = workerthread.WorkerThread(self.input_file_path, self.hce, self.output_folder_path,
                                                        self.free_text, self.malaria, self.country,
                                                        completion_callback=self.on_result)
                self.enable_ui(False)
                self.increment_progress_bar()

        elif self.action_button.GetLabel() == 'Stop':
            self.action_button.SetLabel('Start')
            self.status_gauge.SetValue(1)
            self.status_gauge.SetValue(0)
            self.on_abort()

    def toggle_hce(self, event):
        """
        :type event: wx.CommandEvent
        """
        if isinstance(event.EventObject, wx.Menu):
            self.hce = event.EventObject.IsChecked(id=event.GetId())
        elif isinstance(event.EventObject, wx.CheckBox):
            self.hce = event.EventObject.IsChecked()

    def toggle_free_text(self, event):
        """
        :type event: wx.CommandEvent
        """
        if isinstance(event.EventObject, wx.Menu):
            self.free_text = event.EventObject.IsChecked(id=event.GetId())
        elif isinstance(event.EventObject, wx.CheckBox):
            self.free_text = event.EventObject.IsChecked()

    def toggle_malaria(self, event):
        """
        :type event: wx.CommandEvent
        """
        self.malaria = event.EventObject.IsChecked()

    def change_country(self, event):
        value = event.EventObject.Value
        if value != COUNTRY_DEFAULT and value in COUNTRIES:
            match = re.search(r'\(([A-Z]{3})\)$', value)
            self.country = match.group(1)
        else:
            self.country = None

    def show_error_message(self, title, message):
        dialog = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()

    def on_quit(self, event):
        """
        Quit, without showing a quit dialog.
        :param event: Not used
        """
        self.on_abort()
        if self.about_window:
            self.about_window.Close()
        if self.docs_window:
            self.docs_window.Close()
        self.Destroy()

    def on_docs(self, event):
        self.docs_window = vaDocs(None)
        self.docs_window.Centre()
        self.docs_window.Show()

    def on_about(self, event):
        self.about_window = vaAbout(None)
        self.about_window.Centre()
        self.about_window.Show()

    def on_result(self, event):
        """
        Completion callback.
        :type event: int
        :param event:
        :return:
        """
        if event is workerthread.CompletionStatus.ABORT:
            # If it's none we got an abort
            status_logger.info('Computation successfully aborted')
            self.action_button.Enable(True)
            self.running = False
            self.enable_ui(True)
            self.status_gauge.SetValue(1)
            self.status_gauge.SetValue(0)
        elif event is workerthread.CompletionStatus.DONE:
            # if it's done, then the algorithm is complete
            self.status_gauge.SetValue(1)
            status_logger.info('Process complete')
            self.action_button.SetLabel('Start')
            self.enable_ui(True)
            self.status_gauge.SetValue(1)
            self.status_gauge.SetValue(0)

    def on_abort(self):
        if self.worker:
            # if the thread is running, don't just stop
            status_logger.info('Attempting to cancel, please wait...')
            self.worker.abort()
            self.action_button.Enable(False)
            # do we need an else?  doesn't seem like it

    def enable_ui(self, enable):
        # Turns UI elements on and off
        for widget in self.enabled_widgets:
            widget.Enable(enable)

    def increment_progress_bar(self):
        if self.worker is not None and self.worker.isAlive():
            self.status_gauge.Pulse()
            # call f() again in 60 seconds
            threading.Timer(.3, self.increment_progress_bar).start()
        else:
            self.status_gauge.SetValue(1)
            self.status_gauge.SetValue(0)


def start():
    app = wx.App()
    app.SetAppName(APP_TITLE)
    vaUI(None, title=APP_TITLE)
    app.MainLoop()
