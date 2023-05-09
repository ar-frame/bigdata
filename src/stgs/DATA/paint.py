#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'test for dev stg moudule'
__author__ = 'dpbtrader'
import sys
sys.path.append('../../')

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import func
import cfg

from DATA.stg import STG

class Paint(STG):
    RUN_TYPE_STATIC = 'VIRTUAL'
    def __init__(self, **params):
        print(params)
        super().__init__(**params)

    def start(self):
        print('DATA no paint...')

if __name__ == "__main__":
    Paint(account_name='dtest2').start()

