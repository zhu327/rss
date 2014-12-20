#_*_ coding:utf-8 _*_

import datetime
from dateutil import tz

class LocalTimezone(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)

    def dst(self, dt):
        return datetime.timedelta(0)

def getNow():
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=tz.gettz('UTC'))
    local = utc.astimezone(LocalTimezone())
    return local
