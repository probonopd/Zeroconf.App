#!/usr/bin/env python3

# Calculator Construction Set
# for a fun story, see
# https://www.folklore.org/StoryView.py?story=Calculator_Construction_Set.txt
# https://doc.qt.io/qtforpython-5/overviews/qtwidgets-widgets-calculator-example.html#calculator-example

# Based on PyCalc
# https://github.com/realpython/materials/tree/master/pyqt-calculator-tutorial/pycalc
#
# The MIT License (MIT)
#
# Copyright (c) 2019, Leodanis Pozo Ramos
# Portions Copyright (c) 2020, Simon Peter <probono@puredarwin.org>
# Portions Copyright (c) 2023, Jérôme Ornech alias Hierosme
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""PyCalc is a simple calculator built using Python and PyQt5."""

import os, sys

from functools import partial

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QPixmap, QColor, QIcon

# The Main Window
from main_window_ui import Ui_MainWindow

from widget_calculator_button import CalculatorButton
from dialog_paper_tape import PaperTape

__version__ = "0.2"
__author__ = [
    "Leodanis Pozo Ramos & Contributors",
    "Jérôme ORNECH alias Hierosme"
]

ERROR_MSG = "ERROR"
TILE_WIDTH = 36
TILE_HEIGHT = 34
TILE_SPACING = 0


# Create a subclass of QMainWindow to setup the calculator's GUI
class Window(QMainWindow, Ui_MainWindow):
    """PyCalc's View (GUI)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paper_tape_dialog = None

        self.setupUi(self)
        self.setupCustomUi()

        self._createButtons()

        self.setupInitialState()
        self.connectSignalsSlots()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Calculator.png")))

    def setupInitialState(self):
        self.display.setAlignment(Qt.AlignRight)
        # self.display.setReadOnly(False)

    def connectSignalsSlots(self):

        # Menu and ToolBar
        self.ActionMenuHelpAbout.triggered.connect(self._showAboutDialog)
        self.actionView_Show_Paper_Tape.triggered.connect(self._showPaperTape)

    def setupCustomUi(self):
        # Paper Tape
        self.paper_tape_dialog = PaperTape()
        self.paper_tape_dialog.hide()

    def _createButtons(self):
        """Create the buttons."""
        self.buttons = {}
        # self.basic_buttons_layout = QGridLayout()
        # self.basic_buttons_layout.setSpacing(TILE_SPACING)
        # Button text | position on the QGridLayout
        buttons = {
            # First Line
            "MC": (0, 0),
            "M+": (0, 1),
            "M-": (0, 2),
            "MR": (0, 3),
            # Second line
            "C": (1, 0),
            "±": (1, 1),
            "÷": (1, 2),
            "×": (1, 3),
            # Third line
            "7": (2, 0),
            "8": (2, 1),
            "9": (2, 2),
            "−": (2, 3),
            # etc ...
            "4": (3, 0),
            "5": (3, 1),
            "6": (3, 2),
            "+": (3, 3),
            "1": (4, 0),
            "2": (4, 1),
            "3": (4, 2),
            "=": (4, 3),
            # the last line got only 2 buttons
            "0": (5, 0),
            ".": (5, 2),
        }
        # Create the buttons and add them to the grid layout
        for btnText, pos in buttons.items():
            self.buttons[btnText] = CalculatorButton()
            self.buttons[btnText].setText(btnText)
            # Spanning management
            # self.buttons[btnText].setMinimumWidth(TILE_WIDTH)
            self.buttons[btnText].setMinimumHeight(TILE_HEIGHT)

            # Apply Color
            if btnText in ["−", "±", "÷", "×", "+", "MC", "M+", "M-", "MR"]:
                self.buttons[btnText].setColor(QColor("#7a7a7b"))
                self.buttons[btnText].setColorFont(QColor("#f7f6f6"))
            elif btnText == "=":
                self.buttons[btnText].setColor(QColor("#f09648"))
                self.buttons[btnText].setColorFont(QColor("#ffffff"))
            elif btnText == "C":
                self.buttons[btnText].setColor(QColor("#f0003b"))
                self.buttons[btnText].setColorFont(QColor("#ffffff"))
            else:
                self.buttons[btnText].setColor(QColor("#eeeeed"))
                self.buttons[btnText].setColorFont(QColor("#3f3f3f"))

            if btnText == "=":
                self.buttons[btnText].setMinimumHeight((TILE_HEIGHT * 2) + 3)
                # helloSystem can t make vertical padding on a button
                self.basic_buttons_layout.addWidget(self.buttons[btnText], pos[0], pos[1], 2, 1)
            elif btnText == "0":
                # self.buttons[btnText].setMinimumWidth(TILE_WIDTH * 2)
                self.basic_buttons_layout.addWidget(self.buttons[btnText], pos[0], pos[1], 1, 2)
            else:
                self.basic_buttons_layout.addWidget(self.buttons[btnText], pos[0], pos[1], 1, 1)
        # # Add buttonsLayout to the general layout
        # self.generalLayout.addLayout(self.basic_buttons_layout)

    def setDisplayText(self, text):
        """Set display's text."""
        self.display.setText(text)
        self.display.setFocus()

    def displayText(self):
        """Get display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText("")

    def closeEvent(self, evnt):
        self.paper_tape_dialog.have_to_close = True
        self.paper_tape_dialog.close()

        super(Window, self).closeEvent(evnt)

    def _showAboutDialog(self):
        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setIconPixmap(
            QPixmap(
                os.path.join(
                    os.path.dirname(__file__),
                    "Calculator.png"
                )
            ).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        for candidate in ["COPYRIGHT", "COPYING", "LICENSE"]:
            if os.path.exists(os.path.join(os.path.dirname(__file__), candidate)):
                with open(os.path.join(os.path.dirname(__file__), candidate), 'r') as file:
                    data = file.read()
                msg.setDetailedText(data)
        msg.setText("<h3>Calculator</h3>")
        msg.setInformativeText(
            "A simple calculator application written in PyQt5<br><br>"
            "<a href='https://github.com/helloSystem/Utilities'>https://github.com/helloSystem/Utilities</a>")
        msg.exec()

    def _showPaperTape(self):
        if self.paper_tape_dialog.isVisible():
            self.paper_tape_dialog.hide()
        else:
            self.paper_tape_dialog.show()
        self.activateWindow()
        self.setFocus()


# Create a Model to handle the calculator's operation
def evaluateExpression(expression):
    """Evaluate an expression."""
    if "÷" in expression:
        expression = expression.replace("÷", "/")
    if "×" in expression:
        expression = expression.replace("×", "*")
    if "−" in expression:
        expression = expression.replace("−", "-")
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG

    return result


# Create a Controller class to connect the GUI and the model
class PyCalcCtrl:
    """PyCalc's Controller."""

    def __init__(self, model, view):
        """Controller initializer."""
        self._evaluate = model
        self._view = view
        self._memory = None
        self.memory = None
        # Connect signals and slots
        self._connectSignals()

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, value):
        if value is None:
            self._memory = None
            return
        if self.memory != value:
            self._memory = value

    def _calculateResult(self):
        """Evaluate expressions."""

        result = self._evaluate(expression=self._view.displayText())
        if result:
            self._view.paper_tape_dialog.plainTextEdit.setPlainText(
                "%s\n\n%s" % (self._view.paper_tape_dialog.plainTextEdit.toPlainText(),
                              self._view.displayText()))
            self._view.paper_tape_dialog.plainTextEdit.setPlainText(
                "%s\n= %s" % (self._view.paper_tape_dialog.plainTextEdit.toPlainText(),
                              result))
        self._view.setDisplayText(result)

    def _memory_clear(self):
        """Clear momory by set value to None"""
        self.memory = None
        self._view.display.setFocus()

    def _memory_substact(self):
        """Add the result of display expression to the memory"""
        result = self._evaluate(expression=self._view.displayText())
        if result and "ERROR" not in result:
            if self.memory is None:
                self.memory = 0
            if "." in result:
                if self.memory:
                    self.memory -= float(result)
            else:
                self.memory -= int(result)
        self._view.display.setFocus()

    def _memory_add(self):
        """Substract the result of display expression to the memory"""
        result = self._evaluate(expression=self._view.displayText())
        if result and "ERROR" not in result:
            if self.memory is None:
                self.memory = 0
            if "." in result:
                self.memory += float(result)
            else:
                self.memory += int(result)
        self._view.display.setFocus()

    def _memory_print(self):
        """If memory value, flush the display with it value"""
        if self.memory is not None:
            self._view.clearDisplay()
            self._view.setDisplayText("%s" % (self.memory))
        else:
            self._view.display.setFocus()

    def _neg(self):
        """Evaluate expressions value and display the negative value"""
        result = self._evaluate(expression=self._view.displayText())
        if result and "ERROR" not in result:
            if "." in result:
                if float(result) > 0:
                    result = -abs(float(result))
                else:
                    result = abs(float(result))
            else:
                if int(result) > 0:
                    result = -abs(int(result))
                else:
                    result = abs(int(result))

        self._view.setDisplayText(str(result))

    def _buildExpression(self, sub_exp):
        """Build expression."""
        if self._view.displayText() == ERROR_MSG:
            self._view.clearDisplay()

        expression = self._view.displayText() + sub_exp
        self._view.setDisplayText(expression)

    def _connectSignals(self):
        """Connect signals and slots."""
        for btnText, btn in self._view.buttons.items():
            if btnText not in {"=", "C", "MC", "M+", "M-", "MR", "±"}:
                btn.clicked.connect(partial(self._buildExpression, btnText))

        self._view.buttons["="].clicked.connect(self._calculateResult)
        self._view.display.returnPressed.connect(self._calculateResult)
        self._view.buttons["C"].clicked.connect(self._view.clearDisplay)
        self._view.buttons["±"].clicked.connect(self._neg)
        self._view.buttons["MC"].clicked.connect(self._memory_clear)
        self._view.buttons["M+"].clicked.connect(self._memory_add)
        self._view.buttons["M-"].clicked.connect(self._memory_substact)
        self._view.buttons["MR"].clicked.connect(self._memory_print)
        """self._view.display.escapePressed.connect(self._view.clearDisplay)"""


# Client code
# def main():
#     """Main function."""
#     # Create an instance of `QApplication`
#     pycalc = QApplication(sys.argv)
#     # Show the calculator's GUI
#     view = PyCalcUi()
#     view.show()
#     # Create instances of the model and the controller
#     model = evaluateExpression
#     PyCalcCtrl(model=model, view=view)
#     # Execute calculator's main loop
#     sys.exit(pycalc.exec_())
#
#
# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    model = evaluateExpression
    PyCalcCtrl(model=model, view=win)
    # Execute calculator's main loop

    sys.exit(app.exec())
