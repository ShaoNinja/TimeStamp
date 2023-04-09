####################################
## WARN: Don't Revise by Matlab ! ##
## UTF-8 Encoding, Don't Change ! ##
## 警告: 不要再Matlab中修改此文件 ##
## 要以UTF-8格式保存修改后的文件  ##
####################################

import numpy as np
import array                 # Python格式转Matlab
import pmdarima.arima as pm  # pmdarima的旧版本是pyramid
from pmdarima import preprocessing as ppc

# 双边预测
def P2M_auto_arima(data, K_predict, start_p):
    '''
        在matlab中调用该函数，再使用double函数将其转化为矩阵
        参考连接 https://zhuanlan.zhihu.com/p/92081119?from_voters_page=true
    '''
    data = np.array(data)       # Maltab输入的矩阵默认为array.array类型，要先转为numpy数组。
    K_predict = int(K_predict)  # Matlab输入数值默认为double，所以要先转为int
    start_p   = int(start_p)

    data_extend, fit_forecast_forward, fit_forecast_backward = auto_arima(data, K_predict, start_p)

    # 转化为Matlab可以接收的类型
    return array.array('d', data_extend), array.array('d', fit_forecast_forward), array.array('d', fit_forecast_backward)

# 使用Fourier级数实现长季节性ARIMA模型，一般SARIMA的季节差分大约是20阶
def P2M_farima_predict(data, K_predict, start_p, mS, kS):
    '''
        变量定义参考 auto_farima_predict()
    '''
    # 将Matlab变量转化为Python接收的类型
    data = np.array(data)       # Maltab输入的矩阵默认为array.array类型，要先转为numpy数组。
    K_predict, start_p, mS, kS  = int(K_predict), int(start_p), int(mS), int(kS)
        # Matlab输入数值变量默认为double类型，这里将其转为int
    # 调用Python函数
    fit_forecast_forward, orders = auto_farima_predict(data, K_predict, start_p, mS, kS)
    # 将结果转化为Matlab接收的类型
    return array.array('d', fit_forecast_forward), array.array('d',orders)

# 用于WARIMA预报,单边预测
def P2M_warima(data, K_valid, K_predict, start_p):
    # 变量转换
    data = np.array(data)   # Maltab输入的矩阵默认为array.array类型，要先转为numpy数组。
    K_predict, K_valid, start_p  = int(K_predict), int(K_valid), int(start_p)

    # 提前判断d，建模速度更快
    n_diffs = pm.ndiffs(data, max_d=2)

    # building the model
    model_f = pm.auto_arima(data, d=n_diffs,max_p=50, max_q=50, start_p=start_p,
                            stepwise=True, seasonal=False, trace=True,
                            error_action='warn', suppress_warnings=True)

    # 计算数据长度,拟合数据的起始点
    N, idfit = data.shape[0], model_f.order[0]+model_f.order[1]
    # 计算验证数据的起始点
    idvid = N - idfit - K_valid
    
    # 预测集
    data_predict = model_f.predict(K_predict)
    # 拟合集
    data_fitted = model_f.predict_in_sample(start=idfit)
    # 验证集
    data_fitted[idvid:] = model_f.predict_in_sample(start=N-K_valid, dynamic=True)  # 验证集
    # 结果=拟合集+验证集+预测集
    result = np.concatenate((data[0:idfit],data_fitted, data_predict), axis=0)
    # 返回matlab接受的格式, 注意python传回的一维数组是行向量
    return array.array('d', result)


def auto_farima_predict(data: np.ndarray, K_predict: int, start_p: int = 30, mS: int = 365, kS: int = 4):
    '''
        data: N行?列，行代表时间，列代表变量
        start_p: The starting value of p, the order of the AR model.
                0<=p<=50. 推荐将start_p设为15,20,25,30等,
                数值越大，拟合越准；数值越小，速度越快。
        K_predict: 左右预测的长度
        mS: 季节项的周期（对应数据点数量）
            对于1d采样的数据,mS=365代表一年,183代表半年。
        kS: 实际有kS个周期项,分别为mS./(1:kS)
    '''
    # Fourier法处理季节项，速度更快，使用的模型是固定周期模型
    ppc.FourierFeaturizer(m=mS, k=kS)   # 若k=4,则设定的周期依次为mS./[1,2,3,4]
        # 参考链接：https://robjhyndman.com/hyndsight/longseasonality/
    
    # 提前判断d，建模速度更快
    n_diffs = pm.ndiffs(data, max_d=2)

    # building the model
    model_f = pm.auto_arima(data, d=n_diffs,max_p=50, max_q=50, start_p=start_p,
                            stepwise=True, seasonal=False, trace=True,
                            error_action='warn', suppress_warnings=True)
        # method='nm'速度比'lbfgs'快很多
        # 参数如何设置，参考链接: https://alkaline-ml.com/pmdarima/1.6.1/tips_and_tricks.html#other-performance-concerns

    # 用预测值扩展输入数据并返回
    data_fitted = model_f.predict_in_sample()
    data_predict = model_f.predict(K_predict)

    # fit in model + forward predict
    data_fit_pred = np.concatenate((data_fitted, data_predict), axis=0)

    return data_fit_pred, model_f.order

