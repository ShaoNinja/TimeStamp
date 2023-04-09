# -*- encoding: utf-8 -*-

##
import matplotlib.pyplot as plt

class fig:

    container = []

    def __init__(self):
        # 解决标签无法显示中文的问题, 参考链接如下
        # https://blog.csdn.net/weixin_43343803/article/details/90551321
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

    def plot(self, x, y, linewidth=0.5, holdon=False):
        # 默认新建图窗
        if not holdon:
            self.container = []
            plt.figure()

        # 绘图
        self.container += plt.plot(x, y, linewidth=linewidth)
        plt.grid(linestyle='-.', linewidth=0.5)

        # 展示
        # if show: self.show()

    def set(self, xlim=None, ylim=None, show=False,
            title=None, titlesize=14,
            xlabel=None, ylabel=None, labelsize=12):
        # limit
        if   xlim is not None: plt.xlim(xlim[0], xlim[1])
        if   ylim is not None: plt.xlim(ylim[0], ylim[1])
        # label
        if xlabel is not None: plt.xlabel(xlabel, fontsize=labelsize)
        if ylabel is not None: plt.ylabel(ylabel, fontsize=labelsize)
        if  title is not None: plt.title(xlabel,  fontsize=titlesize)

        # show
        if show: self.show()

    def legend(self, labels=None, show=False):
        for i, c in enumerate(self.container):
            if labels[i] == '': continue
            c.set_label(labels[i])
        plt.legend(loc='best', frameon=False, ncol=2)
        # show
        if show: self.show()
    
    def new(self):
        self.container = []
        plt.figure()

    def show(self):
        self.container = []
        plt.show()
