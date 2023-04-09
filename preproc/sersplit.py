import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 字典解析
def myParser(Dict, flattenX=False):
    '''
    词典解析.
    Arguments:
        Dict: 词典类型. 包含着输入(X)和输出(Y)的列名, 以及预处理后的列名
              注意: 如果不设置预处理后的列名, 输入的列名一定要是唯一的且不存在相互包含的关系
        flattenX: Bool. 设置输出Xcols_in和Xcols_as是否摊平
    Returns:
        Xcols_in, Xcols_as: 两层List. X的列名, Supervised后的列名
        Ycols_in, Ycols_as: 单层List. Y的列名, Supervised后的列名
    Example:
        Dict = { 'Y': [('PC|-1', 'PCY')],    # 更改列名用tuple表示
                'X': { 0: ['PO|-1', 'PH|-1', 'PL|-1', 'PC|-1'],   # X可以有多类输入
                        1: ['VR'] } }        # 尽管X1只有一个变量, 也要用list表示
        Dict = { 'Y': [], 'X': { 0: df.columns } } # 尽管X只有一类输入, 也要用dict表示
            # 对于Series2Supervised而言, []代表空, 将不做任何处理
            # 对于TrainTest_split而言, []将使得输出*_Train和*_Test为空array
    '''
    # Y是单层的List, 元素是str, 对应列名
    Ycols_in = [ y[0] if type(y) is tuple else y for y in Dict['Y'] ]
    Ycols_as = [ y[1] if type(y) is tuple else y for y in Dict['Y'] ]
    # X是两层的List, 第一层是List, 对应不同类型的输入; 第二层是str, 对应同类型输入的列名
    Xcols_in = [ [ x[0] if type(x) is tuple else x for x in cols ] for cols in Dict['X'].values() ]
    Xcols_as = [ [ x[1] if type(x) is tuple else x for x in cols ] for cols in Dict['X'].values() ]
    if flattenX:   # 将两层List摊平为单层
        Xcols_in = sum(Xcols_in, []);  Xcols_as = sum(Xcols_as, [])

    return Xcols_in, Xcols_as, Ycols_in, Ycols_as


# 将时间序列转换为监督学习的数据类型
def Series2Supervised(df, Dict_in_out, LagMax=1, LeadS=1, dropnan=True):
    '''
    Frame a time series as a supervised learning dataset.
    Arguments:
        df:  DataFrame. Sequence of observations.  !!按时间升序排列, 其index为datetime格式!!
        Dict_in_out: Dict. 参见myParser()的Dict
        LagMax:  Int. Max lag of observations as input. like LagMax=5
        LeadS: Int or List. To specify which numbers the cols_out lead. like LeadS=[2,5]
        dropnan: Boolean. Whether or not to drop rows with NaN values.
    Returns:
        Pandas DataFrame of series framed for supervised learning.
    '''
    # 字典解析 ==> X的列名(as列名), Y的列名(as列名)
    Xcols_in, Xcols_as, Ycols_in, Ycols_as = myParser(Dict_in_out, flattenX=True)

    # 若数字为0，则返回'-0'，否则返回带正负号的字符串
    def myStr(x): return {0: ''}.get(x, '%+d' % x)

    # copy input.index to output.index
    agg = pd.DataFrame(index=df.index)
    if Xcols_in != []:       # 在Xcols_in!=[]时才执行
        # input sequence (t-n, ... t-1, t)
        for i in range(LagMax, -1, -1):
            names = [ ('%s(t%s)' % (name, myStr(-i))) for name in Xcols_as ]
            agg[names] = df[Xcols_in].shift(i)

    # convert 'LeadS' to type list
    LeadS = ( lambda x: x if type(x) is list else [x] )( LeadS )
    if Ycols_in != []:      # 在Ycols_in!=[]时才执行
        # forecast sequence (t+1, ... t+n)
        for i in LeadS:
            names = [ ('%s(t%s)' % (name, myStr(i))) for name in Ycols_as ]
            agg[names] = df[Ycols_in].shift(-i)

    # drop the Consecutive empty lines
    saveCase = max( LeadS + [1] )          # 至少保留1例 不做dropna
    a = agg.iloc[:-saveCase].isnull().T.any().reset_index(drop=True)       # 判断每行是否有空值, 然后设置索引为number
    Last_Empty, First_Full = a[a.values].index[-1], a[~a.values].index[0]  # ==> a.values[空行行号] = True
    if First_Full == Last_Empty + 1:    # 连续的空行必删除
        agg = agg.iloc[First_Full:, :]
    else:
        # 展示不连续的空行, 最后的saveCase行除外
        plt.figure(figsize=(10, 2)); plt.plot(agg.index[:-saveCase], a.values)
        plt.title('数据缺失不连续，如图所示, ');  plt.show()
        # ~dropnan时，空行的不连续存放将导致报错
        if dropnan is False: sys.exit('[WARNING] -- 数据的缺失行不连续, 请检查')

    # dropnull时, 删除不连续的空行, 最后的saveCase行除外，因为这几行数据是测试集
    # 其实也是要求测试集的输入不能为空，因为输入为空必然导致预测误差较大
    return ( agg.iloc[:-saveCase, :].dropna(axis=0) ).append( agg.iloc[-saveCase:, :] ) if dropnan else agg

