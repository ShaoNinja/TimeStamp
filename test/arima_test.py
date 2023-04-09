##
import pmdarima.arima as pm  # pmdarima的旧版本是pyramid
import numpy as np

x = np.random.normal(0,1,(1002,1))+2
x = x[0:-2] + 0.2*x[1:-1] - 0.4*x[2:] + 1
model_f = pm.auto_arima(x,trace=True,stepwise=True)
valid = model_f.predict_in_sample(start=990,dynamic=True)

data_fitted = model_f.predict_in_sample(start=model_f.order[0]+model_f.order[1])


data_fitted[900:] = model_f.predict_in_sample(start=900,dynamic=True)


v = model_f.summary()

np.array(model_f.order)

## 绘图对比
import matplotlib.pyplot as plt

import TimeStamps.plot.figure as fig

fig.plot(range(0,1000),data_fitted)

fig.plot(range(990,1000),x[990:1000])
fig.plot(range(990,1000),valid,holdon=True)