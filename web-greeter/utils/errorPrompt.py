# -*- coding: utf-8 -*-
#
#  errorPrompt.py
#
#  Copyright © 2021 JezerM
#
#  This file is part of Web Greeter.
#
#  Web Greeter is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  Web Greeter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The following additional terms are in effect as per Section 7 of the license:
#
#  The preservation of all legal notices and author attributions in
#  the material or in the Appropriate Legal Notices displayed
#  by works containing it is required.
#
#  You should have received a copy of the GNU General Public License
#  along with Web Greeter; If not, see <http://www.gnu.org/licenses/>.

from whither.toolkits.bootstrap import WebPage

from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QLabel, QPushButton

from logging import (
    getLogger,
    DEBUG,
    ERROR,
    Formatter,
    StreamHandler,
)

import globals

log_format = ''.join([
    '%(asctime)s [ %(levelname)s ] %(filename)s %(',
    'lineno)d: %(message)s'
])
formatter = Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")
logger = getLogger("javascript")
logger.propagate = False
stream_handler = StreamHandler()
stream_handler.setLevel(DEBUG)
stream_handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(stream_handler)

def javaScriptConsoleMessage(self, level: WebPage.JavaScriptConsoleMessageLevel, message: str, lineNumber: int, sourceID: str):
    if sourceID == "":
        sourceID = "console"

    logLevel = 0
    if level == WebPage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
        logLevel = 40
    elif level == WebPage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
        logLevel = 30
    elif level == WebPage.JavaScriptConsoleMessageLevel.InfoMessageLevel:
        return
    else:
        return

    record = logger.makeRecord(
        name="javascript",
        level=logLevel,
        fn="",
        lno=lineNumber,
        msg=message,
        args=(),
        exc_info=None
    )
    record.filename = sourceID
    logger.handle(record)

    if logLevel == 40:
        errorMessage = "{source} {line}: {msg}".format(source = sourceID, line = lineNumber, msg = message)
        errorPrompt(errorMessage)

class ErrorDialog(QDialog):
    def __init__(self, parent=None, err=""):
        super().__init__(parent)

        self.setWindowTitle("Error")

        self.buttonBox = QDialogButtonBox()
        cancelBtn = QPushButton("Cancel")
        defaultBtn = QPushButton("Set default theme")
        reloadBtn = QPushButton("Reload theme")

        reloadBtn.clicked.connect(self.handle_reload)

        self.buttonBox.addButton(defaultBtn, QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.addButton(reloadBtn, QDialogButtonBox.ButtonRole.ResetRole)
        self.buttonBox.addButton(cancelBtn, QDialogButtonBox.ButtonRole.RejectRole)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("An error ocurred. Do you want to change to default theme?")
        err = QLabel(err)
        self.layout.addWidget(message)
        self.layout.addWidget(err)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def handle_reload(self, value: bool):
        self.done(2)

def errorPrompt(err):

    if not globals.greeter.config.greeter.detect_theme_errors:
        return

    dia = ErrorDialog(globals.greeter._main_window.widget.centralWidget(), err)

    dia.exec()
    result = dia.result()

    if result == 0: # Cancel
        return
    elif result == 1: # Default theme
        globals.custom_config["app"]["greeter"]["theme"] = "gruvbox"
        globals.greeter.get_and_apply_user_config()
        globals.greeter.load_theme()
        return
    elif result == 2: # Reload
        globals.greeter.load_theme()
        return

    return

WebPage.javaScriptConsoleMessage = javaScriptConsoleMessage