# 训练集和测试集的划分
def TrainTest_split(df, Dict_in_out, NTestCase=30, NXLag=25):
    '''
    将Series2Supervised()的输出划分为训练集和测试集
    Arguments:
        df:  DataFrame. Series2Supervised()的输出
        Dict_in_out: Dict. 具体见myParser()的解释
        NTestCase:  Int. 测试集的个数
        NXLag: Int. 输入(X)的
    Returns:
        X_Train, X_Test: 3D array, if Dict_in_out 对应多类输入 else 2D array
        Y_Train, Y_Test: 2D array
    '''

    # 获取X和Y所属列包含的关键词
    _, Xcols_as, _, Ycols_as = myParser(Dict_in_out, flattenX=False)
        # 若Xcols_as为[[]]或Ycols_as为[], 则输出空array

    cols = []       # cols对应的是Y的特征 (可能是多维的)
    for f in Ycols_as:
        cols += [ x for x in df.columns if x.find(f) >= 0 ]   # x.find('') = 0
    Y_Train = np.array(df[cols].iloc[:-NTestCase, :])
    Y_Test  = np.array(df[cols].iloc[-NTestCase:, :])

    X_Train, X_Test = [], []

    for i in range(len(Xcols_as)):
        # axis 0 对应样本数, axis 1 对应时间长度, axis 2 对应特征个数
        Train = np.zeros(( Y_Train.shape[0], NXLag, len(Xcols_as[i]) ))
        Test  = np.zeros(( Y_Test .shape[0], NXLag, len(Xcols_as[i]) ))
        for j, f in enumerate(Xcols_as[i]):   # 在axis 2上堆叠
            cols = [ x for x in df.columns if x.find(f) >= 0 ]
            Train[:, :, [j]] = np.array(df[cols].iloc[:-NTestCase, :])[:, :, None]  # None 与 np.newaxist 等价
            Test [:, :, [j]] = np.array(df[cols].iloc[-NTestCase:, :])[:, :, None]  # 插入新的维度，使其变为3D array
        X_Train.append(Train)
        X_Test.append(Test)

    if len(Xcols_as) == 1:  X_Train, X_Test = X_Train[0], X_Test[0]

    return X_Train, X_Test, Y_Train, Y_Test



''' 备用 Series2Supervised_Backup
def Series2Supervised_Backup(df, cols_in=[], LagMax=1, cols_out=[], LeadS=1, dropnan=True):
    # 如果为str，则转化为[str] => 如果为空list，则返回df的所有列名 => 否则保持
    def getCols(x): return {str: [x]}.get( type(x), {0: df.columns}.get(len(x), x) )
    # 若数字为0，则返回''，否则返回带正负号的字符串
    def fs(x): return {0: ''}.get(x, '%+d' % x)
    cols, names = list(), list()
    # 转化 cols_in 和 cols_out 的格式
    cols_in, cols_out = [ getCols(x) for x in (cols_in, cols_out) ]
    # input sequence (t-n, ... t-1, t)
    if cols_in != ['']:       # 在cols_in!=['']时才执行
        for i in range(LagMax, -1, -1):
            cols.append(df[cols_in].shift(i))  # 数据向下平移i个单位，相当于获取了过去的数据
            names += [('%s(t%s)' % (name, fs(-i))) for name in df[cols_in].columns]
    # forecast sequence (t+1, ... t+n)
    if cols_out != ['']:      # 在cols_out!=['']时才执行
        for i in np.array([LeadS]).reshape(-1):
            cols.append(df[cols_out].shift(-i))  # 数据向上平移i个单位，相当于获取了未来的数据
            names += [('%s(t%s)' % (name, fs(i))) for name in df[cols_out].columns]
    # put it all together
    agg = pd.concat(cols, axis=1);  agg.columns = names
    # drop rows with NaN values
    return agg.dropna() if dropnan else agg
'''

''' 备用 TrainTest_split
    Y_Train, Y_Test = TrainTest_split(wash_mat, NTestCase, Condition=['PH|+G'] )
    X1_Train, X1_Test = TrainTest_split(wash_mat, NTestCase, Condition=['PC|-1'], ReShape=True )
    X2_Train, X2_Test = TrainTest_split(wash_mat, NTestCase, Condition=['VR'], ReShape=True )
    def TrainTest_split(df, NTestCase=30, Cols=[''], ReShape=False):

    cols = df.columns
    for f in Cols:
        cols = [ x for x in cols if x.find(f) >= 0 ]   # x.find('') = 0

    Train = np.array(df.iloc[:-NTestCase, :][cols])
    Test  = np.array(df.iloc[-NTestCase:, :][cols])

    # convert and reshape to 3D array
    if ReShape:
        [Train, Test] = [ x.reshape(x.shape[0], -1, 1) for x in [Train, Test] ]

    return Train, Test
'''
