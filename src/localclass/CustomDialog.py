from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

from PyQt6 import QtCore

class CustomDialog(QDialog):
    def __init__(self, title, info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(info)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # def accept(self) -> None:
    #     print('acc')
    #     self.close()
    #
    # def reject(self) -> None:
    #     print('rej')
    #     self.close()
