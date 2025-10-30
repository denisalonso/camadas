import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import sounddevice as sd
import soundfile as sf

fs = 44100                                                      # frequencia de amostragem
fc = 500                                                        # 500 Hz
dur = 4.0                                                       # duracao em segundos
n = int(fs*dur)                                                 # numero de instantes
t = np.linspace(0, dur, n, endpoint=False)                      # endpoint=False vamos pegar ate o t(n-1)

# sinal: soma de tons (alguns acima de 500Hz) + ruido leve
sig = 0.6*np.sin(2*np.pi*200*t)                                 # 200 Hz
sig += 0.3*np.sin(2*np.pi*800*t)                                # 800 Hz
sig += 0.2*np.sin(2*np.pi*1500*t)                               # 1500 Hz
sig += 0.05*np.random.randn(len(t))                             # ruido
sig /= float(np.max(np.abs(sig)))                               # normaliza picos (cada pico fica como uma porcentagem do pico maximo)

# FFT helper
def plot_fft(x, fs, title):
    N = len(x)
    X = np.fft.rfft(x * np.hanning(N))
    freqs = np.fft.rfftfreq(N, 1/fs)
    mag = 20*np.log10(np.abs(X)+1e-12)
    plt.semilogx(freqs, mag)
    plt.xlim(20, fs/2)
    plt.xlabel('Hz'); plt.ylabel('magnitude (dB)')
    plt.title(title); plt.grid(True)

plt.figure(figsize=(10,4))
plot_fft(sig, fs, "FFT - sinal original")
plt.tight_layout()
plt.show()

# coeficientes de butterworth
b, a = signal.butter(N=2,Wn=fc/(fs/2), btype='low')

# aplica filtro iir
sig_filt = signal.lfilter(b, a, sig)

plt.figure(figsize=(10,4))
plot_fft(sig_filt, fs, "sinal filtrado (butterworth passa-baixa, limiar: 500 Hz")
plt.tight_layout()
plt.show()

# reproduz audio original e filtrado
print("original")
sd.play(sig, fs); sd.wait()
print("filtrado")
sd.play(sig_filt, fs); sd.wait()

# salva audios
sf.write("ex1_original.wav", sig, fs)
sf.write("ex1_filtrado.wav", sig_filt, fs)
print("arquivos de audio salvos")
