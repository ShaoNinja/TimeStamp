## new
from datetime import datetime, timedelta,timezone
from TimeStamp.utils.time import dateutc, tz_utc, tz_local

# datetime 与 dateutc 对比
datetime(1858,11,17,0,0,0,0) >= dateutc(year=2019,month=11,day=10)
dateutc.now() - datetime(1858,11,17,0,0,0,0)
dateutc(year=2019,month=11,day=10) - datetime(year=2019,month=11,day=1)
type(dateutc.now()) is datetime

# 屏蔽父类方法，执行 utcnow 会报错
a = dateutc(year=2019,month=11,day=10) - timedelta(1)
dateutc.utcnow()

# datetime 对象转化为 dateutc
dateutc.fromdatetime(datetime(1858,11,17,0,0,0,0))

# 若 datetime 未定义时区，需要先设置(为系统)时区，然后再转化为 UTC, 否则可能报错
# 参考链接：https://stackoverflow.com/questions/71680355/oserror-errno-22-invalid-argument-when-using-datetime-strptime
datetime(1858,11,17).replace(tzinfo=tz_local).astimezone(tz_utc)
datetime(1858,11,17).astimezone(tz_utc)