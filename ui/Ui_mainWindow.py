# Form implementation generated from reading ui file '/home/mark/projects/python/WN2A_RFPeakSearch/ui/mainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1533, 1140)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(27, 30, 32))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(192, 192, 176))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(27, 30, 32))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(192, 192, 176))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 113, 115))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(192, 192, 176))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(192, 192, 176))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush)
        MainWindow.setPalette(palette)
        MainWindow.setAutoFillBackground(True)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox.setMinimumSize(QtCore.QSize(185, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(130, 16777215))
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.floatSweepStartFreq = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.floatSweepStartFreq.setMinimum(23.5)
        self.floatSweepStartFreq.setMaximum(3000.0)
        self.floatSweepStartFreq.setObjectName("floatSweepStartFreq")
        self.verticalLayout.addWidget(self.floatSweepStartFreq)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.verticalLayout.addWidget(self.label_11)
        self.floatSweepStopFreq = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.floatSweepStopFreq.setMinimum(23.5)
        self.floatSweepStopFreq.setMaximum(3000.0)
        self.floatSweepStopFreq.setProperty("value", 3000.0)
        self.floatSweepStopFreq.setObjectName("floatSweepStopFreq")
        self.verticalLayout.addWidget(self.floatSweepStopFreq)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_graphWidth = QtWidgets.QLabel(self.groupBox)
        self.label_graphWidth.setObjectName("label_graphWidth")
        self.verticalLayout.addWidget(self.label_graphWidth)
        self.minGraphWidth = QtWidgets.QSpinBox(self.groupBox)
        self.minGraphWidth.setMaximum(10000)
        self.minGraphWidth.setProperty("value", 600)
        self.minGraphWidth.setObjectName("minGraphWidth")
        self.verticalLayout.addWidget(self.minGraphWidth)
        self.label_graphHeight = QtWidgets.QLabel(self.groupBox)
        self.label_graphHeight.setObjectName("label_graphHeight")
        self.verticalLayout.addWidget(self.label_graphHeight)
        self.minGraphHeight = QtWidgets.QSpinBox(self.groupBox)
        self.minGraphHeight.setMaximum(10000)
        self.minGraphHeight.setProperty("value", 400)
        self.minGraphHeight.setObjectName("minGraphHeight")
        self.verticalLayout.addWidget(self.minGraphHeight)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addWidget(self.groupBox, 1, 2, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_3.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(120, 16777215))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.chkArduinoLED = QtWidgets.QCheckBox(self.groupBox_3)
        self.chkArduinoLED.setMinimumSize(QtCore.QSize(110, 0))
        self.chkArduinoLED.setChecked(False)
        self.chkArduinoLED.setObjectName("chkArduinoLED")
        self.gridLayout_2.addWidget(self.chkArduinoLED, 14, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 12, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 19, 0, 1, 1)
        self.numPlotFloor = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.numPlotFloor.setDecimals(3)
        self.numPlotFloor.setMinimum(-90.0)
        self.numPlotFloor.setMaximum(100.0)
        self.numPlotFloor.setSingleStep(0.1)
        self.numPlotFloor.setProperty("value", -62.0)
        self.numPlotFloor.setObjectName("numPlotFloor")
        self.gridLayout_2.addWidget(self.numPlotFloor, 7, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setMinimumSize(QtCore.QSize(85, 0))
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 16, 0, 1, 1)
        self.numPlotCeiling = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.numPlotCeiling.setDecimals(3)
        self.numPlotCeiling.setMinimum(-85.0)
        self.numPlotCeiling.setMaximum(100.0)
        self.numPlotCeiling.setSingleStep(0.1)
        self.numPlotCeiling.setProperty("value", 25.0)
        self.numPlotCeiling.setObjectName("numPlotCeiling")
        self.gridLayout_2.addWidget(self.numPlotCeiling, 5, 0, 1, 1)
        self.cbxSerialPortSelection = QtWidgets.QComboBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxSerialPortSelection.sizePolicy().hasHeightForWidth())
        self.cbxSerialPortSelection.setSizePolicy(sizePolicy)
        self.cbxSerialPortSelection.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.cbxSerialPortSelection.setObjectName("cbxSerialPortSelection")
        self.gridLayout_2.addWidget(self.cbxSerialPortSelection, 17, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 11, 0, 1, 1)
        self.btnRefreshPortsList = QtWidgets.QPushButton(self.groupBox_3)
        self.btnRefreshPortsList.setObjectName("btnRefreshPortsList")
        self.gridLayout_2.addWidget(self.btnRefreshPortsList, 18, 0, 1, 1)
        self.numPeakMarkers = QtWidgets.QSpinBox(self.groupBox_3)
        self.numPeakMarkers.setMinimum(1)
        self.numPeakMarkers.setMaximum(25)
        self.numPeakMarkers.setProperty("value", 3)
        self.numPeakMarkers.setObjectName("numPeakMarkers")
        self.gridLayout_2.addWidget(self.numPeakMarkers, 1, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 4, 0, 1, 1)
        self.cbxSerialSpeedSelection = QtWidgets.QComboBox(self.groupBox_3)
        self.cbxSerialSpeedSelection.setMinimumSize(QtCore.QSize(85, 0))
        self.cbxSerialSpeedSelection.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.cbxSerialSpeedSelection.setObjectName("cbxSerialSpeedSelection")
        self.gridLayout_2.addWidget(self.cbxSerialSpeedSelection, 21, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 23, 0, 1, 1)
        self.chkShowGrid = QtWidgets.QCheckBox(self.groupBox_3)
        self.chkShowGrid.setWhatsThis("")
        self.chkShowGrid.setObjectName("chkShowGrid")
        self.gridLayout_2.addWidget(self.chkShowGrid, 15, 0, 1, 1, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.dbl_attenuator_dB = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.dbl_attenuator_dB.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.dbl_attenuator_dB.setMaximum(31.75)
        self.dbl_attenuator_dB.setSingleStep(0.25)
        self.dbl_attenuator_dB.setObjectName("dbl_attenuator_dB")
        self.gridLayout_2.addWidget(self.dbl_attenuator_dB, 13, 0, 1, 1)
        self.btn_open_serial_port = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_open_serial_port.setObjectName("btn_open_serial_port")
        self.gridLayout_2.addWidget(self.btn_open_serial_port, 22, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 6, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.gridLayout_2.addItem(spacerItem4, 3, 0, 1, 1)
        self.btnClearPeakSearch = QtWidgets.QPushButton(self.groupBox_3)
        self.btnClearPeakSearch.setObjectName("btnClearPeakSearch")
        self.gridLayout_2.addWidget(self.btnClearPeakSearch, 2, 0, 1, 1)
        self.btnPeakSearch = QtWidgets.QPushButton(self.groupBox_3)
        self.btnPeakSearch.setObjectName("btnPeakSearch")
        self.gridLayout_2.addWidget(self.btnPeakSearch, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.graphWidget = PlotWidget(self.centralWidget)
        self.graphWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.graphWidget.setMouseTracking(True)
        self.graphWidget.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.graphWidget.setObjectName("graphWidget")
        self.gridLayout.addWidget(self.graphWidget, 1, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 200))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 200))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.intStepKHz = QtWidgets.QSpinBox(self.groupBox_2)
        self.intStepKHz.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.intStepKHz.setMinimum(1)
        self.intStepKHz.setMaximum(3000000)
        self.intStepKHz.setProperty("value", 7472)
        self.intStepKHz.setObjectName("intStepKHz")
        self.gridLayout_3.addWidget(self.intStepKHz, 3, 5, 1, 1)
        self.floatStopMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.floatStopMHz.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.floatStopMHz.setDecimals(3)
        self.floatStopMHz.setMaximum(3000.0)
        self.floatStopMHz.setSingleStep(0.001)
        self.floatStopMHz.setProperty("value", 3000.0)
        self.floatStopMHz.setObjectName("floatStopMHz")
        self.gridLayout_3.addWidget(self.floatStopMHz, 3, 3, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_3.addItem(spacerItem5, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 0, 3, 1, 1)
        self.floatStartMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.floatStartMHz.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.floatStartMHz.setDecimals(3)
        self.floatStartMHz.setMinimum(0.0)
        self.floatStartMHz.setMaximum(3200.0)
        self.floatStartMHz.setSingleStep(0.001)
        self.floatStartMHz.setProperty("value", 3.0)
        self.floatStartMHz.setObjectName("floatStartMHz")
        self.gridLayout_3.addWidget(self.floatStartMHz, 3, 1, 1, 1)
        self.label_1 = QtWidgets.QLabel(self.groupBox_2)
        self.label_1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_1.setObjectName("label_1")
        self.gridLayout_3.addWidget(self.label_1, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 4, 3, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 4, 5, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_3.addItem(spacerItem6, 3, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 4, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 0, 5, 1, 1)
        self.numFrequencySteps = QtWidgets.QSpinBox(self.groupBox_2)
        self.numFrequencySteps.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.numFrequencySteps.setMinimum(2)
        self.numFrequencySteps.setMaximum(3100000)
        self.numFrequencySteps.setProperty("value", 401)
        self.numFrequencySteps.setObjectName("numFrequencySteps")
        self.gridLayout_3.addWidget(self.numFrequencySteps, 5, 5, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_3.addItem(spacerItem7, 3, 2, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_3.addItem(spacerItem8, 3, 6, 1, 1)
        self.dblCenterMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.dblCenterMHz.setMinimumSize(QtCore.QSize(150, 0))
        self.dblCenterMHz.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dblCenterMHz.setDecimals(3)
        self.dblCenterMHz.setMaximum(10000.0)
        self.dblCenterMHz.setObjectName("dblCenterMHz")
        self.gridLayout_3.addWidget(self.dblCenterMHz, 5, 1, 1, 1)
        self.dblSpanMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.dblSpanMHz.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dblSpanMHz.setDecimals(3)
        self.dblSpanMHz.setObjectName("dblSpanMHz")
        self.gridLayout_3.addWidget(self.dblSpanMHz, 5, 3, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 2, 1, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBox_4.setBaseSize(QtCore.QSize(0, 0))
        self.groupBox_4.setStyleSheet("")
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem9)
        self.btnCalibrate = QtWidgets.QPushButton(self.groupBox_4)
        self.btnCalibrate.setObjectName("btnCalibrate")
        self.horizontalLayout_2.addWidget(self.btnCalibrate)
        self.btn_make_control_dict = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_make_control_dict.setObjectName("btn_make_control_dict")
        self.horizontalLayout_2.addWidget(self.btn_make_control_dict)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem10)
        self.label_8 = QtWidgets.QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.selectReferenceOscillator = QtWidgets.QComboBox(self.groupBox_4)
        self.selectReferenceOscillator.setMinimumSize(QtCore.QSize(0, 30))
        self.selectReferenceOscillator.setObjectName("selectReferenceOscillator")
        self.selectReferenceOscillator.addItem("")
        self.selectReferenceOscillator.addItem("")
        self.selectReferenceOscillator.addItem("")
        self.horizontalLayout_2.addWidget(self.selectReferenceOscillator)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem11)
        self.chk_plot_enable = QtWidgets.QCheckBox(self.groupBox_4)
        self.chk_plot_enable.setChecked(True)
        self.chk_plot_enable.setObjectName("chk_plot_enable")
        self.horizontalLayout_2.addWidget(self.chk_plot_enable)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem12)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectSweepFrequency = QtWidgets.QRadioButton(self.groupBox_4)
        self.selectSweepFrequency.setChecked(True)
        self.selectSweepFrequency.setObjectName("selectSweepFrequency")
        self.horizontalLayout.addWidget(self.selectSweepFrequency)
        self.selectFixedFrequency = QtWidgets.QRadioButton(self.groupBox_4)
        self.selectFixedFrequency.setChecked(False)
        self.selectFixedFrequency.setObjectName("selectFixedFrequency")
        self.horizontalLayout.addWidget(self.selectFixedFrequency)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem13)
        self.gridLayout.addWidget(self.groupBox_4, 0, 0, 1, 3)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 200))
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem14)
        self.btnTrigger = QtWidgets.QPushButton(self.groupBox_5)
        self.btnTrigger.setEnabled(True)
        self.btnTrigger.setObjectName("btnTrigger")
        self.verticalLayout_2.addWidget(self.btnTrigger)
        spacerItem15 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem15)
        self.btnExit = QtWidgets.QPushButton(self.groupBox_5)
        self.btnExit.setObjectName("btnExit")
        self.verticalLayout_2.addWidget(self.btnExit)
        self.gridLayout.addWidget(self.groupBox_5, 2, 2, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_6.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox_6.setMaximumSize(QtCore.QSize(120, 200))
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem16 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem16)
        self.btn_get_arduino_msg = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_get_arduino_msg.setObjectName("btn_get_arduino_msg")
        self.verticalLayout_3.addWidget(self.btn_get_arduino_msg)
        self.btnSweep = QtWidgets.QPushButton(self.groupBox_6)
        self.btnSweep.setObjectName("btnSweep")
        self.verticalLayout_3.addWidget(self.btnSweep)
        self.label_sweep_status = QtWidgets.QLabel(self.groupBox_6)
        self.label_sweep_status.setText("")
        self.label_sweep_status.setObjectName("label_sweep_status")
        self.verticalLayout_3.addWidget(self.label_sweep_status)
        self.line_edit_cmd = QtWidgets.QLineEdit(self.groupBox_6)
        self.line_edit_cmd.setPlaceholderText("")
        self.line_edit_cmd.setObjectName("line_edit_cmd")
        self.verticalLayout_3.addWidget(self.line_edit_cmd)
        spacerItem17 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem17)
        self.gridLayout.addWidget(self.groupBox_6, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.label_graphWidth.setBuddy(self.minGraphWidth)
        self.label_graphHeight.setBuddy(self.minGraphHeight)
        self.label_7.setBuddy(self.numPlotCeiling)
        self.label_6.setBuddy(self.numPlotFloor)
        self.label_3.setBuddy(self.floatStopMHz)
        self.label_1.setBuddy(self.floatStartMHz)
        self.label.setBuddy(self.dblSpanMHz)
        self.label_10.setBuddy(self.numFrequencySteps)
        self.label_2.setBuddy(self.dblCenterMHz)

        self.retranslateUi(MainWindow)
        self.selectReferenceOscillator.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.btnSweep, self.floatStartMHz)
        MainWindow.setTabOrder(self.floatStartMHz, self.floatStopMHz)
        MainWindow.setTabOrder(self.floatStopMHz, self.intStepKHz)
        MainWindow.setTabOrder(self.intStepKHz, self.minGraphWidth)
        MainWindow.setTabOrder(self.minGraphWidth, self.minGraphHeight)
        MainWindow.setTabOrder(self.minGraphHeight, self.cbxSerialPortSelection)
        MainWindow.setTabOrder(self.cbxSerialPortSelection, self.btnPeakSearch)
        MainWindow.setTabOrder(self.btnPeakSearch, self.dbl_attenuator_dB)
        MainWindow.setTabOrder(self.dbl_attenuator_dB, self.numPeakMarkers)
        MainWindow.setTabOrder(self.numPeakMarkers, self.chkArduinoLED)
        MainWindow.setTabOrder(self.chkArduinoLED, self.numPlotFloor)
        MainWindow.setTabOrder(self.numPlotFloor, self.cbxSerialSpeedSelection)
        MainWindow.setTabOrder(self.cbxSerialSpeedSelection, self.chkShowGrid)
        MainWindow.setTabOrder(self.chkShowGrid, self.numPlotCeiling)
        MainWindow.setTabOrder(self.numPlotCeiling, self.btn_open_serial_port)
        MainWindow.setTabOrder(self.btn_open_serial_port, self.btnRefreshPortsList)
        MainWindow.setTabOrder(self.btnRefreshPortsList, self.btnClearPeakSearch)
        MainWindow.setTabOrder(self.btnClearPeakSearch, self.floatSweepStartFreq)
        MainWindow.setTabOrder(self.floatSweepStartFreq, self.floatSweepStopFreq)
        MainWindow.setTabOrder(self.floatSweepStopFreq, self.dblSpanMHz)
        MainWindow.setTabOrder(self.dblSpanMHz, self.dblCenterMHz)
        MainWindow.setTabOrder(self.dblCenterMHz, self.numFrequencySteps)
        MainWindow.setTabOrder(self.numFrequencySteps, self.btnCalibrate)
        MainWindow.setTabOrder(self.btnCalibrate, self.selectReferenceOscillator)
        MainWindow.setTabOrder(self.selectReferenceOscillator, self.chk_plot_enable)
        MainWindow.setTabOrder(self.chk_plot_enable, self.selectSweepFrequency)
        MainWindow.setTabOrder(self.selectSweepFrequency, self.selectFixedFrequency)
        MainWindow.setTabOrder(self.selectFixedFrequency, self.btnTrigger)
        MainWindow.setTabOrder(self.btnTrigger, self.btnExit)
        MainWindow.setTabOrder(self.btnExit, self.btn_get_arduino_msg)
        MainWindow.setTabOrder(self.btn_get_arduino_msg, self.line_edit_cmd)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WN2A Spectrum Analyzer Display"))
        self.label_9.setText(_translate("MainWindow", "Sweep Start"))
        self.label_11.setText(_translate("MainWindow", "Sweep Stop"))
        self.label_graphWidth.setText(_translate("MainWindow", "Min Graph Width"))
        self.label_graphHeight.setText(_translate("MainWindow", "Min Graph Height"))
        self.chkArduinoLED.setText(_translate("MainWindow", "ArduinoLED"))
        self.label_13.setText(_translate("MainWindow", "Attenuator (dB)"))
        self.label_12.setText(_translate("MainWindow", "Serial Speed"))
        self.label_5.setText(_translate("MainWindow", "Serial Port"))
        self.cbxSerialPortSelection.setToolTip(_translate("MainWindow", "These are all the serial ports found on your system"))
        self.cbxSerialPortSelection.setWhatsThis(_translate("MainWindow", "List of all serial ports"))
        self.cbxSerialPortSelection.setAccessibleName(_translate("MainWindow", "List of all serial ports"))
        self.btnRefreshPortsList.setText(_translate("MainWindow", "Refresh Ports"))
        self.label_7.setText(_translate("MainWindow", "Plot Ceiling"))
        self.chkShowGrid.setText(_translate("MainWindow", "Grid"))
        self.btn_open_serial_port.setText(_translate("MainWindow", "Open Port"))
        self.label_6.setText(_translate("MainWindow", "Plot Floor"))
        self.btnClearPeakSearch.setText(_translate("MainWindow", "Clear Peak"))
        self.btnPeakSearch.setText(_translate("MainWindow", "Peak Search"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Frequency Controls"))
        self.label_3.setText(_translate("MainWindow", "Stop (MHz)"))
        self.label_1.setText(_translate("MainWindow", "Start (MHz)"))
        self.label.setText(_translate("MainWindow", "Span (Mhz)"))
        self.label_10.setText(_translate("MainWindow", "Data Points"))
        self.label_2.setText(_translate("MainWindow", "Center (MHz)"))
        self.label_4.setText(_translate("MainWindow", "Step  Size (kHz)"))
        self.btnCalibrate.setText(_translate("MainWindow", "Calibrate"))
        self.btn_make_control_dict.setText(_translate("MainWindow", "Make Control"))
        self.label_8.setText(_translate("MainWindow", "Reference Clock (MHz)"))
        self.selectReferenceOscillator.setItemText(0, _translate("MainWindow", "All Off"))
        self.selectReferenceOscillator.setItemText(1, _translate("MainWindow", "Ref1"))
        self.selectReferenceOscillator.setItemText(2, _translate("MainWindow", "Ref2"))
        self.chk_plot_enable.setText(_translate("MainWindow", "Enable Plotting"))
        self.selectSweepFrequency.setText(_translate("MainWindow", "Sweep"))
        self.selectFixedFrequency.setText(_translate("MainWindow", "Fixed"))
        self.btnTrigger.setText(_translate("MainWindow", "Serial End Msg"))
        self.btnExit.setText(_translate("MainWindow", "Exit"))
        self.btn_get_arduino_msg.setText(_translate("MainWindow", "Arduino Message"))
        self.btnSweep.setText(_translate("MainWindow", "Sweep"))
from pyqtgraph import PlotWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
