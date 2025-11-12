# python util
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import lfilter, freqz, convolve

# util do professor
from util import peaking_eq, graf


def main():
    fs = 44100
    Q_valor = 1
    duration = 4  # segundos
    print('equalizador iniciado!')
    frequencias = np.array([20, 32, 64, 125, 250, 500, #pq esses valores de frequencia?
                            1000, 2000, 4000, 8000, 16000, 32000])
    print('preset: [0,0,8,3,10,-20,-20,-20,0,10,5,0]')
    preset = input('usar preset de equalizacao? [y/n] ')
    while preset not in ['y','n']:
        preset = input('responda entre "y" e "n" ')
    if preset == 'y':
        ganhos_db = np.array([0,0,8,3,10,-20,-20,-20,0,10,5,0])#pq esses valores de ganho?
    else:
        ganhos_db = []
        for f in frequencias:
            g = int(input(f'ganho para {f} Hz [-20 dB, +20 dB]: '))
            ganhos_db.append(g)
        ganhos_db = np.array(ganhos_db)

    print("Iniciando Equalizador Digital.")
    print("Ganhos configurados (dB):", dict(zip(frequencias, ganhos_db)))

    # Geração do sinal (sintético)
    print('criando sinal original')
    tempo = np.linspace(0., duration, int(fs * duration), endpoint=False)
    audio_original = (0.6 * np.sin(2 * np.pi * 200 * tempo) +
                      0.3 * np.sin(2 * np.pi * 800 * tempo) +
                      0.2 * np.sin(2 * np.pi * 1500 * tempo)
                    #   + 0.05*np.random.randn(len(tempo)) ruído, seria legal colocar mas teria que atenuar sempre as frequencias mais altas
                      )
    audio_original = audio_original / np.max(np.abs(audio_original)) # normalizacao

    # ---------- EQUALIZACAO ----------
    sinal_filtrado = audio_original.copy()
    b_coeffs_list = []
    a_coeffs_list = []
    print("\nAplicando 12 filtros em cascata...")
    for f0, gain_db in zip(frequencias, ganhos_db):
        b_i, a_i = peaking_eq(f0, gain_db, Q_valor, fs)
        b_coeffs_list.append(b_i)
        a_coeffs_list.append(a_i)
        sinal_filtrado = lfilter(b_i, a_i, sinal_filtrado) # aplica filtro
    sinal_filtrado = sinal_filtrado / np.max(np.abs(sinal_filtrado)) # normalizacao
    print("filtragem concluida.")
    
    # ---------- GRAFICOS ----------
    # sinal original
    plt.figure(figsize=(10, 4))
    plt.plot(tempo[:1000], audio_original[:1000])
    plt.title("Sinal Original - Amplitude x Tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # sinal filtrado
    plt.figure(figsize=(10, 4))
    plt.plot(tempo[:1000], sinal_filtrado[:1000])
    plt.title("Sinal Filtrado - Amplitude x Tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

    # ---------- DIAGRAMA DE BODE ----------
    b_total = b_coeffs_list[0]
    a_total = a_coeffs_list[0]
    for i in range(1, len(b_coeffs_list)):
        b_total = convolve(b_total, b_coeffs_list[i])
        a_total = convolve(a_total, a_coeffs_list[i])

    w, h = freqz(b_total, a_total, fs=fs, worN=8000)

    plt.figure(figsize=(12, 6))
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Diagrama de Bode do Equalizador Completo (12 Bandas)')
    plt.xlabel('Frequência [Hz] (Escala Logarítmica)')
    plt.ylabel('Ganho [dB]')
    plt.grid(which='both', linestyle='--', linewidth=0.5)
    plt.axhline(0, color='black', linestyle='-')
    plt.ylim(-15, 15)
    plt.show()

    # ---------- REPRODUÇÃO DO ÁUDIO ----------
    print('\nReproduzindo áudio original...')
    sd.play(audio_original, fs)
    sd.wait()

    print('Reproduzindo áudio equalizado...')
    sd.play(sinal_filtrado, fs)
    sd.wait()


if __name__ == "__main__":
    main()
