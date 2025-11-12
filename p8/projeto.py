import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from scipy.io.wavfile import write
from suaBibSignal import signalMeu 
from scipy.fft import fft, fftfreq # Usando scipy.fft como alternativa se 'suaBibSignal' falhar

# --- Parâmetros Globais do Projeto ---
FS = 44100            # Frequência de Amostragem (Hz)
TEMPO_SINAL = 5       # Duração em segundos (Ajuste conforme o seu áudio)
ORDEM_FILTRO = 10     # Ordem do filtro (para boa seletividade)

# Frequência Máxima do Áudio para NÃO INVADIR as bandas: 
# Largura da faixa: 3 kHz. Largura do sinal: 2 * Fm_max.
# 2 * Fm_max deve ser <= 3 kHz. -> Fm_max = 1.5 kHz.
F_BASEBAND_MAX = 1500 # CORREÇÃO CRÍTICA: 1.5 kHz

# Portadoras Centrais (Fc +/- 1.5 kHz)
FC1 = 10500  # Faixa 1: [9.0 kHz - 12.0 kHz] -> Centro em 10.5 kHz
FC2 = 13500  # Faixa 2: [12.0 kHz - 15.0 kHz] -> Centro em 13.5 kHz
FC3 = 16500  # Faixa 3: [15.0 kHz - 18.0 kHz] -> Centro em 16.5 kHz

# --- Funções Auxiliares ---

def butter_filter(data, wc, fs, order=ORDEM_FILTRO, filter_type='low'):
    """Implementa o filtro Butterworth (low/high/band). wc pode ser escalar ou [f_low, f_high]"""
    nyquist = 0.5 * fs
    
    # Se wc for uma lista (para banda), normaliza ambas as frequências
    if isinstance(wc, list) or isinstance(wc, np.ndarray):
        normal_cutoff = np.array(wc) / nyquist
    else: # Se for escalar (para low/high)
        normal_cutoff = wc / nyquist
        
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    y = lfilter(b, a, data)
    return y

def generateSin(freq, time, fs):
    """Gera o sinal da portadora (Carrier)"""
    n = int(time * fs)
    t = np.linspace(0.0, time, n, endpoint=False)
    s = np.sin(freq * t * 2 * np.pi)
    return s

