"""
This module is a modified version of a code sample from
http://wiki.wxpython.org/Combo%20Box%20that%20Suggests%20Options
"""
import wx


class CBEvent(object):
    normal = 0
    ignore = 1
    enter = 2


class PromptingComboBox(wx.ComboBox):
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', 0) | wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
        wx.ComboBox.__init__(self, *args, **kwargs)

        self.choices = self.GetItems()
        self._event_action = CBEvent.normal
        self._current_choice = self.Value

        self.Bind(wx.EVT_TEXT, self._on_evt_text)
        self.Bind(wx.EVT_KEY_DOWN, self._on_evt_key_down)
        self.Bind(wx.EVT_COMBOBOX, self._on_evt_combobox)

    def _on_evt_combobox(self, event):
        """
        Intercept and store value from combobox events.
        :param event:
        """
        self._event_action = CBEvent.ignore
        self._current_choice = self.Value
        event.Skip()

    def _on_evt_key_down(self, event):
        """
        Intercept key stokes to facilitate handling backspace, enter, and tab.
        :param event:
        """
        if event.GetKeyCode() == 8:
            self._event_action = CBEvent.ignore
        elif event.GetKeyCode() in [9, 13]:
            self.ChangeValue(self._current_choice)
            self.SetMark(0, len(self._current_choice))
            self._event_action = CBEvent.enter
        else:
            self._event_action = CBEvent.normal
        event.Skip()

    def _find_choice(self, text):
        for choice in self.choices:
            if choice.lower().startswith(text.lower()):
                return choice
        return None

    def _on_evt_text(self, event):
        """
        Intercept value changes to attempt to match with combobox choices. A match is found if one of the choices
        starts with the the new value. When a match is found, post a combobox event.
        :param event:
        """
        text = event.GetString()

        current_action, self._event_action = self._event_action, CBEvent.normal

        if current_action == CBEvent.ignore:
            event.Skip()
        elif current_action == CBEvent.enter:
            event.Skip()
        elif current_action == CBEvent.normal and not text:
            self._event_action = CBEvent.enter
            wx.CallAfter(self._SetValue, self._current_choice)
        else:
            choice = self._find_choice(text)
            if choice:
                prev_choice, self._current_choice = self._current_choice, choice

                self._event_action = CBEvent.ignore
                self.SetValue(choice)
                self.SetInsertionPoint(len(text))
                self.SetMark(len(text), len(choice))

                # Post a combobox event if the choice has changed.
                if prev_choice != self._current_choice:
                    command_event = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, self.GetId())
                    command_event.EventObject = self
                    wx.PostEvent(self, command_event)
            else:
                event.Skip()
        self.Refresh()

    def _SetValue(self, text):
        self.SetValue(text)
        self.SetMark(0, len(self._current_choice))
