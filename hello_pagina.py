import whisper#transcrição
import sounddevice as sd#gravar
import numpy as np#manipula array
import wavio#trabalha com .wav
import time#vê o tempo
import librosa#analisa o áudio
#import speech_recognition as sr#outra ferramenta de captação/transcrição
#import pyttsx3#pra o computador 'falar'
import os #para interagir com o sistema operacional
from selenium import webdriver#pra interagir com o navegador
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

# variaveis globais
model = whisper.load_model("medium")
limiar = 0.05
amplitude = 0.015
sinal = 10


def determine_channels():
    devices = sd.query_devices()
    l = []
    for i, device in enumerate(devices):
        if 'microfone' in device['name'].lower():
            l.append(device['max_input_channels'])
            
    if 1 in l:
        x = 1
    else:
        x = 2
    print(x)
    return x

canal = determine_channels()

def calculate_snr_speech(audio_path):
    # Carregar o arquivo de áudio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Detectar silêncios para estimar o ruído
    intervals = librosa.effects.split(y, top_db=20)
    
    # Calcular a potência do sinal (somente partes faladas)
    signal_power = np.mean([np.mean(np.square(y[start:end])) for start, end in intervals])
    
    # Verificar se há intervalos de ruído detectados
    if len(intervals) > 1:
        noise_intervals = np.concatenate([y[i:j] for i, j in zip(intervals[:-1, 1], intervals[1:, 0])])
        noise_power = np.mean(np.square(noise_intervals))
    else:
        # Caso não haja intervalos de ruído suficientes, usar um valor padrão pequeno para evitar divisão por zero
        noise_power = np.mean(np.square(y[-int(sr*0.1):]))  # Usando os últimos 10% do áudio como ruído
    
    # Calcular o SNR
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calcular a amplitude RMS
    rms = np.mean(librosa.feature.rms(y=y))
    
    # Calcular a frequência fundamental usando o autocorrelação
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[pitches > 0])  # Média das frequências detectadas
    
    # Calcular o espectro de frequências
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    
    return rms, pitch, spectral_centroid



def reconhecer_comando():
    global limiar
    global canal
    global amplitude
    global sinal
    fs = 44100  # Taxa de amostragem
    seconds = 7 # Duração da gravação
            
    d = time.time()
    print("Diga algo:")

    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()  # Espera até que a gravação esteja finalizada
    #print(f'limiar: {limiar}')
    #print(np.max(np.abs(recording)))

   
    wavio.write("comando.wav", recording, fs, sampwidth=2)
    snr_value = calculate_snr_speech("comando.wav")
    rms, pitch, spectral_centroid = analyze_audio("comando.wav")
    #print(f'Relação Sinal Ruido: {snr_value:.2f},\RMS: {rms:.2f}, \tPitch: {pitch:.2f},\tCentroide Espectral: {spectral_centroid:.2f}')

    result = model.transcribe("comando.wav",fp16=False,language="pt") # configuração sem gpu 
    comando = result["text"].upper()

    
    print(comando)
    #print(f'tempo {time.time() - d}')
    
    return comando.upper()

driver = webdriver.Edge()
time.sleep(1)
driver.get("https://forms.gle/sCQpn2Z4PeQQMCJfA")


while True:
            
    comando = reconhecer_comando()
    if 'NOME' in comando and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Nome":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div/div[1]/input")

        info = (comando.split("NOME", 1)[1]).strip()
        caixa_escrita.send_keys(info)
    if 'IDADE' in comando and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Idade":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (comando.split("IDADE", 1)[1]).strip()
        caixa_escrita.send_keys(info)

    if 'PROFISSÃO' in comando and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Profissão":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (comando.split("PROFISSÃO", 1)[1]).strip()
        caixa_escrita.send_keys(info)
            
    if 'PRÓXIMA' in comando:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Próxima')]")
        botao_avanca.click()
        
    if 'VOLTAR' in comando:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Voltar')]")
        botao_avanca.click()
    if 'ENVIAR' in comando:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Enviar')]")
        botao_avanca.click()
    if 'SAIR' in comando:
        driver.quit()
        break

    '''
    if 'nome' in comando.lower():
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div/div[1]/input")

        info = (comando.split("NOME", 1)[1]).strip()
        caixa_escrita.send_keys(info)
        botao_avanca = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span")
        botao_avanca.click()

    if 'idade' in comando.lower():
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (comando.split("IDADE", 1)[1]).strip()
        caixa_escrita.send_keys(info)
        botao_avanca = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div[2]/span/span")
        botao_avanca.click()

    if 'profissão' in comando.lower():
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (comando.split("PROFISSÃO", 1)[1]).strip()
        caixa_escrita.send_keys(info)
        botao_avanca = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div[2]/span/span")
        botao_avanca.click()        
    
    if 'sair' in comando.lower():
        driver.quit()
        break
    '''