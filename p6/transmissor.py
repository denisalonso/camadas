# emissor.py
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from fft_utils import ACCORDS, compute_fft, generate_chord, plot_time_and_spectrum

# --- CONFIGURAÇÃO ---
FS = 44100 # Frequência de amostragem
DURATION = 8.0 # Duração da emissão em segundos

# --- MAIN EMISSOR ---
def emitter_main():
    print("--- LADO EMISSOR: GERADOR DE ACORDES ---")
    print("Acordes disponíveis:")
    valid_keys = list(ACCORDS.keys())
    
    for i, key in enumerate(valid_keys):
        print(f"[{i+1}] {ACCORDS[key]['nome']} ({key})")
        
    choice = input("\nDigite o nome ou número do acorde a ser tocado: ").strip().lower()

    chord_name = None
    if choice.isdigit():
        try:
            index = int(choice) - 1
            if 0 <= index < len(valid_keys):
                chord_name = valid_keys[index]
        except ValueError:
            pass # Continua para a verificação por nome

    if chord_name is None and choice in valid_keys:
        chord_name = choice
        
    if chord_name is None:
        print("Opção inválida.")
        return

    freqs = ACCORDS[chord_name]['freqs']
    nome_acorde = ACCORDS[chord_name]['nome']

    # 1. Gerar o sinal
    t, x = generate_chord(freqs, FS, T=DURATION)
    
    # 2. Plotar o sinal no tempo e no espectro
    freqs_fft, magnitude, magnitude_db = compute_fft(x, FS, window='hann')
    plot_time_and_spectrum(t, x, FS, freqs_fft, magnitude, magnitude_db, 
                           title_suffix=f'Gerado: {nome_acorde}')

    # 3. Emitir o áudio
    print(f"\nReproduzindo o acorde {nome_acorde} em {FS} Hz ({DURATION}s)...")
    
    # COMENTÁRIO PARA ADAPTAÇÃO AO ANALOG DISCOVERY (EMISSOR/AWG)
    #
    # Se for usar o Analog Discovery:
    # 1. Inicialize a biblioteca DWF: hdwf = dwf.Dwf(...); dwf.FDwfDeviceOpen(...)
    # 2. Configure o AWG: dwf.FDwfAnalogOutNodeEnable(hdwf, channel, 1)
    # 3. Defina o sinal: dwf.FDwfAnalogOutNodeNodeSet(hdwf, channel, dwf.DwfAnalogOutNodeCarrier, np.array(x))
    # 4. Execute: dwf.FDwfAnalogOutConfigure(hdwf, channel, 1)
    # 5. Use time.sleep(DURATION) em vez de sd.wait()
    
    sd.play(x, FS)
    sd.wait() # Aguarda o fim da reprodução
    print("Reprodução finalizada.")
    plt.show()

if __name__ == "__main__":
    emitter_main()