# 该函数使用stepwise算法，且不限制d为0
def auto_arima(data: np.ndarray, K_predict: int, start_p: int = 30):
    '''
        data: N行?列，行代表时间，列代表变量
        start_p: The starting value of p, the order of the AR model. 
                0<=p<=50. 推荐将start_p设为15,20,25,30等，
                数值越大，拟合越准；数值越小，速度越快。
        K_predict: 左右预测的长度
    '''

    # 向右预测, 为提高精度p从30开始
    model_f = pm.auto_arima(data, max_p=50, max_q=20, start_p=start_p,
                            stepwise=True, seasonal=False, trace=True,
                            error_action='warn', suppress_warnings=True)  # building the model

    print('\n\'前\'向预测模型: (p, d, q) = ', model_f.order, ' AIC = ', model_f.aic(), '\n')

    # 向左预测, 为提高精度p从30开始
    tmp = np.flip(data, 0)  # 序列上下翻转
    model_b = pm.auto_arima(tmp, max_p=50, max_q=20, start_p=start_p,
                            stepwise=True, seasonal=False, trace=True,
                            error_action='warn', suppress_warnings=True)   # building the model
    print('\n\'后\'向预测模型: (p, d, q) = ', model_b.order, ' AIC = ', model_b.aic(), '\n')

    # 用预测值扩展输入数据并返回
    sample_fit_forward = model_f.predict_in_sample()
    forecast_forward = model_f.predict(K_predict)
    sample_fit_backward = model_b.predict_in_sample()
    forecast_backward = model_b.predict(K_predict)
    # fit in model + forecast to right
    fit_forecast_forward = np.concatenate((sample_fit_forward, forecast_forward), axis=0)
    # fit in model + forecast to left
    fit_forecast_backward  = np.flip( np.concatenate((sample_fit_backward, forecast_backward), axis=0), 0)
    # forecast to bothside + training data
    data_extend = np.concatenate((np.flip(forecast_backward, 0), data, forecast_forward), axis=0)

    return data_extend, fit_forecast_forward, fit_forecast_backward

# 给定前向预测和后向预测模型的阶数，对输入输入data进行拟合和预测
def arima(data: np.ndarray, K_predict: int, order_forward, order_backward):
    '''
        data: N行?列，行代表时间，列代表变量
        order_forward:  (p,d,q), 前向预测模型的阶数
        order_backward: (p,d,q), 后向预测模型的阶数
        K_predict: 前后预测的长度
    '''
    # Construct an ARIMA
    model_f = pm.ARIMA(order=order_forward)
    model_b = pm.ARIMA(order=order_backward)
    # fit the data
    forecast_forward = model_f.fit_predict(data, n_periods=K_predict)
    forecast_backward = model_b.fit_predict(np.flip(data, 0), n_periods=K_predict)
    
    # predict in sample
    sample_fit_forward = model_f.predict_in_sample()
    sample_fit_backward = model_b.predict_in_sample()
    print('\n\'前\'向预测模型: (p, d, q) = ', model_f.order, ' AIC = ', model_f.aic())
    print('\'后\'向预测模型: (p, d, q) = ', model_b.order, ' AIC = ', model_b.aic(), '\n')

    # fit in model + forecast to right
    fit_forecast_forward = np.concatenate((sample_fit_forward, forecast_forward), axis=0)
    # fit in model + forecast to left
    fit_forecast_backward  = np.flip( np.concatenate((sample_fit_backward, forecast_backward), axis=0), 0)
    # forecast to bothside + training data
    data_extend = np.concatenate((np.flip(forecast_backward, 0), data, forecast_forward), axis=0)

    return data_extend, fit_forecast_forward, fit_forecast_backward


## Test
# import math
# import matplotlib.pyplot as plt
# data = np.array([math.cos(x) + x + math.sin(2*x) for x in np.linspace(0, 10, 50)])
# data_extend, _, _ = auto_arima_stepwise(data, 10)
# plt.plot(np.linspace(-2, 12, 70), data_extend, label='Forcast')
# plt.plot(np.linspace(0, 10, 50), data, label='Train')

##  example provided by the authorities
# http://alkaline-ml.com/pmdarima/1.6.1/auto_examples/arima/example_auto_arima.html#sphx-glr-auto-examples-arima-example-auto-arima-py
# auto_arima详解：http://alkaline-ml.com/pmdarima/1.6.1/modules/generated/pmdarima.arima.auto_arima.html
