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


    def my_exec_(self,path_exe_new,path_config_new,json_query_new,path_exe,path_src_dir,path_tgt_dir,json_params,allow_only_feature_selection,current_is_new):
        """
        ...
        """
        
        #osrm-ias-route:
        self.lineEdit_4.setText(path_exe_new)
        self.lineEdit_5.setText(path_config_new)
        self.textEdit_2.setPlainText(json_query_new)
        
        # osrm-ias-route-predefined:
        self.lineEdit.setText(path_exe)
        self.lineEdit_2.setText(path_src_dir)
        self.lineEdit_3.setText(path_tgt_dir)
        self.textEdit.setPlainText(json_params)
        
        # common:
        if allow_only_feature_selection == True:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        if current_is_new == True:
            self.checkBox_2.setChecked(True)
        else:
            self.checkBox_2.setChecked(False)
            
        return self.exec_()


    def onOkClicked(self):
        """
        ...
        """
        self.accept()



