import matplotlib.pyplot as plt
import numpy as np
import random

# https://gist.github.com/dougmcnally/c8f3cf1b4d0740934ed4b028c4b67276

n = 1024

x = np.zeros(n)
y = np.zeros(n)

for i in range(1, n):
    val = random.randint(1, 4)
    if val == 1:
        x[i] = x[i - 1] + 1
        y[i] = y[i - 1]
    elif val == 2:
        x[i] = x[i - 1] - 1
        y[i] = y[i - 1]
    elif val == 3:
        x[i] = x[i - 1]
        y[i] = y[i - 1] + 1
    else:
        x[i] = x[i - 1]
        y[i] = y[i - 1] - 1

fig = plt.figure(figsize=(10,10))
plt.plot(x,y)
fig.show()
plt.show()