#!/usr/bin/env python
# coding=utf-8
"""
QGIS plugin: OSRM routing
"""

import os
import ConfigParser

class PropertiesParser(object):

    """Parse a java like properties file
    Parser wrapping around ConfigParser allowing reading of java like
    properties file. Based on stackoverflow example:
    https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
    """

    def __init__(self):
        self.secheadname = 'dummy'
        self.sechead = '[' + self.secheadname + ']\n'

    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()

    def parse(self, filepath):
        try:
            self.fp = open(filepath)
            cp = ConfigParser.SafeConfigParser()
            cp.readfp(self)
            self.fp.close()
            return cp.get('dummy','output-dir')
            #return cp.items(self.secheadname)
        except:
            return ''