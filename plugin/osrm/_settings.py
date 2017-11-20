#!/usr/bin/env python
# coding=utf-8
"""
QGIS plugin: OSRM routing
"""

import os
import ConfigParser

from PyQt4.QtCore import *
from qgis.core import *


class Settings:
    
    PATH_EXE = 'osrm-ng-route'
    PATH_SRC_DIR = ''
    PATH_TGT_DIR = ''
    JSON_TRANSPORT_ALLOWED = '{"rail": true, "auto": true, "sea": true, "river": true, "air": true}'
    INT_MAX_TIME = '0'
    ALLOW_ONLY_FEATURE_SELECTION = False
    
    
    def read(self,plugin_dir):
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            config.read(plugin_dir+'/config')
            
            if config.has_section('paths') == True:
                self.PATH_EXE = config.get('paths','path_exe')
                self.PATH_SRC_DIR = config.get('paths','path_src_dir')
                self.PATH_TGT_DIR = config.get('paths','path_tgt_dir')
                
            if config.has_section('params') == True:
                self.JSON_TRANSPORT_ALLOWED = config.get('params','json_transport_allowed')
                self.INT_MAX_TIME = config.get('params','int_max_time')
                b_str = config.get('params','allow_only_feature_selection')
                if b_str == 'True':
                    self.ALLOW_ONLY_FEATURE_SELECTION = True
                else:
                    self.ALLOW_ONLY_FEATURE_SELECTION = False
                
        except:
            pass
            
            
    def write(self,plugin_dir):
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            
            if config.has_section('paths') == False:
                config.add_section('paths')
            if config.has_section('params') == False:
                config.add_section('params')
                
            config.set('paths', 'path_exe', self.PATH_EXE)
            config.set('paths', 'path_src_dir', self.PATH_SRC_DIR)
            config.set('paths', 'path_tgt_dir', self.PATH_TGT_DIR)
            config.set('params', 'json_transport_allowed', self.JSON_TRANSPORT_ALLOWED)
            config.set('params', 'int_max_time', self.INT_MAX_TIME)
            config.set('params', 'allow_only_feature_selection', str(self.ALLOW_ONLY_FEATURE_SELECTION))
            
            with open(plugin_dir+'/config', 'wb') as f:
                config.write(f)
                
        except:
            pass
            
            
            
    