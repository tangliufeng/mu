"""
A mode for working with ESP8266 and ESP32 boards running MicroPython.

Copyright (c) 2015-2019 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
from mu.modes.base import MicroPythonMode
from mu.modes.api import ESP_APIS, SHARED_APIS
from mu.interface.panes import CHARTS
from PyQt5.QtCore import QThread
import os


logger = logging.getLogger(__name__)


class ESPMode(MicroPythonMode):
    """
    Represents the functionality required for running MicroPython on ESP8266
    """

    name = ("ESP MicroPython")
    short_name = "esp"
    description = ("Write MicroPython on ESP8266/ESP32 boards.")
    icon = "esp"

    # The below list defines the supported devices, however, many
    # devices are using the exact same FTDI USB-interface, with vendor
    # ID 0x403 without reporting their own VID/PID

    # In some instances we can recognize the device not on VID/PID,
    # but on manufacturer ID, that's what the third column is for.
    # These more specific device specifications, should be listed
    # before the generic FTDI VID/PID's
    valid_boards = [
        # VID  , PID,    Manufacturer string, Device name
        (0x1A86, 0x7523, None, "HL-340"),
        (0x10C4, 0xEA60, None, "CP210x"),
        (0x0403, 0x6001, "M5STACK Inc.", "M5Stack ESP32 device"),
        (0x0403, 0x6001, None, None),  # FT232/FT245 (XinaBox CW01, CW02)
        (0x0403, 0x6010, None, None),  # FT2232C/D/L/HL/Q (ESP-WROVER-KIT)
        (0x0403, 0x6011, None, None),  # FT4232
        (0x0403, 0x6014, None, None),  # FT232H
        (0x0403, 0x6015, None, None),  # FT X-Series (Sparkfun ESP32)
        (0x0403, 0x601C, None, None),  # FT4222H
    ]

    def actions(self):
        """
        Return an ordered list of actions provided by this module. An action
        is a name (also used to identify the icon) , description, and handler.
        """
        buttons = [

            {
                "name": "repl",
                "display_name": ("REPL"),
                "description": (
                    "Use the REPL to live-code on the " "ESP8266/ESP32."
                ),
                "handler": self.toggle_repl,
                "shortcut": "Ctrl+Shift+I",
            },
        ]

        return buttons


    def toggle_repl(self, event):
      
        if self.repl:
            # Remove REPL
            super().toggle_repl(event)
            self.set_buttons(files=True)
        elif not (self.repl):
            # Add REPL
            super().toggle_repl(event)
            if self.repl:
                self.set_buttons(files=False)

   

    def run(self):
        """
        Takes the currently active tab, compiles the Python script therein into
        a hex file and flashes it all onto the connected device.
        """
        """
        if self.repl:
            message = ("Flashing cannot be performed at the same time as the "
                        "REPL is active.")
            information = ("File transfers use the same "
                            "USB serial connection as the REPL. Toggle the "
                            "REPL off and try again.")
            self.view.show_message(message, information)
            return
        """
        logger.info("Running script.")
        # Grab the Python script.
        tab = self.view.current_tab
        if tab is None:
            # There is no active text editor.
            message = ("Cannot run anything without any active editor tabs.")
            information = (
                "Running transfers the content of the current tab"
                " onto the device. It seems like you don't have "
                " any tabs open."
            )
            self.view.show_message(message, information)
            return
        python_script = tab.text().split("\n")
        if not self.repl:
            self.toggle_repl(None)
        if self.repl and self.connection:
            self.connection.send_commands(python_script)


    def deactivate(self):
        """
        Invoked whenever the mode is deactivated.
        """
        super().deactivate()


    def device_changed(self, new_device):
        """
        Invoked when the user changes device.
        """
        super().device_changed(new_device)
