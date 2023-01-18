from PyQt6 import QtWidgets, QtCore

class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, mark, row, col, *__args):
        super().__init__(*__args)
        self.mark = mark
        self.row = row
        self.col = col

        self.originIsCheck = self.isChecked()
    checkIndexChange = QtCore.pyqtSignal(str, int, int, int)

    def event(self, QEvent):  # real signature unknown; restored from __doc__
        """ event(self, QEvent) -> bool """
        # print('aa', self.isChecked(), self.col, self.row, self.originIsCheck)
        # return False
        if self.isChecked() != self.originIsCheck:
            self.checkIndexChange.emit(self.mark, 1 if self.isChecked() else 0, self.row, self.col)
            self.originIsCheck = self.isChecked()

        return super(CheckBox, self).event(QEvent)

    def setChecked(self, bool):  # real signature unknown; restored from __doc__
        """ setChecked(self, bool) """
        super(CheckBox, self).setChecked(bool)
        self.originIsCheck = bool
