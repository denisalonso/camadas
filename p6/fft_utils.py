# fft_utils.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# --- DEFINIÇÕES DE FREQUÊNCIA ---
ACCORDS = {
    "do_maior": {"freqs": [523.25, 659.25, 783.99], "nome": "Dó Maior"},
    "re_menor": {"freqs": [587.33, 698.46, 880.00], "nome": "Ré Menor"},
    "mi_menor": {"freqs": [659.25, 783.99, 987.77], "nome": "Mi Menor"},
    "fa_maior": {"freqs": [698.46, 880.00, 1046.50], "nome": "Fá Maior"},
    "sol_maior": {"freqs": [783.99, 987.77, 1174.66], "nome": "Sol Maior"},
    "la_menor": {"freqs": [880.00, 1046.50, 1318.51], "nome": "Lá Menor"},
    "si_menor_5b": {"freqs": [493.88, 587.33, 698.46], "nome": "Si Menor 5b"}
}


# --- FUNÇÕES DE FFT E PLOTAGEM (DO ARQUIVO BASE DO PROFESSOR) ---

def compute_fft(x, fs, window=None, nfft=None, return_complex=False):
    # ... (Copie a função compute_fft do arquivo do professor aqui)
    x = np.asarray(x, dtype=float)
    N = x.size

    # janela
    # if window is None:
    #     w = np.ones(N)
    # else:
    if window.lower() == 'hann':
        w = np.hanning(N)
    elif window.lower() == 'hamming':
        w = np.hamming(N)
    elif window.lower() == 'blackman':
        w = np.blackman(N)
    # else:
    #     raise ValueError("Janela desconhecida: use 'hann', 'hamming', 'blackman' ou None")

    xw = x * w

    # nfft
    if nfft is None:
        nfft = N
    # elif nfft < N:
    #     raise ValueError("nfft deve ser >= N (ou None)")

    # FFT unilateral com numpy.rfft
    X = np.fft.rfft(xw, n=nfft)
    freqs = np.fft.rfftfreq(nfft, d=1.0/fs)

    # normalização
    scale = np.sum(w) if np.sum(w) != 0 else N
    magnitude = np.abs(X) / scale

    # ajustar fator 2 para termos positivos
    if nfft % 2 == 0:
        magnitude[1:-1] *= 2.0
    else:
        magnitude[1:] *= 2.0

    # evitar log(0)
    eps = 1e-12
    magnitude_db = 20.0 * np.log10(magnitude + eps)

    if return_complex:
        return freqs, magnitude, magnitude_db, X
    else:
        return freqs, magnitude, magnitude_db

def plot_time_and_spectrum(t, x, fs, freqs, magnitude, magnitude_db, title_suffix=''):
    """Plota sinal no tempo e espectros (linear + dB)."""
    plt.figure(figsize=(12, 8))

    # Plot Tempo
    plt.subplot(2, 1, 1)
    plt.plot(t, x)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title(f'Sinal no domínio do tempo {title_suffix}')
    plt.grid(True)
    
    # Plot Espectro Linear
    plt.subplot(2, 1, 2)
    plt.plot(freqs, magnitude)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (linear)')
    plt.title(f'Espectro de frequência (magnitude) {title_suffix}')
    plt.xlim(0, 1500) # Foco na região de interesse
    plt.grid(True)
    
    # # Plot Espectro dB
    # plt.subplot(3, 1, 3)
    # plt.plot(freqs, magnitude_db)
    # plt.xlabel('Frequência (Hz)')
    # plt.ylabel('Magnitude (dB)')
    # plt.title(f'Espectro de frequência (dB) {title_suffix}')
    # plt.xlim(0, 1500) # Foco na região de interesse
    # plt.ylim(np.max(magnitude_db) - 60, np.max(magnitude_db) + 5) # Foco nos picos
    # plt.grid(True)
    
    plt.tight_layout()
    # Não usamos plt.show() aqui para permitir que o script principal o faça
    
