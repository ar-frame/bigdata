import json

from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QMessageBox

import sys
sys.path.append('../')
import cfg

class StgEditDialog(QDialog):
    tableSave = QtCore.pyqtSignal(str)
    def __init__(self, mark, *args, **kwargs):
        super(StgEditDialog, self).__init__(*args, **kwargs)

        self.mark = mark
        self.setWindowTitle('编辑策略')
        h = 560
        self.resize(480, h)
        vl = QVBoxLayout()
        self.editarea = editarea = QPlainTextEdit()
        stg_content = cfg.getAccountCfg(self.mark, stg=True, raw=True)
        editarea.setPlainText(str(stg_content))
        editarea.setFixedHeight(h - 60)
        vl.addWidget(editarea)
        vl.addStretch()
        hl1 = QHBoxLayout()
        hl1.addStretch()
        btn_init = QPushButton('初始化策略')
        btn_init.clicked.connect(self.load_stg)
        hl1.addWidget(btn_init)

        btn_save = QPushButton('保存')
        btn_save.clicked.connect(self.save_stg)

        hl1.addWidget(btn_save)
        vl.addLayout(hl1)
        self.setLayout(vl)

    def load_stg(self):
        content = cfg.getAccountStgInitCfg(self.mark, raw=True)
        self.editarea.setPlainText(content)

    def save_stg(self):
        content = self.editarea.toPlainText()
        # print("content:", content)
        cfg.saveAccountCfg(self.mark, content.strip(), stg=True)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("info")
        dlg.setText("保存成功")
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Ok:
            self.tableSave.emit(content)
            self.close()



