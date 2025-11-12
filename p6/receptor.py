# receptor.py
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from fft_utils import ACCORDS, compute_fft, find_prominent_peaks, map_peaks_to_chord, plot_time_and_spectrum

# --- CONFIGURAÇÃO ---
FS = 44100      # Frequência de amostragem
DURATION = 3.0  # Duração da gravação em segundos (deve ser maior que a emissão)
DELAY = 0      # Tempo para iniciar a gravação após o início do script

# --- MAIN RECEPTOR ---
def receiver_main():
    print("--- LADO RECEPTOR: IDENTIFICADOR DE ACORDES ---")
    
    sd.default.samplerate = FS 
    sd.default.channels = 1
    num_amostras = int(FS * DURATION)
    
    print(f"A captação começará em {DELAY} segundos. Prepare a emissão.")
    sd.sleep(int(DELAY * 1000))

    # Gravação do sinal
    print(f"Gravação iniciada por {DURATION} segundos em {FS} Hz...")
    

    
    recorded_signal = sd.rec(num_amostras, FS, channels=1, dtype='float64')
    sd.wait()
    print("Gravação finalizada.")
    
    # Prepara o sinal e o vetor tempo
    x_rec = recorded_signal.flatten()
    T_real = len(x_rec) / FS
    t_rec = np.linspace(0, T_real, len(x_rec), endpoint=False)

    # 1. Calcular a FFT (usando janela 'hann' para melhor precisão)
    freqs_fft, magnitude, magnitude_db = compute_fft(x_rec, FS, window='hann') 
    
    # 2. Identificar os picos
    # O min_peak_count é 5, mas a lógica de mapeamento só usará os 3 mais proeminentes.
    peak_freqs, peak_mags = find_prominent_peaks(freqs_fft, magnitude, min_peak_count=5)
    
    # 3. Mapear para o acorde
    acorde_identificado, score = map_peaks_to_chord(peak_freqs, ACCORDS, tolerance=2.0)

    # 4. Plotar os resultados
    plot_time_and_spectrum(t_rec, x_rec, FS, freqs_fft, magnitude, magnitude_db, 
                           title_suffix='Recebido e Analisado')
    
    print(f"\nFrequências dos picos principais encontrados (Hz):")
    # Imprime as 5 frequências mais fortes
    for i, freq in enumerate(peak_freqs[:5]):
        print(f"  {i+1}. {freq:.2f} Hz (Magnitude: {peak_mags[i]:.4f})")
    
    print(f"\n--- RESULTADO DA DECODIFICAÇÃO ---")
    print(f"Acorde Identificado: {acorde_identificado}")
    print(f"Picos Fundamentais Combinados (Score): {score}/3")
    
    plt.show()

if __name__ == "__main__":
    receiver_main()