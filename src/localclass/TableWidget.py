from PyQt6 import QtWidgets, QtCore

class TableWidget(QtWidgets.QTableWidget):
    def __init__(self, mark, *__args):
        super().__init__(*__args)
        self.mark = mark
        self.init_last_item()
    def init_last_item(self):
        self.last_item = {"col": -1, "row": -1, "val": ""}

    cellLastCheckChanged = QtCore.pyqtSignal(str, int, int, str)

    def edit(self, index, trigger, event):
        print('eeee', event, index.row(), index.column())

        try:
            if self.last_item['col'] > -1:
                row = self.last_item['row']
                col = self.last_item['col']
                newval = self.item(row, col).text().strip()
                if self.last_item['val'] != newval:
                    self.cellLastCheckChanged.emit(self.mark, row, col, newval)
                self.init_last_item()

            if index.row() > -1:
                self.last_item['row'] = index.row()
                self.last_item['col'] = index.column()
                self.last_item['val'] = self.item(index.row(), index.column()).text()
        except Exception as e:
            print(e)

        result = super(TableWidget, self).edit(index, trigger, event)
        return result