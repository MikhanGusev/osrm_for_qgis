# -*- coding: utf-8 -*-
"""
QGIS plugin: OSRM routing
"""

import os
import ConfigParser

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import Qt

from qgis.core import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'test_settings_dialog.ui'))


class OSRMTestSettingsDialog(QtGui.QDialog, FORM_CLASS):
    
    PATH_EXE = None
    PATH_SRC_FILE = None
    PATH_TGT_FILE = None

    
    def __init__(self, parent=None):
        """
        ...
        """
        super(OSRMTestSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.butOk.clicked.connect(self.onOkClicked)
        
        
    def my_exec_(self, plugin_path):
        """
        ...
        """
        self.plugin_path = plugin_path
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            config.read(self.plugin_path+'/config')
            path_exe = config.get('paths', 'exe_file_path')
            path_src_file = config.get('paths', 'src_file_path')
            path_tgt_file = config.get('paths', 'tgt_file_path')
        except:
            path_exe = ""
            path_src_file = ""
            path_tgt_file = ""
            
        self.lineEdit.setText(path_exe)
        self.lineEdit_2.setText(path_src_file)
        self.lineEdit_3.setText(path_tgt_file)
        
        return self.exec_()
        

    def onOkClicked(self):
        """
        ...
        """
        self.PATH_EXE = self.lineEdit.text()
        self.PATH_SRC_FILE = self.lineEdit_2.text()
        self.PATH_TGT_FILE = self.lineEdit_3.text()
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            config.add_section('paths')
            config.set('paths', 'exe_file_path', self.PATH_EXE)
            config.set('paths', 'src_file_path', self.PATH_SRC_FILE)
            config.set('paths', 'tgt_file_path', self.PATH_TGT_FILE)
            with open(self.plugin_path+'/config', 'wb') as configfile:
                config.write(configfile)
        except:
            pass

        self.accept()

        
        
        