# coding:utf-8

import datetime
import pytz


tz = pytz.timezone('Asia/Shanghai')


def timenow():
    return datetime.datetime.now(tz)