def calcFFT(signal, fs):
    """Função alternativa para FFT, caso suaBibSignal.py não esteja disponível/correta."""
    N = len(signal)
    T = 1.0 / fs
    xf = fftfreq(N, T)
    yf = fft(signal)
    xf_positive = xf[:N//2]
    yf_positive = 2.0/N * np.abs(yf[:N//2])
    return xf_positive, yf_positive

def plotar_espectro(sinal, fs, titulo, cor='blue'):
    """Plota o espectro de magnitude da FFT."""
    try:
        # Tenta usar suaBibSignal
        sig = signalMeu()
        xf, yf = sig.calcFFT(sinal, fs)
    except:
        # Usa a função alternativa se falhar
        xf, yf = calcFFT(sinal, fs)
        
    plt.figure(figsize=(10, 4))
    plt.plot(xf / 1000, yf, color=cor)
    plt.title(titulo)
    plt.xlabel('Frequência (kHz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, 20)
    plt.grid(True)


# --- Função Principal do Projeto ---

def main():
    
    # --- FASE DE EMISSÃO (MODULADOR) ---
    
    print("--- FASE 1: MODULAÇÃO E SOMA (EMISSOR) ---")
    
    # 1. Carrega e prepara o áudio
    try:
        samplerate, audio_bruto = wavfile.read('__pycache__\lobsomem.wav')
    except FileNotFoundError:
        print("ERRO: O arquivo 'piratas.wav' não foi encontrado. Certifique-se de que ele está no mesmo diretório.")
        return
        
    audio_original = audio_bruto.flatten()
    
    # Normaliza e garante que o tamanho seja o definido
    num_amostras = int(TEMPO_SINAL * FS)
    audio_original = audio_original[:num_amostras]
    audio_original = audio_original / np.max(np.abs(audio_original))
    
    # 2. Pré-Filtragem (Baseband) - Garante que o áudio caiba na banda (0 a 1.5 kHz)
    audio_baseband = butter_filter(audio_original, F_BASEBAND_MAX, FS, filter_type='low')
    
    # 3. Geração das Portadoras
    C1 = generateSin(FC1, TEMPO_SINAL, FS)
    C2 = generateSin(FC2, TEMPO_SINAL, FS)
    C3 = generateSin(FC3, TEMPO_SINAL, FS)
    
    # 4. Modulação (Multiplicação) das 3 Estações
    S1_modulado = audio_baseband * C1 # Estação 1 (10.5 kHz)
    S2_modulado = audio_baseband * C2 # Estação 2 (13.5 kHz)
    S3_modulado = audio_baseband * C3 # Estação 3 (16.5 kHz)
    
    # GRÁFICO FFT DOS 3 SINAIS MODULADOS (Item de Entrega)
    plotar_espectro(S1_modulado, FS, f'FFT Estação 1 Modulada ({FC1/1000} kHz)', cor='blue')
    plotar_espectro(S2_modulado, FS, f'FFT Estação 2 Modulada ({FC2/1000} kHz)', cor='orange')
    plotar_espectro(S3_modulado, FS, f'FFT Estação 3 Modulada ({FC3/1000} kHz)', cor='green')
    plt.show() # Exibe os 3 gráficos de modulação
    
    # 5. Soma dos Sinais (Meio Físico)
    S_somado = S1_modulado + S2_modulado + S3_modulado
    
    # Normaliza o sinal somado (para evitar clipping)
    S_somado = S_somado / np.max(np.abs(S_somado))
    
    # GRÁFICO FFT DO SINAL SOMADO (Item de Entrega)
    plotar_espectro(S_somado, FS, 'FFT Sinal Resultante da SOMA (Meio Físico)', cor='red')
    plt.show()
    
    # Salva o sinal (equivalente ao seu 'audio_modulado.wav' contendo TUDO)
    write('sinal_meio_fisico.wav', FS, S_somado.astype(np.float32))

    
    # --- FASE DE RECEPÇÃO (DEMODULADOR) ---
    
    print("\n--- FASE 2: EXTRAÇÃO E DEMODULAÇÃO (RECEPTOR) ---")
    
    portadoras = [(FC1, C1), (FC2, C2), (FC3, C3)]
    bandas = [([9000, 12000], "Estação 1"), ([12000, 15000], "Estação 2"), ([15000, 18000], "Estação 3")]
    
    # Para cada estação:
    for idx, (fc, portadora) in enumerate(portadoras):
        f_banda, nome_estacao = bandas[idx]
        
        print(f"\nProcessando {nome_estacao}...")
        
        # 1. EXTRAÇÃO: Filtro Passa-Banda para isolar a estação desejada do sinal somado
        S_extraido = butter_filter(S_somado, f_banda, FS, filter_type='band')
        
        # GRÁFICO FFT DOS SINAIS EXTRAÍDOS (Item de Entrega)
        plotar_espectro(S_extraido, FS, f'FFT {nome_estacao} EXTRAÍDA (Filtro Passa-Banda)', cor='gray')
        
        # 2. DEMODULAÇÃO SÍNCRONA: Multiplica pelo sinal da portadora
        S_demodulado_multi = S_extraido * portadora
        
        # 3. FILTRAGEM FINAL: Filtro Passa-Baixa para obter o áudio (Baseband)
        # wc * 1.1 é para ter uma margem no filtro
        S_recuperado = butter_filter(S_demodulado_multi, F_BASEBAND_MAX * 1.1, FS, filter_type='low')
        
        # 4. AUMENTO DE VOLUME (Ganho)
        S_recuperado_final = S_recuperado * 4.0
        
        # GRÁFICO FFT DOS ÁUDIOS DEMODULADOS (Item de Entrega)
        plotar_espectro(S_recuperado_final, FS, f'FFT {nome_estacao} DEMODULADA (Áudio Recuperado)', cor='purple')

        # 5. EXECUTA O ÁUDIO DEMODULADO (Item de Entrega)
        print(f"Reproduzindo o áudio demodulado da {nome_estacao}...")
        sd.play(S_recuperado_final, FS)
        sd.wait()
        
    plt.show()
    print("\n--- Fim do Projeto ---")

if __name__ == "__main__":
    main()