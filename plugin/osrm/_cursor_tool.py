#!/usr/bin/env python
# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


class CursorTool(QgsMapTool):
    """
    ...
    """
    
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.emit( SIGNAL( "geomIdentified" ), point)

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
    
    
    
    