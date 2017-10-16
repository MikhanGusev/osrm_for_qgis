# -*- coding: utf-8 -*-
"""
QGIS plugin: OSRM routing
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import Qt

from qgis.core import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'test_results_dialog.ui'))


class OSRMTestResultsDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """
        ...
        """
        super(OSRMTestResultsDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.butOk.clicked.connect(self.onOkClicked)
        
        
    def my_exec_(self):
        """
        ...
        """
        return self.exec_()
        

    def onOkClicked(self):
        """
        ...
        """        
        self.accept()

        
        
        