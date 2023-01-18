import json

from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox

import sys
sys.path.append('../')
import cfg

class AccountDialog(QDialog):
    tableSave = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        super(AccountDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle('添加账号')
        self.resize(320, 220)
        vl = QVBoxLayout()

        label_size = 60
        val_size = 160

        tzs = cfg.getTzTitles()
        print(tzs)

        self.cb_tz = cb_tz = QComboBox()
        cb_tz.addItems(tzs)
        # cb_tz.setCursor(1)
        cb_tz.setFixedWidth(val_size)

        label_tz = QLabel('选择平台:')
        label_tz.setFixedWidth(label_size)
        hl0 = QHBoxLayout()
        hl0.addWidget(label_tz)
        hl0.addWidget(cb_tz)
        hl0.addStretch()

        self.cb_stg = cb_stg = QComboBox()
        stglist = cfg.getStgLists()
        cb_stg.addItems(stglist)
        cb_stg.setFixedWidth(val_size)
        label_stg = QLabel('选择策略:')
        label_stg.setFixedWidth(label_size)
        hl_stg = QHBoxLayout()
        hl_stg.addWidget(label_stg)
        hl_stg.addWidget(cb_stg)
        hl_stg.addStretch()

        label_username = QLabel('用户名:')
        label_username.setFixedWidth(label_size)
        self.username = username = QLineEdit()

        username.setFixedWidth(val_size)
        hl = QHBoxLayout()
        hl.addWidget(label_username)
        hl.addWidget(username)
        hl.addStretch()


        label_appid = QLabel('appid:')
        label_appid.setFixedWidth(label_size)
        self.appid = appid = QLineEdit()

        appid.setFixedWidth(val_size)
        hl_appid = QHBoxLayout()
        hl_appid.addWidget(label_appid)
        hl_appid.addWidget(appid)
        hl_appid.addStretch()

        label_apikey = QLabel('apikey:')
        label_apikey.setFixedWidth(label_size)
        self.apikey = apikey = QLineEdit()

        apikey.setFixedWidth(val_size)
        hl_apikey = QHBoxLayout()
        hl_apikey.addWidget(label_apikey)
        hl_apikey.addWidget(apikey)
        hl_apikey.addStretch()

        label_optk = QLabel('optk:')
        label_optk.setFixedWidth(label_size)
        self.optk = optk = QLineEdit()

        optk.setFixedWidth(val_size)
        hl_optk = QHBoxLayout()
        hl_optk.addWidget(label_optk)
        hl_optk.addWidget(optk)
        hl_optk.addStretch()


        vl.addLayout(hl0)
        vl.addLayout(hl_stg)
        vl.addLayout(hl)
        vl.addLayout(hl_appid)
        vl.addLayout(hl_apikey)
        vl.addLayout(hl_optk)


        vl.addStretch()

        btn_save = QPushButton('保存')
        btn_save.clicked.connect(self.save_account)
        hl1 = QHBoxLayout()
        hl1.addStretch()
        hl1.addWidget(btn_save)

        vl.addLayout(hl1)
        self.setLayout(vl)

    def save_account(self):
        username = self.username.text()
        print("username:", username)

        tz = self.cb_tz.currentText()
        print("tz:", tz)

        stg = self.cb_stg.currentText()
        print("stg:", stg)

        appid = self.appid.text()
        apikey = self.apikey.text()
        optk = self.optk.text()

        data = {"username": username, "tz": tz, "stg": stg, "appid": appid, "apikey": apikey, "optk": optk}
        datastr = json.dumps(data)
        print(data)
        errmsg = '请输入完整数据'
        if username.strip() and tz.strip() and stg.strip():
            if cfg.checkAccountNameEnable(username.strip()) == False:
                errmsg = '用户名已存在'
            else:
                self.tableSave.emit(datastr)
                self.close()
                return

        dlg = QMessageBox(self)
        dlg.setWindowTitle("info")
        dlg.setText(errmsg)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Ok:
            print("OK!")



