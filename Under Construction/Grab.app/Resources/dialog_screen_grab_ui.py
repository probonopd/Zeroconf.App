# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './dialog_screen_grab.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ScreenGrabDialog(object):
    def setupUi(self, ScreenGrabDialog):
        ScreenGrabDialog.setObjectName("ScreenGrabDialog")
        ScreenGrabDialog.setWindowModality(QtCore.Qt.WindowModal)
        ScreenGrabDialog.resize(493, 206)
        ScreenGrabDialog.setFocusPolicy(QtCore.Qt.NoFocus)
        ScreenGrabDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ScreenGrabDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.MainVbox = QtWidgets.QVBoxLayout()
        self.MainVbox.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.MainVbox.setContentsMargins(0, 0, 0, 0)
        self.MainVbox.setSpacing(6)
        self.MainVbox.setObjectName("MainVbox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.icon = QtWidgets.QLabel(ScreenGrabDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon.sizePolicy().hasHeightForWidth())
        self.icon.setSizePolicy(sizePolicy)
        self.icon.setMinimumSize(QtCore.QSize(64, 64))
        self.icon.setMaximumSize(QtCore.QSize(64, 64))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap("./../../../../../../Processes.app/Resources/Processes.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout_2.addWidget(self.icon, 0, QtCore.Qt.AlignLeft)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Label = QtWidgets.QLabel(ScreenGrabDialog)
        font = QtGui.QFont()
        font.setFamily("Nimbus Sans")
        self.Label.setFont(font)
        self.Label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.Label.setWordWrap(True)
        self.Label.setObjectName("Label")
        self.verticalLayout_2.addWidget(self.Label)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.MainVbox.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.MainVbox.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setSpacing(22)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.button_cancel = QtWidgets.QPushButton(ScreenGrabDialog)
        self.button_cancel.setDefault(True)
        self.button_cancel.setObjectName("button_cancel")
        self.horizontalLayout.addWidget(self.button_cancel)
        self.MainVbox.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.MainVbox)

        self.retranslateUi(ScreenGrabDialog)
        QtCore.QMetaObject.connectSlotsByName(ScreenGrabDialog)

    def retranslateUi(self, ScreenGrabDialog):
        _translate = QtCore.QCoreApplication.translate
        ScreenGrabDialog.setWindowTitle(_translate("ScreenGrabDialog", "Screen Grab"))
        self.Label.setText(_translate("ScreenGrabDialog", "To capture the screen, click outside this window. (This window will not be included in the screen capture.) If you selected a pointer in Grab preferences, the pointer will be superimposed where you click."))
        self.button_cancel.setText(_translate("ScreenGrabDialog", "Cancel"))
