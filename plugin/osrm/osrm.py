# -*- coding: utf-8 -*-
"""
QGIS plugin: OSRM routing
"""

import os.path
import subprocess
from subprocess import CalledProcessError, check_output

from PyQt4 import QtGui
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon, QMenu, QMessageBox, QColor, QToolButton
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
import qgis.utils

from osgeo import ogr

from test_settings_dialog import OSRMTestSettingsDialog
from test_results_dialog import OSRMTestResultsDialog

from _feature_tool import IdentifyFeatureTool
from _cursor_tool import CursorTool
from _settings import Settings


class OSRM:
    """
    Plugin's entry point
    """

    action_init = None
    action_routing = None
    action_settings = None
    action_start_flag = None
    action_end_flag = None
    action_start_coords_flag = None
    action_end_coords_flag = None
    action_path = None

    map_tool = None

    toolbutton_start_flag = None
    toolbutton_end_flag = None
    toolbutton_start_coords_flag = None
    toolbutton_end_coords_flag = None
    toolbutton_path = None

    LAYER_STARTFLAG = None
    LAYER_ENDFLAG = None
    LAYER_PATH = None

    PRESSED_TOOLB = None
    PRESSED_ICON = None # to store the icon for button before pressing

    LAT_START = None
    LON_START = None
    LAT_END = None
    LON_END = None

    settings = None


    def __init__(self, iface):
        """
        Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Create the dialogs (after translation) and keep reference
        self.dlg_settings = OSRMTestSettingsDialog()
        self.dlg_results = OSRMTestResultsDialog()

        # Declare instance attributes
        self.actions = []
        self.toolbuttons = []
        self.menu = self.tr(u'&OSRM')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OSRM')
        self.toolbar.setObjectName(u'OSRM')

        self.settings = Settings()
        self.settings.read(os.path.dirname(__file__))


    def add_action(
        self,
        menu, # to which sub menu add this action. If None action is added to the root via addPluginToMenu()
        icon_path,
        text,
        callback = None,
        enabled_flag = True,
        status_tip = None,
        whats_this = None,
        add_to_toolbar = False,
        parent = None):
        """
        ...
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        toolbutton = QToolButton()
        toolbutton.setIcon(icon)

        if callback is not None:
            action.triggered.connect(callback)
            toolbutton.clicked.connect(callback)

        action.setEnabled(enabled_flag)
        toolbutton.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
            toolbutton.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
            toolbutton.setWhatsThis(whats_this)

        if menu is None:
            self.iface.addPluginToMenu(self.menu, action)
        else:
            menu.addAction(action)
        self.actions.append(action)

        if add_to_toolbar:
            #self.toolbar.addAction(action)
            self.toolbar.addWidget(toolbutton) # otherwise it is not able to get the toolbutton from toolbar
            self.toolbuttons.append(toolbutton)
        else:
            toolbutton = None

        return action, toolbutton


    def initGui(self):
        """
        ...
        """
        self.action_init, stub = self.add_action(
            menu=None,
            icon_path=None,
            text=self.tr(u'Initialize'),
            callback=self.onInitClick,
            parent=self.iface.mainWindow(),
            enabled_flag=True)
        self.action_routing, stub = self.add_action(
            menu=None,
            icon_path=None,
            text=self.tr(u'Routing'),
            callback=None,
            parent=self.iface.mainWindow(),
            enabled_flag=True)
        self.action_settings, stub = self.add_action(
            menu=None,
            icon_path=None,
            text=self.tr(u'Settings'),
            callback=self.onSettingsClick,
            parent=self.iface.mainWindow(),
            enabled_flag=True)

        menu_main = QMenu('menu')
        self.action_routing.setMenu(menu_main)

        self.action_start_flag, self.toolbutton_start_flag = self.add_action(
            menu=menu_main,
            icon_path=self.plugin_dir+'/icons/start.png',
            text=self.tr(u'Set start flag'),
            callback=self.onStartFlagClicked,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
            status_tip=self.tr(u'Mark feature as start node'),
            add_to_toolbar = True)
        self.action_end_flag, self.toolbutton_end_flag = self.add_action(
            menu=menu_main,
            icon_path=self.plugin_dir+'/icons/end.png',
            text=self.tr(u'Set end flag'),
            callback=self.onEndFlagClicked,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
            status_tip=self.tr(u'Mark feature as end node'),
            add_to_toolbar = True)
        self.action_start_coords_flag, self.toolbutton_start_coords_flag = self.add_action(
            menu=menu_main,
            icon_path=self.plugin_dir+'/icons/start_pressed.png',
            text=self.tr(u'Set start flag'),
            callback=self.onStartCoordsFlagClicked,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
            status_tip=self.tr(u'Place a point on the map'),
            add_to_toolbar = True)
        self.action_end_coords_flag, self.toolbutton_end_coords_flag = self.add_action(
            menu=menu_main,
            icon_path=self.plugin_dir+'/icons/end_pressed.png',
            text=self.tr(u'Set end flag'),
            callback=self.onEndCoordsFlagClicked,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
            status_tip=self.tr(u'Place a point on the map'),
            add_to_toolbar = True)
        self.action_path, self.toolbutton_path = self.add_action(
            menu=menu_main,
            icon_path=self.plugin_dir+'/icons/path.png',
            text=self.tr(u'Calculate shortest path'),
            callback=self.onPathClicked,
            parent=self.iface.mainWindow(),
            enabled_flag=False,
            status_tip=self.tr(u'Calculate the shortest path between start and end nodes'),
            add_to_toolbar = True)


    def unload(self):
        """
        Removes the plugin menu item and icon from QGIS GUI.
        """
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QNetwork'),
                action)
            #self.iface.removeToolBarIcon(action)
        del self.toolbar


    #**********************************************************************************************************#
    #                                                                                                          #
    #                                                  SLOTS                                                   #
    #                                                                                                          #
    #**********************************************************************************************************#

    def onInitClick(self):
        """
        ...
        """
        self.init(self.settings.ALLOW_ONLY_FEATURE_SELECTION)
            
            
    def onSettingsClick(self): 
        """
        ...
        """
        self.dlg_settings.show()
        result = self.dlg_settings.my_exec_(self.settings.PATH_EXE, self.settings.PATH_SRC_DIR, self.settings.PATH_TGT_DIR, self.settings.JSON_TRANSPORT_ALLOWED, self.settings.INT_MAX_TIME, self.settings.ALLOW_ONLY_FEATURE_SELECTION)
        if result == 1:
            self.settings.PATH_EXE = self.dlg_settings.lineEdit.text()
            self.settings.PATH_SRC_DIR = self.dlg_settings.lineEdit_2.text()
            self.settings.PATH_TGT_DIR = self.dlg_settings.lineEdit_3.text()
            self.settings.JSON_TRANSPORT_ALLOWED = self.dlg_settings.lineEdit_4.text()
            self.settings.INT_MAX_TIME = self.dlg_settings.lineEdit_5.text()
            if self.dlg_settings.checkBox.isChecked() == True:
                self.settings.ALLOW_ONLY_FEATURE_SELECTION = True
            else:
                self.settings.ALLOW_ONLY_FEATURE_SELECTION = False
            self.settings.write(os.path.dirname(__file__))
            

    def onStartFlagClicked(self):
        """
        ...
        """
        self.clickFlagButton(self.toolbutton_start_flag, QIcon(self.plugin_dir+'/icons/start_pressed.png'))

    def onEndFlagClicked(self):
        """
        ...
        """
        self.clickFlagButton(self.toolbutton_end_flag, QIcon(self.plugin_dir+'/icons/end_pressed.png'))


    def onStartCoordsFlagClicked(self):
        """
        ...
        """
        self.clickFlagButton(self.toolbutton_start_coords_flag, QIcon(self.plugin_dir+'/icons/start_pressed.png'))

    def onEndCoordsFlagClicked(self):
        """
        ...
        """
        self.clickFlagButton(self.toolbutton_end_coords_flag, QIcon(self.plugin_dir+'/icons/end_pressed.png'))


    def onPathClicked(self):
        """
        ...
        """
        try:
            output = subprocess.check_output([self.settings.PATH_EXE, str(self.LON_START), str(self.LAT_START), str(self.LON_END), str(self.LAT_END), self.settings.JSON_TRANSPORT_ALLOWED, self.settings.INT_MAX_TIME, self.settings.PATH_SRC_DIR, self.settings.PATH_TGT_DIR], shell=False, stderr=subprocess.STDOUT)
            returncode = 0
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode
        #except:
        #    output = 'Error'
        #    returncode = -1
        self.dlg_results.textEdit.setText(output)
        self.dlg_results.show()
        ret = self.dlg_results.my_exec_() # show results in the dialog
        if returncode == 0:
            driver = ogr.GetDriverByName('GeoJSON')
            ds = driver.Open(self.settings.PATH_TGT_DIR + '/path.json', 0)
            layer = ds.GetLayer(0)
            self.updateResultLayer(layer, self.LAYER_PATH)
        

    def onIdentifyFeature(self,layer,feature):
        """
        Select only one feature among point layers in the project
        """
        if self.PRESSED_TOOLB is None: # skip any actions if no flag button pressed
            return

        # WARNING. Possibly we must check here the proper CRS!
        geom = feature.geometry()
        point = geom.asPoint()

        if self.PRESSED_TOOLB == self.toolbutton_start_flag:
            self.LAT_START = point.y()
            self.LON_START = point.x()
            self.placeFlag(self.toolbutton_start_flag,feature)
        elif self.PRESSED_TOOLB == self.toolbutton_end_flag:
            self.LAT_END = point.y()
            self.LON_END = point.x()
            self.placeFlag(self.toolbutton_end_flag,feature)

        self.clickFlagButton(self.PRESSED_TOOLB, None) # unpress any pressed flag button and unset map tool


    def onIdentifyCursorCoords(self,point):
        """
        ...
        """
        if self.PRESSED_TOOLB is None: # skip any actions if no flag button pressed
            return

        # TEMPORARY:
        canvas = self.iface.mapCanvas()
        transf = QgsCoordinateTransform(QgsCoordinateReferenceSystem(canvas.mapRenderer().destinationCrs().authid()), QgsCoordinateReferenceSystem(4326))
        transf_point = transf.transform(point)

        if self.PRESSED_TOOLB == self.toolbutton_start_coords_flag:
            self.LAT_START = transf_point.y()
            self.LON_START = transf_point.x()
            self.placeFlagByCoords(self.toolbutton_start_coords_flag,transf_point)
        elif self.PRESSED_TOOLB == self.toolbutton_end_coords_flag:
            self.LAT_END = transf_point.y()
            self.LON_END = transf_point.x()
            self.placeFlagByCoords(self.toolbutton_end_coords_flag,transf_point)

        self.clickFlagButton(self.PRESSED_TOOLB, None) # unpress any pressed flag button and unset map tool


    #**********************************************************************************************************#
    #                                                                                                          #
    #                                                  METHODS                                                 #
    #                                                                                                          #
    #**********************************************************************************************************#


    def init(self,select_features):
        """
        ...
        """
        self.clickFlagButton(self.PRESSED_TOOLB, None) # unpress any pressed flag button and unset map tool
        self.PRESSED_TOOLB = None
        self.PRESSED_ICON = None

        self.LAT_START = None
        self.LON_START = None
        self.LAT_END = None
        self.LON_END = None       

        # TODO: recreate groups
        root_layer_tree = QgsProject.instance().layerTreeRoot()
        common_group = root_layer_tree.insertGroup(0,'OSRM')
        flags_group = common_group.addGroup('Flags')
        results_group = common_group.addGroup('Results')

        # TODO: reset layer
        self.LAYER_STARTFLAG = self.createFlagsLayer(flags_group,'_osrm_flag_start',self.plugin_dir+'/icons/start_flag.svg')
        if self.LAYER_STARTFLAG is None:
            self.showWarn(self.tr(u'Unable to create start flag\'s layer'))

        # TODO: reset layer
        self.LAYER_ENDFLAG = self.createFlagsLayer(flags_group,'_osrm_flag_end',self.plugin_dir+'/icons/end_flag.svg')
        if self.LAYER_ENDFLAG is None:
            self.showWarn(self.tr(u'Unable to create end flag\'s layer'))

        # TODO: reset layer
        self.LAYER_PATH = self.createResultLayer(results_group,'_osrm_path',QColor(255,0,0))
        if self.LAYER_PATH is None:
            self.showWarn(self.tr(u'Unable to create result layer for shortest path calculations'))

        self.action_start_flag.setEnabled(True)
        self.action_end_flag.setEnabled(True)
        self.action_path.setEnabled(True)

        self.toolbutton_path.setEnabled(True)

        self.action_init.setEnabled(False)

        if select_features == True:
            self.toolbutton_start_flag.setEnabled(True)
            self.toolbutton_end_flag.setEnabled(True)
            self.toolbutton_start_coords_flag.setEnabled(False)
            self.toolbutton_end_coords_flag.setEnabled(False)
            self.map_tool = IdentifyFeatureTool(self.iface.mapCanvas())
            QObject.connect(self.map_tool , SIGNAL("geomIdentified") , self.onIdentifyFeature)
        else:
            self.toolbutton_start_flag.setEnabled(False)
            self.toolbutton_end_flag.setEnabled(False)
            self.toolbutton_start_coords_flag.setEnabled(True)
            self.toolbutton_end_coords_flag.setEnabled(True)
            self.map_tool = CursorTool(self.iface.mapCanvas())
            QObject.connect(self.map_tool , SIGNAL("geomIdentified") , self.onIdentifyCursorCoords)


    def placeFlag(self,toolb,feature):
        """
        ...
        """
        if toolb == self.toolbutton_start_flag:
            layer_this = self.LAYER_STARTFLAG
            layer_other = self.LAYER_ENDFLAG
        elif toolb == self.toolbutton_end_flag:
            layer_this = self.LAYER_ENDFLAG
            layer_other = self.LAYER_STARTFLAG
        else:
            return

        # Remove old flag feature.
        ids = [f.id() for f in layer_this.getFeatures()]
        layer_this.dataProvider().deleteFeatures(ids)
        # Create new one.
        geom = feature.geometry()
        point = geom.asPoint()
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(point))
        (res, outFeats) = layer_this.dataProvider().addFeatures([new_feature])
        layer_this.triggerRepaint() # Otherwise point in this layer will not be moved.


    def placeFlagByCoords(self,toolb,point):
        """
        ...
        """
        if toolb == self.toolbutton_start_coords_flag:
            layer_this = self.LAYER_STARTFLAG
            layer_other = self.LAYER_ENDFLAG
        elif toolb == self.toolbutton_end_coords_flag:
            layer_this = self.LAYER_ENDFLAG
            layer_other = self.LAYER_STARTFLAG
        else:
            return

        # Remove old flag feature.
        ids = [f.id() for f in layer_this.getFeatures()]
        layer_this.dataProvider().deleteFeatures(ids)
        # Create new one.
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(point))
        (res, outFeats) = layer_this.dataProvider().addFeatures([new_feature])
        layer_this.triggerRepaint() # Otherwise point in this layer will not be moved.

        #self.showMsg(str(point.x()) + " , " + str(point.y()))


    def createFlagsLayer(self,group,name,icon_path):
        """
        ...
        """
        uri_layer = str('Point?crs=epsg:4326')
        layer = QgsVectorLayer(uri_layer,name,"memory")
        if layer is None:
            return None
        layer.setReadOnly(True)
        QgsMapLayerRegistry.instance().addMapLayer(layer,False)
        group.addLayer(layer)
        symbols = layer.rendererV2().symbols()
        symbol = symbols[0]
        symbol.deleteSymbolLayer(0)
        sl = QgsSvgMarkerSymbolLayerV2() # http://qgis.org/api/classQgsSvgMarkerSymbolLayerV2.html
        sl.setPath(icon_path)
        sl.setSize(6.0)
        sl.setHorizontalAnchorPoint(QgsMarkerSymbolLayerV2.Left)
        sl.setVerticalAnchorPoint(QgsMarkerSymbolLayerV2.Bottom)
        symbol.appendSymbolLayer(sl)
        qgis.utils.iface.legendInterface().refreshLayerSymbology(layer)
        return layer


    def createResultLayer(self,group,name,color):
        """
        ...
        """
        uri_layer = str('LineString?crs=epsg:4326')
        layer = QgsVectorLayer(uri_layer,name,"memory")
        if layer is None:
            return None
        layer.setReadOnly(True)
        QgsMapLayerRegistry.instance().addMapLayer(layer,False)
        group.addLayer(layer)
        symbols = layer.rendererV2().symbols()
        symbol = symbols[0]
        symbol.deleteSymbolLayer(0)
        sl = QgsSimpleLineSymbolLayerV2()
        sl.setWidth(1.9)
        sl.setColor(color)
        symbol.appendSymbolLayer(sl)
        qgis.utils.iface.legendInterface().refreshLayerSymbology(layer)
        return layer


    def clickFlagButton(self, toolbutton, icon):
        """
        ...
        """
        if self.PRESSED_TOOLB is not None:
            self.PRESSED_TOOLB.setDown(False)
            self.PRESSED_TOOLB.setIcon(self.PRESSED_ICON)
        if toolbutton == self.PRESSED_TOOLB:
            self.PRESSED_TOOLB = None
            self.PRESSED_ICON = None
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
            return
        self.PRESSED_TOOLB = toolbutton
        self.PRESSED_ICON = toolbutton.icon()
        toolbutton.setDown(True)
        toolbutton.setIcon(icon)
        self.iface.mapCanvas().setMapTool(self.map_tool)


    def updateResultLayer(self,ogr_layer,qgis_layer):
        """
        Clear and than fill the layer with line geometries
        """
        # TODO: ...
        features_to_visualize = []
        ogr_layer.ResetReading()
        ogr_feature = ogr_layer.GetNextFeature()
        while ogr_feature is not None:
            ogr_geom = ogr_feature.GetGeometryRef()
            wkb = ogr_geom.ExportToWkb(ogr.wkbNDR)
            qgs_geom = QgsGeometry()
            qgs_geom.fromWkb(wkb)
            qgs_feature = QgsFeature()
            qgs_feature.setGeometry(qgs_geom)
            if qgs_feature.geometry().type() == QGis.Line:
                features_to_visualize.append(qgs_feature)
            ogr_feature = ogr_layer.GetNextFeature()
        # Clear layer and add features at once.
        ids = [f.id() for f in qgis_layer.getFeatures()]
        qgis_layer.dataProvider().deleteFeatures(ids)
        (res, outFeats) = qgis_layer.dataProvider().addFeatures(features_to_visualize)
        qgis_layer.triggerRepaint()


    def showMsg(self, text):
        """
        ...
        """
        msg_box = QtGui.QMessageBox()
        msg_box.setText(text)
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.exec_()


    def showWarn(self, text):
        """
        ...
        """
        self.showMsg(self.tr(u'Warning. ') + text)


     # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """
        Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OSRM', message)



