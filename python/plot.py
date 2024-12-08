import matplotlib.pyplot as plt
import numpy as np

callback = np.loadtxt("assets/callback.dat")
uart = np.loadtxt("assets/uart.dat")
filtered  = np.loadtxt("assets/filtered.dat")
input = np.loadtxt("assets/input.dat")

def t(data):
    return np.linspace(0, len(data) / 1000, len(data))

plt.plot(t(callback), callback / (10**6), label="Time taken per sample")
plt.plot([0, t(callback)[-1]], [1, 1], "r--", label="Limit")
plt.xlabel("Time (s)")
plt.ylabel("Sample time (ms)")
plt.legend()

plt.figure()
plt.plot(t(uart), uart)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.figure()
plt.plot(t(filtered), filtered)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.figure()
plt.plot(t(input), input)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.show()