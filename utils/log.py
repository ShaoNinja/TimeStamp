# 保存所执行代码的日志信息

import os
from datetime import datetime

class Log:

    _INFO, _WARN, _EROR, _STOP = 0, 1, 2, 3

    def __init__(self, suffix, rootdir='', level='INFO'):
        self.suffix  = suffix                     # log文件的后缀
        if rootdir == '':                         # log文件的根路径
            self.rootdir = os.getcwd() + '/LOG/'  # 这是默认根路径
        else:
            self.rootdir = rootdir
        self._LEVEL = self._INFO                  # 默认日志等级为INFO

    def utcnow(self,format='%H:%M:%S'):
        return datetime.utcnow().strftime(format)

    def GetLatestPath(self):
        return self.rootdir + '%s.%s.log' % (self.utcnow('%Y%m'),self.suffix)

    # Write Content to LogFile (log日志中使用UTC时间)
    def Write(self, text: str = ''):
        filename = self.GetLatestPath()
        exit_flag = os.path.exists(filename)  # Check File Whether Exist
        with open(filename, 'a', encoding='utf-8') as file:
            if bool(1-exit_flag):
                file.write( '--- Create DateTime : %s ---\n\n' % self.utcnow('%Y-%m-%d %H:%M:%S') )
            file.write(self.utcnow('%H:%M:%S') + ' ' + text + '\n\n')  # 时间 + 内容

    @property
    def LEVEL(self):
        return self._LEVEL
    
    # 设置日志等级,分为'INFO','WARN','ERROR','STOP'四个级别
    @LEVEL.setter
    def LEVEL(self, level:str):
        ''' 设置日志等级,分为'INFO','WARN','ERROR','STOP'四个级别:
            1. 'INFO' 输出所有日志信息,即[INFO],[WARN]和[ERROR];\n
            2. 'WARN' 输出[WARN]和[ERROR]级别的信息;\n
            3. 'ERROR'只输出[ERROR]级别信息;\n
            4. 'STOP' 停止输出上述三种级别信息;\n
            5. 此外,Write函数可以输出任意自定义信息,不受Level影响.
        '''
        if level == 'INFO':
            self._LEVEL = self._INFO
        elif level == 'WARN':
            self._LEVEL = self._WARN
        elif level == 'ERROR':
            self._LEVEL = self._EROR
        elif level == 'STOP':
            self._LEVEL = self._STOP

    # 只有在'INFO'级别时才起作用
    def INFO(self, label: str = '', text: str = ''):
        if self.LEVEL == self._INFO:
            self.Write('[INFO -- %s] ' % label + text)

    # 'WARN'以下级别才起作用
    def WARN(self, label: str = '', text: str = ''):
        if self.LEVEL <= self._WARN:
            self.Write('[WARN -- %s] ' % label + text)

    # 'ERROR'以下级别才起作用
    def ERROR(self, label: str = '', text: str = ''):
        if self.LEVEL <= self._EROR:
            self.Write('[ERROR -- %s] ' % label + text)