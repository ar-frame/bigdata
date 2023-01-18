from PyQt6 import QtWidgets, QtCore

class DoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, mark, *__args):
        super().__init__(*__args)
        self.mark = mark
        self.origin_value = self.value()

    spinIndexChange = QtCore.pyqtSignal(str, float)

    def event(self, QEvent):  # real signature unknown; restored from __doc__
        """ event(self, QEvent) -> bool """
        # print('aa', self.isChecked(), self.col, self.row, self.originIsCheck)
        # return False
        # print('eee', self.value())
        if self.origin_value != self.value():
            self.spinIndexChange.emit(self.mark, self.value())
            self.origin_value = self.value()
        return super(DoubleSpinBox, self).event(QEvent)

    def setValue(self, val: float) -> None:
        self.origin_value = val
        return super(DoubleSpinBox, self).setValue(val)