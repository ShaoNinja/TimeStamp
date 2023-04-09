# -*- encoding: utf-8 -*-

import numpy as np
import TimeStamps.plot.figure as fig
pi = np.pi

## Fourier分析
def myFFT(series, dt, x_type='Frq', y_type='Amp', Nzp=None, result='d', holdon=False):
    ''' 使用说明
        Input
        ------
        `series` : 一维时间序列
        `dt` : 序列的采样间隔
        `x_type` : 图像的x轴代表什么
            'Frq' : 频率   [-1/dt,1/dt) —— 缺省/默认值 i.e.cycles-per-dt
            'Nfrq': 归一化频率   [-1/2,1/2)
            'Omg' : 角频率 [-pi/dt,pi/dt)
            'Nomg': 归一化角频率 [-pi,pi)
            'Per' : 周期
        `y_type` : 振幅频谱图的y轴代表什么
            'Amp' : 振幅 —— 缺省/默认值
            'Pow' : 功率
            'Dec' : 分贝: 20*log10(abs(Amp))
        `Nzp` : 零填充后的序列长度
            缺省/默认值 : Nzp取为输入序列长度
            若Nzp大于序列长度, 在序列之后填零
            若Nzp小于序列长度, 则截断原始序列
        `window` : 窗函数
            矩形窗 : np.ones —— 缺省/默认值
            三角窗 : np.bartlett
            其他窗函数 : np.hanning, np.hamming, np.kaiser, np.blackman
        `result` : 返回data和fig的标志
            'd'    : 只返回data —— 缺省/默认值
            'f1'   : 只返回fig(只有振幅图)
            'f2'   : 只返回fig(振幅图和相位图)
            'd+f1' : 返回data+fig(只有振幅图)
            'd+f2' : 返回data+fig(振幅图和相位图)
        `holdon` : 同Matlab的hold on
            True  : 若有图窗没使用plt.show(),则继续在之上绘图
            False : 新建图窗 —— 缺省/默认值

        Output
        ------
        `x` : 输出序列的自变量, 由'x_type'指定
        `y` : 输出序列的因变量, 由'y_type'指定
    '''
    Ns  = series.shape[0]   # 序列原始长度
    if Nzp is None:         # Nzp缺省->取为原始数据长度Ns
        Nzp = Ns
    elif Nzp < Ns:          # Nzp比Ns还小->截断数据
        series, Ns = series[:Nzp], Nzp
    # 获取序列的实/复性
    flag_iscomplex = np.iscomplex(series).all()
    series = series.reshape(-1,)   # 整理成普通数组
    # 计算x轴
    Omg_Nom = np.fft.fftfreq(Nzp) * (2*pi)  # [0,pi)∪[-pi,0)
    Omg_Nom = np.fft.fftshift(Omg_Nom)      # 交换顺序 -> [-pi,pi)
    if   x_type == 'Frq':                # 频率:cos(2*pi*F*t)中的F
        x = Omg_Nom / (2*pi*dt)             # 取值范围[0,2/dt) -> [-1/dt,1/dt)
    elif x_type == 'Nfrq':               # 归一化频率:cos(2*pi*f*n)中的f, f=F*dt
        x = Omg_Nom / (2*pi)                # 取值范围[0,1) -> [-1/2,1/2)
    elif x_type == 'Omg':                # 角频率:cos(W*t)中的W, W=2*pi*f
        x = Omg_Nom / dt                    # 取值范围[0,2pi/dt) -> [-pi/dt,pi/dt)
    elif x_type == 'Nomg':               # 归一化角频率:cos(w*n)中的w, w=W*dt
        x = Omg_Nom                         # 取值范围[0,2pi) -> [-pi,pi)
    elif x_type == 'Per':                # 周期:cos(2*pi/P*t)中的P, P=1/f=2*pi/w
        x = np.divide(2*pi*dt, Omg_Nom)     # 注意周期P与dt的量纲一致.
        # = (2*np.pi*dt) / Omg_Nom       # 使用divide函数的原因: divide(1,0)=inf
    else:
        raise ValueError('[ERROR] - wrong value of `x_type`')

    # 计算y轴
    F = np.fft.fft(series, n=Nzp)      # 对序列做FFT变换
    y = np.fft.fftshift(F)             # 交换顺序，用于绘图
    if   y_type == 'Amp':
        y = np.abs(y) / Ns
    elif y_type == 'Pow':
        pass
    elif y_type == 'Dec':
        pass
    else:
        raise ValueError('[ERROR] - wrong value of `y_type`')

    # 根据序列实/复性对y值进行修正
    if not flag_iscomplex: y = y*2
        # W=0和-pi处的y值再除以2
        # if Nzp % 2 == 0:  # Nzp是偶数
        #     y[1] = y[1] / 2  #

    # 绘图代码
    if 'f' in result:
        # 根据序列实/复性获取index
        idx = [True]*Ns if flag_iscomplex else (x >= 0)
        if   'f1' in result:
            fig.plot(x[idx], y[idx],  linewidth=0.75, holdon=holdon)
        elif 'f2' in result:
            angle = np.arctan2(F.imag, F.real)  # 相位角 in the range [-pi, pi]
            fig.plt.subplot(211)                # 振幅图
            fig.plot(x[idx], y[idx],      linewidth=0.75, label='振幅')
            fig.plt.subplot(212)                # 相位图
            fig.plot(x[idx], angle[idx],  linewidth=0.75, label='相位')
        else:
            raise ValueError('[ERROR] - wrong value of `flag_return`')
    
    # 返回‘完整’数据 (对于实序列,图像只展示了一半)
    if 'd' in result: return x, y
