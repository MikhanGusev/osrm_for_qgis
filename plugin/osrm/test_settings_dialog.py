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
    os.path.dirname(__file__), 'test_settings_dialog.ui'))


class OSRMTestSettingsDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """
        ...
        """
        super(OSRMTestSettingsDialog, self).__init__(parent)
        self.setupUi(self)

        self.butOk.clicked.connect(self.onOkClicked)


    def my_exec_(self,path_exe,path_src_dir,path_tgt_dir,json_transport_allowed,int_max_time,allow_only_feature_selection):
        """
        ...
        """
        self.lineEdit.setText(path_exe)
        self.lineEdit_2.setText(path_src_dir)
        self.lineEdit_3.setText(path_tgt_dir)
        self.lineEdit_4.setText(json_transport_allowed)
        self.lineEdit_5.setText(int_max_time)
        if allow_only_feature_selection == True:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        return self.exec_()


    def onOkClicked(self):
        """
        ...
        """
        self.accept()



