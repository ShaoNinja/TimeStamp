##
from TimeStamps.utils.time import dateutc, datetime, timedelta


datetime(1858,11,17,0,0,0,0) >= dateutc(year=2019,month=11,day=10)
dateutc.now().astimezone() - datetime(1858,11,17,0,0,0,0).astimezone()
dateutc(year=2019,month=11,day=10) - datetime(year=2019,month=11,day=1)
type(dateutc.now()) is datetime

a = dateutc(year=2019,month=11,day=10) - timedelta(1)
dateutc.utcnow()

dateutc.fromdatetime(datetime(1858,11,17,0,0,0,0))