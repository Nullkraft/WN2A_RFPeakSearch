# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/mark/projects/python/WN2A_RFPeakSearch/ui/mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1533, 996)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox.setMinimumSize(QtCore.QSize(130, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(130, 16777215))
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
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
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnZeroSpan = QtWidgets.QPushButton(self.groupBox)
        self.btnZeroSpan.setObjectName("btnZeroSpan")
        self.verticalLayout.addWidget(self.btnZeroSpan)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.btnFullSpan = QtWidgets.QPushButton(self.groupBox)
        self.btnFullSpan.setObjectName("btnFullSpan")
        self.verticalLayout.addWidget(self.btnFullSpan)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        self.btnLastSpan = QtWidgets.QPushButton(self.groupBox)
        self.btnLastSpan.setObjectName("btnLastSpan")
        self.verticalLayout.addWidget(self.btnLastSpan)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
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
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.gridLayout.addWidget(self.groupBox, 1, 2, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_3.setMinimumSize(QtCore.QSize(120, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(120, 16777215))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btn_disable_LO2_RFout = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_disable_LO2_RFout.setObjectName("btn_disable_LO2_RFout")
        self.gridLayout_2.addWidget(self.btn_disable_LO2_RFout, 13, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 4, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 21, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 6, 0, 1, 1)
        self.numPeakMarkers = QtWidgets.QSpinBox(self.groupBox_3)
        self.numPeakMarkers.setMinimum(1)
        self.numPeakMarkers.setMaximum(25)
        self.numPeakMarkers.setProperty("value", 3)
        self.numPeakMarkers.setObjectName("numPeakMarkers")
        self.gridLayout_2.addWidget(self.numPeakMarkers, 1, 0, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem6, 11, 0, 1, 1)
        self.numPlotFloor = QtWidgets.QSpinBox(self.groupBox_3)
        self.numPlotFloor.setMinimum(-200)
        self.numPlotFloor.setMaximum(30)
        self.numPlotFloor.setProperty("value", -90)
        self.numPlotFloor.setObjectName("numPlotFloor")
        self.gridLayout_2.addWidget(self.numPlotFloor, 7, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setMinimumSize(QtCore.QSize(85, 0))
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 16, 0, 1, 1)
        self.cbxSerialPortSelection = QtWidgets.QComboBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxSerialPortSelection.sizePolicy().hasHeightForWidth())
        self.cbxSerialPortSelection.setSizePolicy(sizePolicy)
        self.cbxSerialPortSelection.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cbxSerialPortSelection.setObjectName("cbxSerialPortSelection")
        self.gridLayout_2.addWidget(self.cbxSerialPortSelection, 17, 0, 1, 1)
        self.btnPeakSearch = QtWidgets.QPushButton(self.groupBox_3)
        self.btnPeakSearch.setObjectName("btnPeakSearch")
        self.gridLayout_2.addWidget(self.btnPeakSearch, 0, 0, 1, 1)
        self.chkShowGrid = QtWidgets.QCheckBox(self.groupBox_3)
        self.chkShowGrid.setWhatsThis("")
        self.chkShowGrid.setObjectName("chkShowGrid")
        self.gridLayout_2.addWidget(self.chkShowGrid, 15, 0, 1, 1, QtCore.Qt.AlignHCenter)
        spacerItem7 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem7, 3, 0, 1, 1)
        self.chkArduinoLED = QtWidgets.QCheckBox(self.groupBox_3)
        self.chkArduinoLED.setMinimumSize(QtCore.QSize(110, 0))
        self.chkArduinoLED.setChecked(True)
        self.chkArduinoLED.setObjectName("chkArduinoLED")
        self.gridLayout_2.addWidget(self.chkArduinoLED, 14, 0, 1, 1)
        self.cbxSerialSpeedSelection = QtWidgets.QComboBox(self.groupBox_3)
        self.cbxSerialSpeedSelection.setMinimumSize(QtCore.QSize(85, 0))
        self.cbxSerialSpeedSelection.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cbxSerialSpeedSelection.setObjectName("cbxSerialSpeedSelection")
        self.gridLayout_2.addWidget(self.cbxSerialSpeedSelection, 20, 0, 1, 1)
        self.numPlotCeiling = QtWidgets.QSpinBox(self.groupBox_3)
        self.numPlotCeiling.setMinimum(-190)
        self.numPlotCeiling.setMaximum(30)
        self.numPlotCeiling.setProperty("value", -40)
        self.numPlotCeiling.setObjectName("numPlotCeiling")
        self.gridLayout_2.addWidget(self.numPlotCeiling, 5, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 19, 0, 1, 1)
        self.btnClearPeakSearch = QtWidgets.QPushButton(self.groupBox_3)
        self.btnClearPeakSearch.setObjectName("btnClearPeakSearch")
        self.gridLayout_2.addWidget(self.btnClearPeakSearch, 2, 0, 1, 1)
        self.btnRefreshPortsList = QtWidgets.QPushButton(self.groupBox_3)
        self.btnRefreshPortsList.setObjectName("btnRefreshPortsList")
        self.gridLayout_2.addWidget(self.btnRefreshPortsList, 18, 0, 1, 1)
        self.btn_disable_LO3_RFout = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_disable_LO3_RFout.setObjectName("btn_disable_LO3_RFout")
        self.gridLayout_2.addWidget(self.btn_disable_LO3_RFout, 12, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.graphWidget = PlotWidget(self.centralWidget)
        self.graphWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.graphWidget.setObjectName("graphWidget")
        self.gridLayout.addWidget(self.graphWidget, 1, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 200))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 200))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.dblCenterMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.dblCenterMHz.setMinimumSize(QtCore.QSize(150, 0))
        self.dblCenterMHz.setDecimals(6)
        self.dblCenterMHz.setObjectName("dblCenterMHz")
        self.gridLayout_3.addWidget(self.dblCenterMHz, 3, 2, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem8, 3, 1, 1, 1)
        self.dblStepKHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.dblStepKHz.setDecimals(6)
        self.dblStepKHz.setMaximum(9999.0)
        self.dblStepKHz.setProperty("value", 10.0)
        self.dblStepKHz.setObjectName("dblStepKHz")
        self.gridLayout_3.addWidget(self.dblStepKHz, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 4, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 0, 4, 1, 1)
        self.dblSpanMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.dblSpanMHz.setDecimals(6)
        self.dblSpanMHz.setObjectName("dblSpanMHz")
        self.gridLayout_3.addWidget(self.dblSpanMHz, 5, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 2, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem9, 3, 3, 1, 1)
        self.label_1 = QtWidgets.QLabel(self.groupBox_2)
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_1.setObjectName("label_1")
        self.gridLayout_3.addWidget(self.label_1, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 4, 0, 1, 1)
        self.floatStartMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.floatStartMHz.setDecimals(6)
        self.floatStartMHz.setMinimum(23.5)
        self.floatStartMHz.setMaximum(3200.0)
        self.floatStartMHz.setSingleStep(0.5)
        self.floatStartMHz.setProperty("value", 23.5)
        self.floatStartMHz.setObjectName("floatStartMHz")
        self.gridLayout_3.addWidget(self.floatStartMHz, 3, 0, 1, 1)
        self.floatStopMHz = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.floatStopMHz.setDecimals(5)
        self.floatStopMHz.setMaximum(3200.0)
        self.floatStopMHz.setSingleStep(0.001)
        self.floatStopMHz.setProperty("value", 3200.0)
        self.floatStopMHz.setObjectName("floatStopMHz")
        self.gridLayout_3.addWidget(self.floatStopMHz, 3, 4, 1, 1)
        self.numFrequencySteps = QtWidgets.QSpinBox(self.groupBox_2)
        self.numFrequencySteps.setMinimum(2)
        self.numFrequencySteps.setMaximum(401)
        self.numFrequencySteps.setObjectName("numFrequencySteps")
        self.gridLayout_3.addWidget(self.numFrequencySteps, 5, 4, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 4, 4, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 2, 1, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBox_4.setBaseSize(QtCore.QSize(0, 0))
        self.groupBox_4.setStyleSheet("")
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem10)
        self.label_8 = QtWidgets.QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.selectReferenceOscillator = QtWidgets.QComboBox(self.groupBox_4)
        self.selectReferenceOscillator.setObjectName("selectReferenceOscillator")
        self.selectReferenceOscillator.addItem("")
        self.selectReferenceOscillator.addItem("")
        self.horizontalLayout_2.addWidget(self.selectReferenceOscillator)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem11)
        self.chkLockDetect = QtWidgets.QCheckBox(self.groupBox_4)
        self.chkLockDetect.setChecked(True)
        self.chkLockDetect.setObjectName("chkLockDetect")
        self.horizontalLayout_2.addWidget(self.chkLockDetect)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem12)
        self.chkFracOpt = QtWidgets.QCheckBox(self.groupBox_4)
        self.chkFracOpt.setObjectName("chkFracOpt")
        self.horizontalLayout_2.addWidget(self.chkFracOpt)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem13)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectSweepFrequency = QtWidgets.QRadioButton(self.groupBox_4)
        self.selectSweepFrequency.setObjectName("selectSweepFrequency")
        self.horizontalLayout.addWidget(self.selectSweepFrequency)
        self.selectFixedFrequency = QtWidgets.QRadioButton(self.groupBox_4)
        self.selectFixedFrequency.setChecked(True)
        self.selectFixedFrequency.setObjectName("selectFixedFrequency")
        self.horizontalLayout.addWidget(self.selectFixedFrequency)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem14)
        self.gridLayout.addWidget(self.groupBox_4, 0, 0, 1, 3)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btnTrigger = QtWidgets.QPushButton(self.groupBox_5)
        self.btnTrigger.setEnabled(True)
        self.btnTrigger.setObjectName("btnTrigger")
        self.verticalLayout_2.addWidget(self.btnTrigger)
        self.numDataPoints = QtWidgets.QSpinBox(self.groupBox_5)
        self.numDataPoints.setMinimum(256)
        self.numDataPoints.setMaximum(1792)
        self.numDataPoints.setSingleStep(64)
        self.numDataPoints.setProperty("value", 512)
        self.numDataPoints.setObjectName("numDataPoints")
        self.verticalLayout_2.addWidget(self.numDataPoints)
        spacerItem15 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem15)
        spacerItem16 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem16)
        self.btnExit = QtWidgets.QPushButton(self.groupBox_5)
        self.btnExit.setObjectName("btnExit")
        self.verticalLayout_2.addWidget(self.btnExit)
        spacerItem17 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem17)
        self.gridLayout.addWidget(self.groupBox_5, 2, 2, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_6.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox_6.setMaximumSize(QtCore.QSize(120, 200))
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem18 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem18)
        self.btn_get_arduino_msg = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_get_arduino_msg.setObjectName("btn_get_arduino_msg")
        self.verticalLayout_3.addWidget(self.btn_get_arduino_msg)
        self.btnSweep = QtWidgets.QPushButton(self.groupBox_6)
        self.btnSweep.setObjectName("btnSweep")
        self.verticalLayout_3.addWidget(self.btnSweep)
        self.btnSendRegisters = QtWidgets.QPushButton(self.groupBox_6)
        self.btnSendRegisters.setObjectName("btnSendRegisters")
        self.verticalLayout_3.addWidget(self.btnSendRegisters)
        self.btn_reinitialize = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_reinitialize.setObjectName("btn_reinitialize")
        self.verticalLayout_3.addWidget(self.btn_reinitialize)
        self.line_edit_cmd = QtWidgets.QLineEdit(self.groupBox_6)
        self.line_edit_cmd.setPlaceholderText("")
        self.line_edit_cmd.setObjectName("line_edit_cmd")
        self.verticalLayout_3.addWidget(self.line_edit_cmd)
        spacerItem19 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem19)
        self.gridLayout.addWidget(self.groupBox_6, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.label_graphWidth.setBuddy(self.minGraphWidth)
        self.label_graphHeight.setBuddy(self.minGraphHeight)
        self.label_7.setBuddy(self.numPlotCeiling)
        self.label_6.setBuddy(self.numPlotFloor)
        self.label.setBuddy(self.dblSpanMHz)
        self.label_3.setBuddy(self.floatStopMHz)
        self.label_2.setBuddy(self.dblCenterMHz)
        self.label_1.setBuddy(self.floatStartMHz)
        self.label_4.setBuddy(self.dblStepKHz)
        self.label_10.setBuddy(self.numFrequencySteps)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WN2A Spectrum Analyzer Display"))
        self.label_9.setText(_translate("MainWindow", "Sweep Start"))
        self.label_11.setText(_translate("MainWindow", "Sweep Stop"))
        self.btnZeroSpan.setText(_translate("MainWindow", "Zero Span"))
        self.btnFullSpan.setText(_translate("MainWindow", "Full Span"))
        self.btnLastSpan.setText(_translate("MainWindow", "Last Span"))
        self.label_graphWidth.setText(_translate("MainWindow", "Min Graph Width"))
        self.label_graphHeight.setText(_translate("MainWindow", "Min Graph Height"))
        self.btn_disable_LO2_RFout.setText(_translate("MainWindow", "Disable LO2"))
        self.label_7.setText(_translate("MainWindow", "Plot Ceiling"))
        self.label_6.setText(_translate("MainWindow", "Plot Floor"))
        self.label_5.setText(_translate("MainWindow", "Serial Port"))
        self.cbxSerialPortSelection.setToolTip(_translate("MainWindow", "These are all the serial ports found on your system"))
        self.cbxSerialPortSelection.setWhatsThis(_translate("MainWindow", "List of all serial ports"))
        self.cbxSerialPortSelection.setAccessibleName(_translate("MainWindow", "List of all serial ports"))
        self.btnPeakSearch.setText(_translate("MainWindow", "Peak Search"))
        self.chkShowGrid.setText(_translate("MainWindow", "Grid"))
        self.chkArduinoLED.setText(_translate("MainWindow", "ArduinoLED"))
        self.label_12.setText(_translate("MainWindow", "Serial Speed"))
        self.btnClearPeakSearch.setText(_translate("MainWindow", "Clear Peak"))
        self.btnRefreshPortsList.setText(_translate("MainWindow", "New Ports"))
        self.btn_disable_LO3_RFout.setText(_translate("MainWindow", "Disable LO3"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Frequency Controls"))
        self.label.setText(_translate("MainWindow", "Span (Mhz)"))
        self.label_3.setText(_translate("MainWindow", "Stop (MHz)"))
        self.label_2.setText(_translate("MainWindow", "Center (MHz)"))
        self.label_1.setText(_translate("MainWindow", "Start (MHz)"))
        self.label_4.setText(_translate("MainWindow", "Step (kHz)"))
        self.label_10.setText(_translate("MainWindow", "Number of Steps"))
        self.label_8.setText(_translate("MainWindow", "Reference Clock (MHz)"))
        self.selectReferenceOscillator.setItemText(0, _translate("MainWindow", "60 MHz"))
        self.selectReferenceOscillator.setItemText(1, _translate("MainWindow", "100 MHz"))
        self.chkLockDetect.setText(_translate("MainWindow", "Lock Detect"))
        self.chkFracOpt.setText(_translate("MainWindow", "Fractional Optimization"))
        self.selectSweepFrequency.setText(_translate("MainWindow", "Sweep"))
        self.selectFixedFrequency.setText(_translate("MainWindow", "Fixed"))
        self.btnTrigger.setText(_translate("MainWindow", "Trigger"))
        self.btnExit.setText(_translate("MainWindow", "Exit"))
        self.btn_get_arduino_msg.setText(_translate("MainWindow", "Arduino Message"))
        self.btnSweep.setText(_translate("MainWindow", "Sweep"))
        self.btnSendRegisters.setText(_translate("MainWindow", "Transmit"))
        self.btn_reinitialize.setText(_translate("MainWindow", "Re-Initialize"))
from pyqtgraph import PlotWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
