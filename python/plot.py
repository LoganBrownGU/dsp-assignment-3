import matplotlib.pyplot as plt
import numpy as np

callback = np.loadtxt("assets/callback.dat")
uart = np.loadtxt("assets/uart.dat")
filtered  = np.loadtxt("assets/filtered.dat")
input = np.loadtxt("assets/input.dat")
ideal_uart = np.transpose(np.loadtxt("assets/ideal_uart.dat"))

def t(data):
    return np.linspace(0, len(data) / 1000, len(data))

plt.tight_layout()
plt.title("Sampling time")
plt.plot(t(callback), callback / (10**6), label="Time taken per sample")
plt.plot([0, t(callback)[-1]], [1, 1], "r--", label="Limit")
plt.xlabel("Time (s)")
plt.ylabel("Sample time (ms)")
plt.legend()
plt.savefig("../report/figures/sampling.pdf")

plt.figure()
plt.tight_layout()
plt.title("UART Tx vs UART Rx")
plt.plot(t(uart), uart, label="Input to UART Rx")
plt.plot(ideal_uart[0], ideal_uart[1] * np.max(uart), "--", label="Output from UART Tx (scaled)")
plt.xticks(np.arange(0, t(uart)[-1] + 0.1, 0.1))
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True, which="both", axis="x")
plt.legend()
plt.savefig("../report/figures/uart.pdf")

plt.figure()
plt.tight_layout()
plt.title("IIR filtered data")
plt.plot(t(filtered), filtered)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.savefig("../report/figures/filtered.pdf")

plt.figure()
plt.tight_layout()
plt.title("Raw input to filter")
plt.plot(t(input), input)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.savefig("../report/figures/raw.pdf")

# plt.show()