import json
import os
import sys
import traceback
from multiprocessing import freeze_support
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox, QMessageBox, \
    QDialogButtonBox, QTabWidget, QScrollArea, QPlainTextEdit

from localclass.WorkerTimerTzStatusThread import WorkerTimerTzStatusThread
from localclass.WorkerWebServerThread import WorkerWebServerThread
from stgs.RSI.paint import Paint
import cfg
import func

import tools
from Trade import Trade
from localclass.PushButton import PushButton
from localclass.StgEditDialog import StgEditDialog
from localclass.Label import Label
from localclass.WorkerOrderThread import WorkerOrderThread
from localclass.WorkerTimerAccountProcessStatusThread import WorkerTimerAccountProcessStatusThread

from localclass.AccountDialog import AccountDialog
from localclass.CheckBox import CheckBox
from localclass.CustomDialog import CustomDialog
from localclass.TableWidget import TableWidget

from localclass.BroswerWindow import BroswerWindow

import pandas as pd

from localclass.WorkerThread import WorkerThread
from localclass.WorkerDataListenThread import WorkerDataListenThread
from localclass.WorkerStgThread import WorkerStgThread
from localclass.WorkerStgShipanThread import WorkerStgShipanThread

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # base config
        self.config = cfg.getCfg()

        self.WORKER_INIT = False
        self.WORKER_START = False

        # 实例化线程对象 start worker server
        self.work = WorkerThread()
        self.work.trigger.connect(self.job_done)
        self.work.finished.connect(self.job_finished)

        self.work_webserver = WorkerWebServerThread()

        self.windowhandles = []

        self.workdatalisten = WorkerDataListenThread()
        if int(self.config.get('app', 'stop_listen')) == 0:
            try:
                print('start work m..')
                self.workdatalisten.start()
            except Exception as e:
                print('worker data listen  e:', e)

        self.workstg = WorkerStgThread()
        self.workstg.finished.connect(self.onCloseWorkerStg)

        self.workstg_shipan = WorkerStgShipanThread()
        self.workstg_shipan.finished.connect(self.onCloseWorkerStg)

        self.setWindowTitle(self.config.get('app', 'title'))
        # As well as .setFixedSize() you can also call .setMinimumSize() and .setMaximumSize() to set the minimum and maximum sizes respectively. Experiment with this yourself!
        self.setMinimumSize(QSize(960, 580))

        # main layout
        layout_main = QVBoxLayout()
        header = self.getHeader()
        body = self.getBody()

        layout_main.addLayout(header)

        # 账号设置
        bodywidget = QWidget()
        bodywidget.setLayout(body)
        tabwidget = QTabWidget()
        tabwidget.addTab(bodywidget, "账号设置")

        # 历史数据
        self.layout_his = layout_his = QHBoxLayout()
        boxaccounts = QWidget()

        self.layout_accounts = layout_accounts = QVBoxLayout()
        layout_1account = QHBoxLayout()
        layout_1account.addWidget(QLabel('账号'))
        layout_1account.addWidget(QLabel('余额'))
        layout_1account.addWidget(QLabel('状态'))
        layout_accounts.addLayout(layout_1account)

        df_accounts = cfg.getAccountConfig(DATAFRAME=True)
        # print(account_config)

        for i in range(len(df_accounts)):
            row = df_accounts.iloc[i]
            print(row['用户名'])

            layout_1account = QHBoxLayout()
            qltz = Label(row['用户名'], row['用户名'])
            qltz.clicked.connect(self.labelclicked)
            qltz.setStyleSheet('color:#666;cursor:pointer;')
            layout_1account.addWidget(qltz)
            layout_1account.addWidget(QLabel('-'))

            qlonlinestatus = QLabel('离线')
            qlonlinestatus.setStyleSheet('color:red;')
            layout_1account.addWidget(qlonlinestatus)

            layout_accounts.addLayout(layout_1account)

        layout_accounts.addStretch()
        boxaccounts.setLayout(layout_accounts)
        boxaccounts.setFixedWidth(200)
        layout_his.addWidget(boxaccounts)

        # order thread
        self.workorder = WorkerOrderThread()
        self.workorder.trigger.connect(self.updateOrderData)
        # self.workorder.finished.connect(self.stopOrderData)

        # timer thread
        self.worktimer = WorkerTimerAccountProcessStatusThread()
        self.worktimer.trigger.connect(self.updateAccountProcessStatus)

        # real shipan account status
        self.worktimer_shipan = WorkerTimerTzStatusThread()
        self.worktimer_shipan.trigger.connect(self.updateShipanStatus)

        layout_his.addWidget(self.getHisOrderLayout())

        boxhis = QWidget()
        boxhis.setLayout(layout_his)
        tabwidget.addTab(boxhis, "历史数据")

        tabwidget.currentChanged.connect(self.tabchange)
        layout_main.addWidget(tabwidget)

        version_text = self.config.get('app', 'version')
        layout_main.addWidget(QLabel(version_text))

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    def updateShipanStatus(self, notifystr):
        # print('up status:', notifystr)
        datalist = json.loads(notifystr)
        count = self.layout_accounts.count()
        # print('lc:', count)
        for i in range(count):
            item = self.layout_accounts.itemAt(i)
            if type(item) is QHBoxLayout:
                if i == 0:
                    continue
                # print('item found...', i)
                obj = item.itemAt(0)
                widget = obj.widget()
                if type(widget) is Label:
                    # print('widget', widget.text(), widget.mark)
                    # widget.setText('aabbcc')
                    try:
                        objbalance = item.itemAt(1)
                        widgetbalance = objbalance.widget()
                        crow = datalist[i - 1]
                        if crow['account_name'] == widget.mark:
                            widgetbalance.setText(str(crow['balance']))
                            objinfo = item.itemAt(2)
                            widgetinfo = objinfo.widget()
                            if crow['online'] == True:
                                widgetinfo.setText('在线')
                                widgetinfo.setStyleSheet('color:green;')
                            else:
                                widgetinfo.setText('离线')
                                widgetinfo.setStyleSheet('color:red;')
                    except Exception as e:
                        print('updateShipanStatus', e)
                        traceback.print_exc()
    def onCloseWorkerStg(self):
        print('worker stg close')

    def clearHiddenWindow(self):
        lenh = len(self.windowhandles)
        # print('clear window:', lenh)
        for i in range(lenh):
            wk = lenh - 1 - i
            w = self.windowhandles[wk]
            if w.isHidden():
                del(self.windowhandles[wk])

    def updateAccountProcessStatus(self, notifystr):
        print('up status:', notifystr)
        self.initAccountTable()
        self.clearHiddenWindow()

    def labelclicked(self, mark):
        if self.WORKER_START:
            print('label c....', mark)
            self.workorder.set_current_mark(mark)
            self.workorder.start()
        else:
            self.showAlertStartService()

    def tabchange(self, p_int):
        # print('tab change...', p_int)
        if p_int == 1:
            pass
            # print('workorder: re get order info')
            # self.workorder.start()

    def updateOrderData(self, data):
        # self.updateNewOrderComeRefresh()
        # print("update orders...", data)

        try:
            jsonobj = json.loads(data)
            self.ql_order_header.setText(jsonobj['mark'] + '交易记录')
            self.order_editarea.setPlainText(jsonobj['result_str'])
        except Exception as e:
            # print(e)
            self.order_editarea.setPlainText('记录为空')

        # self.layout_done_orders.addWidget(QLabel('加载完毕。。'))

    def stopOrderData(self):
        print('order end...')

    def getHisOrderLayout(self):
        layout_his_right = QVBoxLayout()
        layout_order_header = QHBoxLayout()
        self.ql_order_header = ql_order_header = QLabel('')
        layout_order_header.addWidget(self.ql_order_header)
        layout_his_right.addLayout(layout_order_header)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.layout_done_orders = layout_done_orders = QVBoxLayout()
        self.order_editarea = order_editarea = QPlainTextEdit()

        # t = Trade('dtest').getTradeResult('20230115221010', 16000)
        # print(t)
        # order_editarea.setPlainText(t['result_str'])
        # order_editarea.setDisabled(True)
        layout_done_orders.addWidget(order_editarea)

        widgetorders = QWidget()
        widgetorders.setLayout(self.layout_done_orders)

        scroll.setWidget(widgetorders)
        layout_his_right.addWidget(scroll)

        qw_his_right = QWidget()
        qw_his_right.setLayout(layout_his_right)

        # order_style = 'background-color:#999;'
        # qw_his_right.setStyleSheet(order_style)
        return qw_his_right

    def job_finished(self):
        print('job finished')
        # self.btn_start.setText('开始')

    def job_start(self):
        print('job start..')
        # return 'start...'
        if self.WORKER_START == False:
            self.btn_start.setText('停止')
            self.WORKER_START = True
            self.work.start()
            self.work_webserver.start()

            if self.WORKER_INIT == False:
                print('first start worktimer')
                self.worktimer.start()
                self.worktimer_shipan.start()

                self.WORKER_INIT = True
        else:
            print('worker listen...')
            print('stoped ...')
            self.btn_start.setText('开始')
            self.work.stop_server()
            self.work.terminate()
            self.WORKER_START = False

    def job_done(self, bakstr):
        print('job done succ..' + bakstr)

    def job_clear(self):
        print('job clear...')
        func.clearData()
        self.showAlertStartService('清理完成')

    def getHeader(self):
        # header
        header = QHBoxLayout()
        self.btn_start = btn_start = QPushButton('开始')
        btn_start.clicked.connect(self.job_start)

        self.btn_clear = btn_clear = QPushButton('清理')
        btn_clear.clicked.connect(self.job_clear)

        header.addWidget(btn_start, 0)
        header.addWidget(btn_clear)

        # qc_stop_listen = CheckBox('app.stop_listen', 0, 0)
        # qc_stop_listen.setText('暂停监控')
        # if int(self.config.get('app', 'stop_listen')) == 1:
        #     qc_stop_listen.setChecked(True)
        # else:
        #     pass
        # qc_stop_listen.checkIndexChange.connect(self.check_change)
        # qc_stop_xiazhu = CheckBox('app.stop_xiazhu', 0, 0)
        # qc_stop_xiazhu.setText('暂停下单')
        #
        # if int(self.config.get('app', 'stop_xiazhu')) == 1:
        #     qc_stop_xiazhu.setChecked(True)
        #
        # qc_stop_xiazhu.checkIndexChange.connect(self.check_change)

        # header.addWidget(qc_stop_listen)
        # header.addWidget(qc_stop_xiazhu)

        header.addStretch()
        btn_start_stg = QPushButton('启动回测')
        btn_start_stg.clicked.connect(self.start_stg)

        btn_stop_stg = QPushButton('停止回测')
        btn_stop_stg.clicked.connect(self.stop_stg)

        btn_start_stg_shipan = QPushButton('启动实盘')
        btn_start_stg_shipan.clicked.connect(self.start_stg_shipan)

        btn_stop_stg_shipan = QPushButton('停止实盘')
        btn_stop_stg_shipan.clicked.connect(self.stop_stg_shipan)

        header.addWidget(btn_start_stg)
        header.addWidget(btn_stop_stg)

        header.addWidget(btn_start_stg_shipan)
        header.addWidget(btn_stop_stg_shipan)

        return header

    def start_stg(self):
        try:
            if self.WORKER_START:
                print('start stg')
                selectRows = self.tw_account_list.selectionModel().selectedRows()
                loginuid = 0
                if selectRows:
                    if len(selectRows) == 1:
                        currentRows = selectRows[0]
                        accs = cfg.getAccountConfig(DATAFRAME=True)
                        selacc = accs.iloc[currentRows.row()]
                        loginuid = currentRows.row()

                        account_name = selacc['用户名']
                        print('acc:', account_name)
                        w = BroswerWindow(account_name + '回测', account_name, path='paint')
                        func.setAccountKlineData(account_name, Paint.RUN_TYPE_STATIC, {})
                        self.windowhandles.append(w)
                        w.show()
                        self.workstg.set_login_uid(loginuid)
                        self.workstg.start()
            else:
                self.showAlertStartService()
        except Exception as e:
            print('e start stg err:', e)

    def start_stg_shipan(self):
        if self.WORKER_START:
            print('start shipan stg')
            selectRows = self.tw_account_list.selectionModel().selectedRows()
            loginuid = 0
            if selectRows:
                if len(selectRows) == 1:
                    currentRows = selectRows[0]
                    accs = cfg.getAccountConfig(DATAFRAME=True)
                    selacc = accs.iloc[currentRows.row()]
                    loginuid = currentRows.row()

                    account_name = selacc['用户名']
                    w = BroswerWindow(account_name + '实盘', account_name, path='shipan')

                    self.windowhandles.append(w)
                    w.show()
                    print('is hidden:', w.isHidden())


                    self.workstg_shipan.set_login_uid(loginuid)
                    self.workstg_shipan.start()
        else:
            self.showAlertStartService()

    def showAlertStartService(self, msg=None):
        if msg is None:
            msg = "请先开始服务"
        dlg = QMessageBox(self)
        dlg.setWindowTitle("info")
        dlg.setText(msg)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Ok:
            print("OK!")

    def stop_stg(self):
        if self.WORKER_START:
            print('stop stg')
            selectRows = self.tw_account_list.selectionModel().selectedRows()
            loginuid = 0
            if selectRows:
                if len(selectRows) == 1:
                    currentRows = selectRows[0]
                    accs = cfg.getAccountConfig(DATAFRAME=True)
                    selacc = accs.iloc[currentRows.row()]
                    # print()
                    account_name = selacc['用户名']
                    try:
                        pid = tools.getAccountProcessId(account_name)
                        if pid is not None:
                            tools.kill_pid(pid)
                        self.showAlertStartService('操作成功')
                    except Exception as e:
                        print(e)
                else:
                    self.showAlertStartService('请选择回测账号')
            else:
                self.showAlertStartService('请选择账号')
        else:
            self.showAlertStartService()

    def stop_stg_shipan(self):
        if self.WORKER_START:
            print('stop stg shipan')
            selectRows = self.tw_account_list.selectionModel().selectedRows()
            loginuid = 0
            if selectRows:
                if len(selectRows) == 1:
                    currentRows = selectRows[0]
                    accs = cfg.getAccountConfig(DATAFRAME=True)
                    selacc = accs.iloc[currentRows.row()]
                    # print()
                    account_name = selacc['用户名']
                    try:
                        processname = account_name
                        pid = tools.getAccountProcessId(processname, shipan=True)
                        if pid is not None:
                            tools.setAccountProcess(processname, None, shipan=True)
                            tools.kill_pid(pid)
                        self.showAlertStartService('操作成功')
                    except Exception as e:
                        print(e, 'process not found')
                        self.showAlertStartService('process not found')
                else:
                    self.showAlertStartService('请选择操作账号')
            else:
                self.showAlertStartService('请选择账号')
        else:
            self.showAlertStartService()

    def getBody(self):
        # body
        body = QHBoxLayout()
        body_window_left = QVBoxLayout()

        body_bar = QHBoxLayout()

        account_set = QLabel('账号设置')

        body_bar.addWidget(account_set)

        body_bar.addStretch()
        body_window_left.addLayout(body_bar)

        # tz config
        tz_config = cfg.getTzConfig()

        self.table_account = table_account = TableWidget('TZ')
        # print(len(tz_config['tzs']))
        table_account.setRowCount(len(tz_config['tzs']))
        table_account.setColumnCount(len(tz_config['title']))

        table_account.setHorizontalHeaderLabels(tz_config['title'])
        # table_account.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i in range(len(tz_config['tzs'])):
            ctz = tz_config['tzs'][i]
            for j in range(len(ctz)):
                if j in [2, 3]:
                    qc = CheckBox('TABLE_TZ', i, j)
                    checked = int(ctz[j])
                    if checked == 1:
                        qc.setChecked(True)
                    qc.checkIndexChange.connect(self.check_change)
                    table_account.setCellWidget(i, j, qc)
                else:
                    table_account.setItem(i, j, QTableWidgetItem(str(ctz[j])))

        table_account.setColumnWidth(0, 20)

        table_account.cellLastCheckChanged.connect(self.event_table_edit)

        # table_account.setStyleSheet('background-color:#666;')

        # config account tool bar
        lh_manaccount = QHBoxLayout()
        add_btn = QPushButton('添加账户')
        add_btn.clicked.connect(self.addAccount)

        del_btn = QPushButton('删除账户')

        del_btn.clicked.connect(self.deleteAccount)
        lh_manaccount.addWidget(add_btn)
        lh_manaccount.addWidget(del_btn)
        lh_manaccount.addStretch()

        # account table
        self.tw_account_list = tw_account_list = self.initAccountTable()
        body_window_left.addWidget(table_account)
        body_window_left.addLayout(lh_manaccount)
        body_window_left.addWidget(tw_account_list)

        btn_save = QPushButton('保存')
        btn_save.clicked.connect(self.onClickSaveAccountTable)
        btn_save.setFixedWidth(80)

        body_window_left.addWidget(btn_save)

        # body_window_left.addStretch()

        # float right
        body_window_right = QVBoxLayout()
        body_window_right_widget = QWidget()
        body_window_right_widget.setLayout(body_window_right)
        body_window_right_widget.setFixedWidth(136)

        stgs = cfg.getStgLists()
        infobox = QVBoxLayout()
        infobox.addWidget(QLabel('系统已装载策略(%d)' % len(stgs)))
        stgstr = ','.join(stgs)
        infobox.addWidget(QLabel(stgstr))

        body_window_right.addLayout(infobox)

        body_window_right.addStretch()
        body.addLayout(body_window_left)
        body.addWidget(body_window_right_widget)

        return body

    def onClickSaveAccountTable(self):
        print('save account table...')
        if hasattr(self, 'tw_account_list'):
            tcount = self.tw_account_list.rowCount()
            # self.tw_account_list.insertRow(tcount)
            print('table count:', tcount)
            account_config = cfg.getAccountConfig()
            print(account_config)
            header_list = account_config['title']
            df_accounts = cfg.getAccountConfig(True)

            for i in range(tcount):
                curuname = account_config['accounts'][i][1]
                for j in range(len(header_list)):
                    colname = header_list[j]
                    citem = self.tw_account_list.item(i, j)
                    if colname in ['APPID', 'APIKEY', 'OPTK', '策略', '备注']:
                        if type(citem) is QTableWidgetItem:
                            # print(i, j, citem, citem.text())
                            df_accounts.iloc[i, j] = citem.text().strip()

                            # sync key param
                            if colname in ['APPID', 'APIKEY', 'OPTK']:
                                # if colname == '策略':
                                #     colname = 'STG'
                                cfg.save_config('set.' + colname, citem.text().strip(), name='account.' + curuname)

            cfg.saveAccountsConfig(df_accounts)

        self.initAccountTable()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("提示")
        dlg.setText("保存成功!")
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Ok:
            print("OK!")

    def initAccountTable(self):
        account_config = cfg.getAccountConfig()
        cfg_accounts = account_config['accounts']

        if hasattr(self, 'tw_account_list'):
            tw_account_list = self.tw_account_list
            # print('rowcount', tw_account_list.rowCount())

            if tw_account_list.rowCount() != len(cfg_accounts):
                tw_account_list.clear()
                tw_account_list.setRowCount(0)
                tw_account_list.setColumnCount(0)
                # print('clear...')
                tw_account_list.setRowCount(len(account_config['accounts']))
                tw_account_list.setColumnCount(len(account_config['title']))
                tw_account_list.setHorizontalHeaderLabels(account_config['title'])
        else:
            tw_account_list = TableWidget('ACCOUNT')

            tw_account_list.setRowCount(len(account_config['accounts']))
            tw_account_list.setColumnCount(len(account_config['title']))
            tw_account_list.setHorizontalHeaderLabels(account_config['title'])

            tw_account_list.cellLastCheckChanged.connect(self.event_table_edit)

        header_list = account_config['title']

        for i in range(len(account_config['accounts'])):
            account = account_config['accounts'][i]

            for j in range(len(account)):
                colname = header_list[j]
                # TZID, 用户名, 启用, 虚拟下单, APPID, APIKEY, OPTK, 策略, 备注, 状态
                if colname in ['启用', '虚拟下单']:
                    qc = CheckBox('TABLE_ACCOUNT_KEY', i, j)
                    checked = int(account[j])
                    if checked == 1:
                        qc.setChecked(True)
                    qc.checkIndexChange.connect(self.check_change)
                    tw_account_list.setCellWidget(i, j, qc)
                else:
                    if colname == '策略':
                        clbox = QHBoxLayout()
                        clbox.addWidget(QLabel(str(account[j])))
                        account_name = str(account[1])

                        btn_edit_stg = PushButton(account_name, 'edit')
                        # btn_edit_stg.setFixedHeight(60)
                        btn_edit_stg.clicked.connect(self.onClickEditStg)

                        clbox.addWidget(btn_edit_stg)

                        clwidget = QWidget()
                        clwidget.setLayout(clbox)

                        tw_account_list.setCellWidget(i, j, clwidget)
                    elif colname in ['平台', '用户名', '状态']:
                        ql = QLabel(str(account[j]))
                        tw_account_list.setCellWidget(i, j, ql)
                    else:
                        qitem = QTableWidgetItem(str(account[j]))
                        tw_account_list.setItem(i, j, qitem)

            tw_account_list.setRowHeight(i, 36)

        for i in range(len(header_list)):
            colname = header_list[i]
            if colname in ['APPID', 'APIKEY', 'OPTK']:
                tw_account_list.setColumnWidth(i, 50)

        self.tw_account_list = tw_account_list
        return tw_account_list

    def onClickEditStg(self, mark):
        print('onClickEditStg:', mark)

        try:
            dialog = StgEditDialog(mark, self)
            # dialog.tableSave.connect(self.event_tablesave)
            dialog.exec()
        except Exception as e:
            print(e)

    def deleteAccount(self):
        selectRows = self.tw_account_list.selectionModel().selectedRows()
        if selectRows:
            dlg = CustomDialog("警告", "确认删除" + str(len(selectRows)) + "条数据？")
            button = dlg.exec()
            if button == 1:
                selectRows.reverse()
                for rowobj in selectRows:
                    index = rowobj.row()
                    cfg.delAccount(index)
                    self.tw_account_list.removeRow(index)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("info")
            dlg.setText("请选择行")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")

    def addAccount(self):
        try:
            dialog = AccountDialog(self)
            dialog.tableSave.connect(self.event_add_account)
            dialog.exec()
        except Exception as e:
            print(e)

    def event_add_account(self, datastr):
        data = json.loads(datastr)
        username = data['username']
        tz = data['tz']

        accounts = cfg.getAccountConfig(True)
        tzs = cfg.getTzConfig(True)

        try:
            tzid = tzs.loc[tzs['网站'] == tz]['ID'].reset_index(drop=True).iloc[0]
            # TZID, 用户名, 启用, 虚拟下单, APPID, APIKEY, OPTK, 策略, 备注
            df_new_row = pd.DataFrame({"TZID": [tzid], "用户名": [username], "启用": ["0"], "虚拟下单": ["0"], \
                                       "APPID": [data.get('appid')], "APIKEY": [data.get('apikey')], \
                                       "OPTK": [data.get('optk')], "策略": [data.get('stg')], "备注": [""]})

            accounts = pd.concat([accounts, df_new_row])
            cfg.saveAccountsConfig(accounts)
            cfg.initAccountData(username)

            self.initAccountTable()

        except Exception as e:
            print(e)

    def event_table_edit(self, mark, row, column, newval):
        ctext = newval
        if mark == 'TZ':
            if len(ctext) > 0:
                tzs = cfg.getTzConfig(DATAFRAME=True)
                tzs.iloc[row, column] = ctext
                cfg.saveTzConfig(tzs)
        elif mark == 'ACCOUNT':
            print('ACCOUNT edit...', mark, row, column, newval)

            if len(ctext) > 0:
                df = cfg.getAccountConfig(DATAFRAME=True)
                df.iloc[row, column] = ctext
                cfg.saveAccountsConfig(df)

    def check_change(self, mark, checked, *args):
        print(mark, checked, args)
        if mark == 'TABLE_TZ':
            tzs = cfg.getTzConfig(DATAFRAME=True)
            row = args[0]
            col = args[1]
            tzs.iloc[row, col] = str(checked)
            cfg.saveTzConfig(tzs)

        elif mark == 'TABLE_ACCOUNT_KEY':
            accounts = cfg.getAccountConfig(DATAFRAME=True)
            row = args[0]
            col = args[1]
            accounts.iloc[row, col] = str(checked)
            cfg.saveAccountsConfig(accounts)

            username = accounts.iloc[row]['用户名']
            print(username)
            if str(checked) == '1':
                if col == 2:
                    cfg.save_config('set.SHIPAN_ENABLE', 'yes', name='account.' + username)
                elif col == 3:
                    cfg.save_config('set.SHIPAN_TYPE', 'VIRTUAL', name='account.' + username)
            else:
                if col == 2:
                    cfg.save_config('set.SHIPAN_ENABLE', 'no', name='account.' + username)
                elif col == 3:
                    cfg.save_config('set.SHIPAN_TYPE', 'REAL', name='account.' + username)

        elif mark.find('.') > -1:
            try:
                cfg.save_config(mark, checked)
                if mark == 'app.stop_listen':
                    if int(checked) == 1:
                        self.workdatalisten.stop_server()
                    else:
                        self.workdatalisten.start()

            except Exception as e:
                print(e)

    def tztimerChange(self, opt, val):
        cfg.save_config(opt, val)

    def tzlrChange(self, val):
        cfg.save_config('zoudi.profit', val)

    def closeEvent(self, event):
        print("close event")
        cfg.setpid(None)
        self.windowhandles = []
        self.work.stop_server()
        self.workdatalisten.stop_server()
        self.workorder.stop_server()
        self.worktimer.stop_server()
        self.worktimer_shipan.stop_server()
        self.work_webserver.stop_server()


if __name__ == "__main__":
    try:
        freeze_support()
        print("start")
        print("当前进程ID：", os.getpid())
        cfg.setpid(os.getpid())
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        app.exec()
    except Exception as e:
        print('__main__ e:', e)
