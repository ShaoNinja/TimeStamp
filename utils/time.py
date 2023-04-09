##
from datetime import date, datetime, timedelta, timezone
import math

tz_utc = timezone.utc
mjd0_datetime = datetime(1858, 11, 17, 0, tzinfo=timezone.utc)  # 简化儒略日起始日

# mjd 转 dateutc
def mjd2dateutc(mjd):
    return mjd0_datetime + timedelta(days=mjd)

# 创建datetime子类。datetime对象是Python内置的不可变对象，所用的time源码是C语言所写。
# 建议阅读：https://aaronoellis.com/articles/subclassing-datetime-date-in-python-3
class dateutc(datetime):

    # 屏蔽父类方法 (搜索下面一行代码可以了解相关内容)
    utcnow = property(doc='(!) Disallowed inherited')

    # region : 重写父类方法

    def __new__(cls, year, month=None, day=None, hour=0, minute=0, second=0,
                microsecond=0, tzinfo=tz_utc, *args, **kwags):
        ''' 获取以 UTC 时区为基准的日期时间\n
            注意：程序会忽略外部传入的 tzinfo 变量, 内部将默认使用 UTC 时区'''
        return super().__new__(cls, year, month, day, hour, minute, second,
                               microsecond, tzinfo=tz_utc, *args, **kwags)

    @classmethod
    def now(cls):
        '''获取UTC时区的当前时间,同utcnow'''
        return super().now(tz=tz_utc)

    def astimezone(self, tz=None) -> datetime:
        '''转换时区, 返回父类 ( datetime ), 默认转化为当地时间'''
        return self.to_datetime.astimezone(tz)

    def __repr__(self):
        """Convert to formal string, for repr()."""
        assert self.tzinfo == timezone.utc
        L = [self.year, self.month, self.day, self.hour,
             self.minute, self.second + self.microsecond/1.E6]
        return self.__class__.__qualname__ + "(%s)" % ", ".join(map(str, L))

    # 减法运算需要重写父类方法，加法运算可直接调用父类方法
    def __sub__(self, other):
        '''减法运算'''
        if type(other) is datetime and other.tzinfo is not tz_utc:
            return super().__sub__(other.astimezone(tz=tz_utc))
        else:
            return super().__sub__(other)

    # Comparisons of datetime objects with other.

    def _cmp(self, other):
        '''比较运算'''
        diff = self - other           # diff 的类型是 timedelta
        if diff.total_seconds() < 0:  # timedelta 的 seconds 属性是小数, 包含了 microsecond 信息
            return -1
        return diff.total_seconds() and 1

    def __eq__(self, other):
        '''等于(==)比较'''
        if isinstance(other, datetime):
            return self._cmp(other) == 0
        else:
            return NotImplemented

    def __le__(self, other):
        '''小于等于(<=)比较'''
        if isinstance(other, datetime):
            return self._cmp(other) <= 0
        else:
            return NotImplemented

    def __lt__(self, other):
        '''小于(<)比较'''
        if isinstance(other, datetime):
            return self._cmp(other) < 0
        else:
            return NotImplemented

    def __ge__(self, other):
        '''大于等于(>=)比较'''
        if isinstance(other, datetime):
            return self._cmp(other) >= 0
        else:
            return NotImplemented

    def __gt__(self, other):
        '''大于(>)比较'''
        if isinstance(other, datetime):
            return self._cmp(other) > 0
        else:
            return NotImplemented

    # endregion 重写父类方法

    def today(hour:float=0., minute:float=0., second:float=0.):
        '''获取当天某时刻, 返回 dateutc 类型'''
        now = dateutc.now()  # 获取当前utc时间
        dt = timedelta(hours=hour,minutes=minute,seconds=second)
        return dateutc(now.year,now.month,now.day) + dt

    def fromdate(date:date):
        '''将 date 类型转化为 dateutc 类型, 时间为 UTC 0 时刻'''
        return dateutc(date.year, date.month, date.day)

    def fromdatetime(datetime:datetime):
        '''将 datetime 转化为 dateutc, 如果 datetime 没有时区信息, 则默认为本地时区'''
        tmp = datetime.astimezone(tz=tz_utc)
        return dateutc(tmp.year, tmp.month, tmp.day, tmp.hour, tmp.minute,
                       tmp.second, tmp.microsecond, tmp.tzinfo, fold=tmp.fold)

    @property  # 转化为父类(datetime)
    def to_datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day,
                        self.hour, self.minute, self.second,
                        self.microsecond, self.tzinfo, fold=self.fold)

    @property  # 获取这一年的第几天
    def to_doy(self):
        year = self.year
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            mlist = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:  # 闰年↑ 非闰年↓
            mlist = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return sum(mlist[0:self.month-1]) + self.day

    @property  # datetime 转 mjd
    def to_mjd(self):
        mjd = ( self - mjd0_datetime ).days
        mjd_s = self.hour*3600.0 + self.minute*60.0 + self.second + self.microsecond/1.E6
        return mjd + mjd_s/86400.0        # 精确到微秒

    @property  # datetime 转 gps (包括GPS周和小数天)
    def to_gps(self):
        elapse = self.to_mjd - 44244      # GPS从MJD44244开始
        week = math.floor(elapse/7)       # GPS周数
        fday = elapse - week*7            # 周内天数
        return week, fday