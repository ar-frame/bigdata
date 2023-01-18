from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton
from PyQt6 import QtCore
class PushButton(QPushButton):
    # clicked=pyqtSignal()
    clicked = QtCore.pyqtSignal(str)
    # def __init(self, parent):
    #     QLabel.__init__(self, QMouseEvent)

    def __init__(self, mark, *__args):  # real signature unknown; restored from __doc__ with multiple overloads
        super().__init__(*__args)
        self.mark = mark

    def mousePressEvent(self, ev):
        self.clicked.emit(self.mark)