# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import pkg_resources

from ..qt import QtCore, QtGui, QtWebKit
from ..ui.getting_started_dialog_ui import Ui_GettingStartedDialog


class GettingStartedDialog(QtGui.QDialog, Ui_GettingStartedDialog):
    """
    GettingStarted dialog.
    """

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.uiWebView.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        self.uiWebView.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        self.adjustSize()
        self.uiWebView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.uiWebView.linkClicked.connect(self._urlClickedSlot)
        self.uiWebView.loadFinished.connect(self._loadFinishedSlot)
        self.uiCheckBox.setChecked(QtCore.QSettings().value("GUI/show_getting_started_dialog", True, type=bool))
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._loadFinishedSlot)
        self._timer.setSingleShot(True)
        self._timer.start(5000)
        self.uiWebView.load(QtCore.QUrl("http://start.gns3.net"))

    def showit(self):
        """
        Either this dialog should be automatically showed at startup.

        :returns: boolean
        """

        return self.uiCheckBox.isChecked()

    def done(self, result):
        """
        This dialog is closed.

        :param result: ignored
        """

        QtCore.QSettings().setValue("GUI/show_getting_started_dialog", self.uiCheckBox.isChecked())
        QtGui.QDialog.done(self, result)

    def _urlClickedSlot(self, url):
        """
        Opens a clicked URL using user's default browser.

        :param url: URL to open
        """

        if QtGui.QDesktopServices.openUrl(url) is False:
            QtGui.QMessageBox.critical(self, "Getting started", "Failed to open the URL: {}".format(url))

    def _loadFinishedSlot(self, result=False):
        """
        Slot called when the web page has been loaded.

        :param result: boolean
        """

        self.uiWebView.loadFinished.disconnect(self._loadFinishedSlot)
        self._timer.stop()
        self._timer.timeout.disconnect()
        if result is False:
            # load a local resource if the page is not available
            resource_name = os.path.join("static", "getting_started.html")
            getting_started = None
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                getting_started = os.path.normpath(resource_name)
            elif pkg_resources.resource_exists("gns3", resource_name):
                getting_started_page = pkg_resources.resource_filename("gns3", resource_name)
                getting_started = os.path.normpath(getting_started_page)
            if getting_started:
                self.uiWebView.load(QtCore.QUrl("file://{}".format(getting_started)))
            else:
                self.accept()
