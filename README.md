# 【KT交易端】
本程序bigdata（KT交易端）是ktrader核心交易程序，使用PyQT开发，理论上跨平台兼容各种操作系统。

GUI配置，多进程+线程运行，支持实盘，回测，支持多品种同时交易。

* 系统主界面
![系统截图](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/app_2.1.2.png)

# 【1.安装】

## Mongodb安装
KT交易端运行需要mongodb数据库的支持，windows双击安装即可。
mongodb下载地址https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-4.4.15-signed.msi
安装好后，参考'配置'的mongodb

## 交易端下载
KT交易端是基于PyQt6的开发，打包windows exe运行程序在开发群文件共享里下载

### 启动
* 解压app.zip, 启动app.exe，配置参数，启动策略
* 交易端app.zip压缩文件放在交流群里自由下载，如运行错误请安装vc64运行库
* 系统推荐WIN10 64位 8G以上内存

# 【2.配置】
复制src/conf/rename.conf.ini 重命名为配置文件 src/conf/conf.ini

## 【2.1全局配置】
主要配置网络，数据库，密钥等，如无特殊说明保持默认即可。
httpproxies 网络代理
mongo_store 配置mongo存储
```
[set]
shipan_enable = yes
trade_broker_type = binance
print_runtime_trace = no
push_to_shipan_record = yes
shipan_db_type = mongodb
mongo = store
localserver = localhost:5000
localserverkey = aaabbbccccoopserverkey123in
localwebserver = localhost:8000
httpproxies = 192.168.101.169:10810

[mongo_store]
db_host = 192.168.101.169
db = store
db_pass = 
db_user = 
db_port = 27017
```

## 【2.2账户添加】
KT的每个账户（非交易所账户）独立存在，建议每个交易对配置一个账户。
不同策略参数配置不同账户，名称不同即可。
![账户添加](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/add_account.png)

# 【3.回测】
实盘之前，需要检测策略的逻辑正确性，可行性，回测即是最好的方案

## 配置参数
![策略编辑](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/edit_stg.png)

## 启动回测
![启动回测](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/start_paint.png)

## 启动数据源
回测前，需要添加DATA账户，启动一段时间（根据策略的需要来定）
数据是1s Kline data, 回测的时间最好不要超过24h
![启动DATA](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/start_data.png)


# 【4.实盘】
* 设置策略参数 参考回测，建议先回测检验策略的有效性
* 启动实盘
![启动回测](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/start_shipan.png)

* 历史数据
![历史数据](https://gitee.com/ar-frame/bigdata/raw/master/docs/img/show_his.png)


# 【5.策略开发】

## 自定义策略
### 目录
src/stgs
参照内置策略名：`RSI`, 
开发复制整个`RSI`目录，更改为其他名字，建议不要使用中文。

目录需要包含
* main.ini 策略配置
* main.py 实盘引导文件
* paint.py 回测引导文件
* stg.py 策略逻辑文件

策略是主要修改stg.py的策略内容

目前策略内置 DATA，RSI两个策略：
DATA，数据存储，回测前必启动
RSI，参考策略模板
* 更多策略请+交流群

# 【二开】
## 使用的技术和框架
coop_fetch
coop_server
python3
mongodb
websocket
pyqt
nodejs
react
tradingview lightweight-charts

## 依赖库参考
matplotlib
numpy             
pandas             
pymongo            
PyMySQL           
python-dateutil    
requests           
websocket         
websocket-client
PyQt6
psutil
pycryptodome
flask_cors
alive_progress
            
### 参考一键安装命令
`python -m pip install -r requirements.txt`

## 数据库
### mongodb (必须)

## 错误及调试日志
log/stg_error_log.log

## gui package 
pyinstaller .\app.spec

# 【更新日志】

## 2023/05/09 功能增加
* 增加实盘，回测 K线
* 多窗口监控
* 优化交易

## 2023/01/18 增加GUI交易端
* 重构以支持GUI操作 (PyQT6) windows exe 一键启动
* 封装NJ交易策略
* 自定义装载策略

## 2022/11/26 增加能级配置参数
[trade]
```
# 每次加仓价格波动率
SHIPAN_CON_GRID_INC_LEVEL_POINT = 0.00618
# 每次减仓价格波动率
SHIPAN_CON_GRID_DEC_LEVEL_POINT = 0.00818

# BUY 能级
STG_NG_UP = 320000
# SELL 能级
STG_NG_DOWN = 280000

```
【MIT】
* Copyright © 2023 dpbtrader, v: kozdpb
* ktrader学习交流q群: `259956472`


---
*申明：本项目仅为交流学习作用，切勿用作第三方商业使用，鉴于网络，参数，品种的各种不确定性，没有100%赚钱的量化软件，使用此软件造成的损失与我方无关，交易有风险，投资需谨慎。*


