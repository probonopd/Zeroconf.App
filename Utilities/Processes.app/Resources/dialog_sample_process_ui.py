# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './dialog_sample_process.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SampleProcess(object):
    def setupUi(self, SampleProcess):
        SampleProcess.setObjectName("SampleProcess")
        SampleProcess.resize(692, 427)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SampleProcess)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(SampleProcess)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.comboBox = QtWidgets.QComboBox(SampleProcess)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.buttonRefresh = QtWidgets.QPushButton(SampleProcess)
        self.buttonRefresh.setObjectName("buttonRefresh")
        self.horizontalLayout_4.addWidget(self.buttonRefresh)
        self.buttonSave = QtWidgets.QPushButton(SampleProcess)
        self.buttonSave.setObjectName("buttonSave")
        self.horizontalLayout_4.addWidget(self.buttonSave)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.StatusText = QtWidgets.QLabel(SampleProcess)
        self.StatusText.setEnabled(False)
        self.StatusText.setAlignment(QtCore.Qt.AlignCenter)
        self.StatusText.setObjectName("StatusText")
        self.verticalLayout_3.addWidget(self.StatusText)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.textBrowser = QtWidgets.QTextBrowser(SampleProcess)
        font = QtGui.QFont()
        font.setFamily("Roboto Mono for Powerline")
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout_3.addWidget(self.textBrowser)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonClose = QtWidgets.QPushButton(SampleProcess)
        self.buttonClose.setDefault(True)
        self.buttonClose.setObjectName("buttonClose")
        self.horizontalLayout.addWidget(self.buttonClose)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(SampleProcess)
        self.comboBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(SampleProcess)

    def retranslateUi(self, SampleProcess):
        _translate = QtCore.QCoreApplication.translate
        SampleProcess.setWindowTitle(_translate("SampleProcess", "Sample of %s"))
        self.label_2.setText(_translate("SampleProcess", "Display"))
        self.comboBox.setItemText(0, _translate("SampleProcess", "Sample Text"))
        self.comboBox.setItemText(1, _translate("SampleProcess", "Sample Markdown"))
        self.buttonRefresh.setText(_translate("SampleProcess", "Refresh"))
        self.buttonSave.setText(_translate("SampleProcess", "Save..."))
        self.StatusText.setText(_translate("SampleProcess", "Process with pid %s sampled %s times"))
        self.textBrowser.setHtml(_translate("SampleProcess", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Roboto Mono for Powerline\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Roboto\';\"><br /></p></body></html>"))
        self.buttonClose.setText(_translate("SampleProcess", "Close"))
