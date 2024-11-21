import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("dump.dat")
# data -= max(data)


fft = np.fft.fft(data)
plt.plot(np.linspace(0, 1000, len(fft)), fft)
fhp = 1
fc1 = int(40 * (len(fft) / 1000))
fc2 = int(60 * (len(fft) / 1000))
print(fhp)
fft[fc1:fc2] = 0
fft[:fhp] = 0
fft[-fc2:-fc1] = 0
fft[-fhp:] = 0
plt.plot(np.linspace(0, 1000, len(fft)), fft)
plt.ylim(0, 2)

plt.figure()
plt.plot(data - max(data))
plt.plot(np.fft.ifft(fft))
plt.show()