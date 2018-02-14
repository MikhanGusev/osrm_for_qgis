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
    
    PATH_EXE_NEW = 'osrm-ias-route'
    PATH_CONFIG_NEW = ''
    JSON_QUERY_NEW = ''
    
    PATH_EXE = 'osrm-ias-route-predefined'
    PATH_SRC_DIR = ''
    PATH_TGT_DIR = ''
    JSON_PARAMS = ''
    
    ALLOW_ONLY_FEATURE_SELECTION = False
    CURRENT_IS_NEW = True
    
    
    def read(self,plugin_dir):
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            config.read(plugin_dir+'/config')
            
            if config.has_section('osrm-ias-route') == True:
                self.PATH_EXE_NEW = config.get('osrm-ias-route','path_exe_new')
                self.PATH_CONFIG_NEW = config.get('osrm-ias-route','path_config_new')  
                self.JSON_QUERY_NEW = config.get('osrm-ias-route','json_query_new')
            
            if config.has_section('osrm-ias-route-predefined') == True:
                self.PATH_EXE = config.get('osrm-ias-route-predefined','path_exe')
                self.PATH_SRC_DIR = config.get('osrm-ias-route-predefined','path_src_dir')
                self.PATH_TGT_DIR = config.get('osrm-ias-route-predefined','path_tgt_dir')
                self.JSON_PARAMS = config.get('osrm-ias-route-predefined','json_params')

            if config.has_section('common') == True:     
                b_allow_str = config.get('common','allow_only_feature_selection')
                if b_allow_str == 'True':
                    self.ALLOW_ONLY_FEATURE_SELECTION = True
                else:
                    self.ALLOW_ONLY_FEATURE_SELECTION = False 
                b_current_str = config.get('common','current_is_new')
                if b_current_str == 'True':
                    self.CURRENT_IS_NEW = True
                else:
                    self.CURRENT_IS_NEW = False
                    
        except:
            pass
            
            
            
    def write(self,plugin_dir):
        
        try:
            config = ConfigParser.SafeConfigParser(allow_no_value=True)
            
            if config.has_section('osrm-ias-route') == False:
                config.add_section('osrm-ias-route')
            if config.has_section('osrm-ias-route-predefined') == False:
                config.add_section('osrm-ias-route-predefined')
            if config.has_section('common') == False:
                config.add_section('common')    
                
            config.set('osrm-ias-route', 'path_exe_new', self.PATH_EXE_NEW)
            config.set('osrm-ias-route', 'path_config_new', self.PATH_CONFIG_NEW)     
            config.set('osrm-ias-route', 'json_query_new', self.JSON_QUERY_NEW)
                
            config.set('osrm-ias-route-predefined', 'path_exe', self.PATH_EXE)
            config.set('osrm-ias-route-predefined', 'path_src_dir', self.PATH_SRC_DIR)
            config.set('osrm-ias-route-predefined', 'path_tgt_dir', self.PATH_TGT_DIR)
            config.set('osrm-ias-route-predefined', 'json_params', self.JSON_PARAMS)
            
            config.set('common', 'allow_only_feature_selection', str(self.ALLOW_ONLY_FEATURE_SELECTION))
            config.set('common', 'current_is_new', str(self.CURRENT_IS_NEW))
            
            with open(plugin_dir+'/config', 'wb') as f:
                config.write(f)
                
        except:
            pass
            
            
            
    