def generate_sin(freq, time, fs, amplitude=1.0):
    """Gera um sinal senoide."""
    n = int(time * fs)
    t = np.linspace(0.0, time, n, endpoint=False)
    s = amplitude * np.sin(2 * np.pi * freq * t)
    return t, s

def generate_chord(freqs, fs, T=3.0, amplitude=0.9):
    """Gera um sinal de áudio (acorde) somando três senoides."""
    
    # O tempo é gerado pela primeira frequência para garantir o vetor t
    t, chord_signal = generate_sin(freqs[0], T, fs, amplitude=0.0) # sinal inicializado com zeros

    # A amplitude é dividida por 3 para evitar saturação (0.9 / 3 = 0.3 por senoide)
    amp_per_sin = amplitude / len(freqs) 
    
    for f in freqs:
        _, s_comp = generate_sin(f, T, fs, amplitude=amp_per_sin)
        chord_signal += s_comp
        
    return t, chord_signal
    
# --- FUNÇÕES DE DETECÇÃO DE PICO ---

def find_prominent_peaks(freqs, magnitude, min_peak_count=5):
    """
    Encontra os picos mais proeminentes no espectro, tentando garantir um mínimo.
    """
    # 1. Encontrar picos, ajustando a proeminência dinamicamente
    peaks_indices = np.array([])
    # Começa com uma proeminência relativa ao maior pico (assumindo que o maior pico é 1, se normalizado)
    # ou usando um valor absoluto que elimine ruído de fundo (ex: 10% do pico máximo)
    max_mag = np.max(magnitude) if len(magnitude) > 0 else 0
    
    current_prominence = 0.1 * max_mag # 10% da amplitude máxima
    
    # Busca com proeminência
    while len(peaks_indices) < min_peak_count and current_prominence > 0.001 * max_mag:
        peaks_indices, properties = find_peaks(magnitude, prominence=current_prominence, height=0.01 * max_mag) 
        current_prominence *= 0.8 # Reduz a proeminência
        
    # Se ainda houver poucos, faz uma busca mais simples por altura mínima
    if len(peaks_indices) < min_peak_count:
        peaks_indices, properties = find_peaks(magnitude, height=0.05 * max_mag) # 5% da amplitude máxima
        
    # 2. Filtrar picos encontrados para a região de interesse do acorde (450 Hz a 1400 Hz)
    valid_indices = (freqs[peaks_indices] > 450) & (freqs[peaks_indices] < 1400)
    peaks_indices = peaks_indices[valid_indices]

    # 3. Obter a frequência e magnitude dos picos filtrados
    peak_freqs = freqs[peaks_indices]
    peak_mags = magnitude[peaks_indices]

    # 4. Ordenar os picos pela magnitude (do maior para o menor)
    sorted_indices = np.argsort(peak_mags)[::-1]
    
    return peak_freqs[sorted_indices], peak_mags[sorted_indices]


def map_peaks_to_chord(peak_freqs, ACCORDS, tolerance=5.0):
    """
    Compara as frequências dos picos com as frequências dos acordes conhecidos.
    """
    
    # 1. Usar as 3 frequências mais proeminentes (reais)
    top_3_peaks = peak_freqs[:3]
    
    best_match_name = "Acorde Não Identificado"
    best_match_score = 0
    
    # 2. Comparar com cada acorde na lista
    for key, data in ACCORDS.items():
        expected_freqs = data['freqs']
        match_count = 0
        
        # Para cada frequência fundamental esperada no acorde
        for expected_f in expected_freqs:
            # Verifica se algum dos picos encontrados está "próximo" (dentro da tolerância)
            if any(abs(p - expected_f) <= tolerance for p in top_3_peaks):
                match_count += 1
        
        # Atualiza o melhor score
        if match_count > best_match_score:
            best_match_score = match_count
            best_match_name = data['nome']
            
    # Se o melhor score for menor que 3, a identificação pode não ser confiável.
    if best_match_score < 3:
        return "Acorde Não Identificado", best_match_score
    
    return best_match_name, best_match_score