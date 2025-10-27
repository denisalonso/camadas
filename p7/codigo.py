import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import lfilter, freqz, convolve


def peaking_eq(f0, gain_db, Q, fs):
    #so pode ganho no intervalo permitido entre -10 e 10 dB
    gain_db = np.clip(gain_db, -10, 10) 
    
    A = 10**(gain_db / 40) 
    omega = 2 * np.pi * f0 / fs
    alpha = np.sin(omega) / (2 * Q)

    # Coeficientes do Numerador (b)
    b0 = 1 + alpha * A
    b1 = -2 * np.cos(omega)
    b2 = 1 - alpha * A
    
    # Coeficientes do Denominador (a)
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(omega)
    a2 = 1 - alpha / A

    # Normalização
    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0
    return b, a


def main():
    fs = 44100              # ts
    Q_valor = 1.0           # fq
    duration = 4            

    frequencias = np.array([20, 32, 64, 125, 250, 500, #12 bandas
                            1000, 2000, 4000, 8000, 16000, 20000])

    
    ganhos_db = np.array([0, 0, 8, 3, 0, 0, 
                          0, 0, 0, 10, 5, 0])
    
    print("Iniciando Equalizador Digital.")
    print("Ganhos configurados (dB):", dict(zip(frequencias, ganhos_db)))

    #geramos matematicamnete
    tempo = np.linspace(0., duration, int(fs * duration), endpoint=False)
    audio_original = (0.5 * np.sin(2 * np.pi * 100 * tempo) + 
                      0.3 * np.sin(2 * np.pi * 1000 * tempo) + 
                      0.2 * np.sin(2 * np.pi * 5000 * tempo))
    
    audio_original = audio_original / np.max(np.abs(audio_original))
    
    sinal_filtrado = audio_original.copy()
    b_coeffs_list = []
    a_coeffs_list = []

    print("\naplicando 12 filtros em cascata")
    for f0, gain_db in zip(frequencias, ganhos_db):
        # coeficientes
        b_i, a_i = peaking_eq(f0, gain_db, Q_valor, fs)
        b_coeffs_list.append(b_i)
        a_coeffs_list.append(a_i)
        
        # a saida de um é a entrada do outro
        sinal_filtrado = lfilter(b_i, a_i, sinal_filtrado)

    # normalização
    sinal_filtrado = sinal_filtrado / np.max(np.abs(sinal_filtrado))
    print("Filtragem concluída.")

    
    # Multiplicação das Funções de Transferência é a Convolução dos Coeficientes
    b_total = b_coeffs_list[0]
    a_total = a_coeffs_list[0]

    for i in range(1, len(b_coeffs_list)):
        b_total = convolve(b_total, b_coeffs_list[i])
        a_total = convolve(a_total, a_coeffs_list[i])

    # resposta em frequência (Bode)
    w, h = freqz(b_total, a_total, fs=fs, worN=8000)

    # diagrama de bode
    plt.figure(figsize=(12, 6))
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Diagrama de Bode do Equalizador Completo (12 Bandas)')
    plt.xlabel('Frequência [Hz] (Escala Logarítmica)')
    plt.ylabel('Ganho [dB]')
    plt.grid(which='both', linestyle='--', linewidth=0.5)
    plt.axhline(0, color='black', linestyle='-')
    plt.ylim(-15, 15) 
    plt.show()
    
    print('\nReproduzindo áudio original...')
    sd.play(audio_original, fs)
    sd.wait()

    print('Reproduzindo áudio equalizado...')
    sd.play(sinal_filtrado, fs)
    sd.wait()


if __name__ == "__main__":
    main()