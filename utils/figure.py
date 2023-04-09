# -*- encoding: utf-8 -*-

##
from matplotlib import pyplot as plt
import matplotlib.style as mplstyle
import os

# 设置快速样式,加快绘图速度.并确保fast在最后
# https://blog.csdn.net/jeffery0207/article/details/81317000
mplstyle.use(['seaborn-deep', 'fast'])
# matplotlib绘图风格,参考下面链接. seaborn-deep效果不错
# https://blog.csdn.net/justisme/article/details/100543869

# 解决标签无法显示中文的问题
plt.rcParams['font.sans-serif'] = ['Helvetica']         # matlab字体
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']   # 微软雅黑,可显示中文
plt.rcParams['axes.unicode_minus'] = False              # 用来正常显示负号

# matplotlib 查看所有可设置字体
# import matplotlib
# a = sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])
# print(a)

container = []     # 容器, 用于放置axes

STAGE = 'test'     # 'test' 'show' 'save', 默认'test'

HOLD = False       # holdon 全局设置, 仅使用一次

FIGwidth, FIGheight, FIGdpi = 8, 5.8, 300

# 全局设置
def stage(stage: str, figwidth=FIGwidth, figheight=FIGheight, figdpi=FIGdpi):
    # 设置阶段
    global STAGE, FIGwidth, FIGheight, FIGdpi
    if stage.lower() in ['test', 'show', 'save']:
        STAGE = stage
    else:
        raise ValueError('wrong value of `stage`')
    # 设置图像参数
    FIGwidth, FIGheight, FIGdpi = figwidth, figheight, figdpi
    # 清空容器
    container.clear()

def subplot(*args, stick=True):
    global HOLD; HOLD = True
    plt.subplot(*args, frameon=stick)
    if STAGE.lower() in ['show','save']:
        plt.gcf().set_figwidth(FIGwidth)
        plt.gcf().set_figheight(FIGheight)

def stem(*args, label=None, linewidth=0.5, line='-', marker=' ', holdon=False):
    # holdon和HOLD有一个为True就不新建图窗
    if not (holdon or HOLD): new()
    # 绘图
    if label is None or label == '':
        ax = plt.stem(*args, linefmt=line, markerfmt=marker,  basefmt=' ')
    else:
        ax = plt.stem(*args, linefmt=line, markerfmt=marker,  basefmt=' ', label=label)
        leg = plt.legend(loc='best', frameon=False, ncol=2)
        leg.legendHandles[0].set_linewidth(linewidth)       # 设置legend的线宽
        ax[1].set_linewidth(linewidth)    # 竖线 matplotlib.collections.LineCollection
        # ax[0].set_markersize(linewidth) # 标记 matplotlib.lines.Line2D
    container.append(ax)                  # stem的axes包含3个元素
    # 绘制格网
    plt.grid(b=True, linestyle='-.', linewidth=0.5)


def plot(*args, label=None, linewidth=0.75, holdon=False):
    # holdon和HOLD有一个为True就不新建图窗
    if not (holdon or HOLD): new()
    # 绘图
    if label is None or label == '':
        ax = plt.plot(*args, linewidth=linewidth)
    else:
        ax = plt.plot(*args, linewidth=linewidth, label=label)
        plt.legend(loc='best', frameon=False, ncol=2)
    container.extend(ax)
    # 绘制格网
    plt.grid(b=True, linestyle='-.', linewidth=0.5)

def set(xlim=None, ylim=None,
        title=None, titlesize=11.5, label=None,
        xlabel=None, ylabel=None, labelsize=11.5,
        show=False):
    # 如果仅仅用于测试, 则将字体调小
    # 若用于Word文档, 12号的字体很合适
    if STAGE.lower() == 'test':
        titlesize, labelsize = 10, 10
    # limit
    if   xlim is not None: plt.xlim(xlim[0], xlim[1])
    if   ylim is not None: plt.ylim(ylim[0], ylim[1])
    # title
    if  title is not None: plt.title(title,  fontsize=titlesize)
    # legend of current axes
    if  label is not None:
        container[-1].set_label(label)
        plt.gcf().axes[-1].legend(loc='best', frameon=False, ncol=2)
    # x/y label
    if xlabel is not None: plt.xlabel(xlabel, fontsize=labelsize)
    if ylabel is not None: plt.ylabel(ylabel, fontsize=labelsize)
    # show
    if show: showing()

# 仅设置axes.lines里的legend
def legend_lines(labels=None, show=False):
    lines_gca = plt.gca().lines
    for i, l in enumerate(lines_gca):
        if labels[i] == '': continue
        l.set_label(labels[i])
    plt.legend(loc='best', frameon=False, ncol=2)
    # show
    if show: showing()

# 设置container里每一个axes的Legend
def legend(labels=None, show=False):
    # 如果lables是str类型,将其转为list
    if isinstance(labels, str): labels = [labels]
    # 逐一设置label
    for i, c in enumerate(container):
        if labels[i] == '': continue
        c.set_label(labels[i])
    # 对于每个子图，都要调用.legend()方法
    for ax in plt.gcf().axes:
        ax.legend(loc='best', frameon=False, ncol=2)
    # show
    if show: showing()

def new():  # 清空容器, 创建新fig
    global HOLD; HOLD = False
    container.clear()
    # 创建图窗
    plt.figure()
    if STAGE.lower() in ['show','save']:
        plt.gcf().set_figwidth(FIGwidth)
        plt.gcf().set_figheight(FIGheight)
        if STAGE.lower() == 'save':
            plt.gcf().set_figdpi(FIGdpi)

def save(filename='tmp.svg', path=None):
    # 获取存储路径
    if path is None: path = os.getcwd() + '/'
    # 判断路径的末尾是否存在'/'或'\\',若不存在则添加'/'
    if path[-1] != '/' and path[-2:] != '\\':
        path = path + '/'
    # save 背景是透明的
    if STAGE.lower() == 'save':
        mplstyle.use(['seaborn-deep'])            # 取消fast
        plt.savefig( path + filename, transparent=True, dpi=FIGdpi)
        mplstyle.use(['seaborn-deep', 'fast'])    # fast仅用于展示
    else:
        plt.savefig( path + filename, transparent=True)

def showing():  # 清空容器, 展示fig
    container.clear()
    # if backen is not None:
    #     plt.switch_backend(backen)
    # else:
    #     backen = 'TkAgg'
    # # 判断启用的是否是webagg
    # if backen.lower() == 'webagg':
    #     import nest_asyncio
    #     nest_asyncio.apply()
    # show完不需关闭，程序自动向下执行
    plt.ion()
    # show完不需关闭，程序自动向下执行
    plt.show()
