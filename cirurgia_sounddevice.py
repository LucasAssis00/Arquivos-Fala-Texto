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
    print(f'limiar: {limiar}')
    print(np.max(np.abs(recording)))

   
    wavio.write("comando.wav", recording, fs, sampwidth=2)
    snr_value = calculate_snr_speech("comando.wav")
    rms, pitch, spectral_centroid = analyze_audio("comando.wav")
    print(f'Relação Sinal Ruido: {snr_value:.2f},\RMS: {rms:.2f}, \tPitch: {pitch:.2f},\tCentroide Espectral: {spectral_centroid:.2f}')

    
    '''
    if snr_value > sinal and pitch > 100 and rms >= amplitude and spectral_centroid > 1500:
           
            
            result = model.transcribe("comando.wav",fp16=False,language="pt") # configuração sem gpu 
            comando = result["text"]
            with open('registro-fala.txt', 'a',encoding='utf-8') as arquivo: 
                arquivo.write(comando + '\n')
    else:
            comando = ' '
    
    '''
    result = model.transcribe("comando.wav",fp16=False,language="pt") # configuração sem gpu 
    comando = result["text"]

    
    print(comando)
    print(f'tempo {time.time() - d}')
    
    return comando

def atualizar_dados_com_fala():
    while True:
               
        comando = reconhecer_comando()

        if 'sair' in comando.lower():
            
            break
        


def habilitar_calibra():
    global limiar
    global canal
    global amplitude
    global sinal
    fs = 44100  # Taxa de amostragem
    seconds = 7  # Duração da gravação
    print('Fale: calibrando o microfone')
    recording2 = sd.rec(int(seconds * fs), samplerate=fs, channels=canal)
    sd.wait()
    print('fim da calibralção')  
    limiar = np.max(np.abs(recording2))
    wavio.write("comando2.wav", recording2, fs, sampwidth=2)
    rms2, pitch, spectral_centroid = analyze_audio("comando2.wav")
    sinal = calculate_snr_speech("comando2.wav")
    print(f'sinal: {sinal:.2f}')
    print(f'rms2: {rms2:.2f}')
    if rms2 > 0.02:
        amplitude = 0.02
    else:
        amplitude = rms2
    

habilitar_calibra()

################
start_time = time.time()

#atualizar_dados_com_fala()
html_file_path = os.path.abspath("webinicial.html")

driver = webdriver.Edge()
driver.get(f"file://{html_file_path}")
#time.sleep(3)

interrupcao = False

while True:
    command = reconhecer_comando().upper()  # string
    if "INTERROMPER GRAVAÇÃO" in command:
        #if interrupcao == False:
        #    speak("Sistema em modo de espera")
        print('Sistema em modo de espera.')
        interrupcao = True
    elif "INICIAR GRAVAÇÃO" in command or "CONTINUAR GRAVAÇÃO" in command:
        #if interrupcao == True:
        #    speak("Sistema identificando fala")
        print('Sistema identificando fala.')
        interrupcao = False
    
    if interrupcao == False:

        '''
        if "NAVEGADOR" in command:
            print(command)
            speak("Abrindo o navegador")
            driver = webdriver.Edge()
            #driver = webdriver.Firefox()
        '''

        if "NOVA ABA" in command:
            #speak("nova aba")
            driver.switch_to.new_window('tab')
            janelas_ativas = driver.window_handles
        if "ABA INICIAL" in command:
            #speak("nova aba")
            driver.switch_to.window(driver.window_handles[0])
        if "MUDAR" in command and "ABA" in command:
            #speak("mudando de aba")
            #driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + Keys.TAB)
            #driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
            janela_atual = driver.current_window_handle
            indice_atual = janelas_ativas.index(janela_atual)
            driver.switch_to.window(janelas_ativas[indice_atual - 1])
        if "NOVA JANELA" in command:
            #speak("nova janela")
            driver.switch_to.new_window('window')
            janelas_ativas = driver.window_handles
        '''
        if "GOOGLE" in command:
            speak("google")
            driver.get("http://www.google.com")
        if "YOUTUBE" in command:
            driver.get("https://www.youtube.com")
            janelas_ativas = driver.window_handles
        '''
        if "FORMULÁRIO 1" in command:
            #speak("abrindo Demonstração Preenchimento Web")
            driver.switch_to.new_window('tab')
            #driver = webdriver.Edge()
            time.sleep(1)
            driver.get("http://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM")
            janelas_ativas = driver.window_handles
            print(f'***{driver.current_url}')
        if "FORMULÁRIO 2" in command:
            #speak("abrindo Demonstração Preenchimento Web")
            driver.switch_to.new_window('tab')
            #driver = webdriver.Edge()
            time.sleep(1)
            driver.get("https://practice-automation.com/form-fields/")
            janelas_ativas = driver.window_handles
            print(f'***{driver.current_url}')
        if "FORMULÁRIO 3" in command:
            #speak("abrindo Demonstração Preenchimento Web")
            driver.switch_to.new_window('tab')
            #driver = webdriver.Edge()
            time.sleep(1)
            driver.get("https://docs.google.com/forms/d/e/1FAIpQLSc1JetQtx0i1VsrSdUNAl_wo319_bnxZOW7nJxMNWM49rryjw/viewform")
            janelas_ativas = driver.window_handles

        if "https://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM/viewform?edit_requested=true" in driver.current_url:
            if "NOME" in command:
                search_box = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
                #cor_desejada = "#FFD700"  # Amarelo
                #driver.execute_script(f"arguments[0].style.backgroundColor = '{cor_desejada}';", search_box)
                #driver.execute_script("arguments[0].style.color = 'red';", search_box)
                #driver.execute_script("arguments[0].scrollIntoView()", search_box)
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    nome_user = (command.split("NOME", 1)[1]).strip()
                    search_box.send_keys(nome_user)
            if "GÊNERO" in command:
                search_box = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    genero_user = (command.split("GÊNERO", 1)[1]).strip()
                    search_box.send_keys(genero_user)
            if "DATA DO EXAME" in command:
                search_box = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    date_user = (command.split("DATA DO EXAME", 1)[1]).strip()

                    search_box.send_keys(date_user)
            if "PROFISSIONAL RESPONSÁVEL" in command:
                search_box = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    worker = (command.split("PROFISSIONAL RESPONSÁVEL", 1)[1]).strip()
                    search_box.send_keys(worker)
            if "DESCRIÇÃO" in command:
                search_box = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div[2]/textarea')
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    description = (command.split("DESCRIÇÃO", 1)[1]).strip()
                    search_box.send_keys(description)
            if "ENVIAR" in command:

                botao_avanca = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
                driver.execute_script("arguments[0].scrollIntoView()", botao_avanca)

                botao_avanca.click()
                #speak("As informações foram registradas.")
                '''
                try:
                    alert = Alert(driver)
                    # To accept the alert (click OK or Yes)
                    alert.accept()
                except:
                    print("No alert found.")
                #time.sleep(0.5)
                '''
                driver.execute_script("window.scrollTo(0, 0);")

        if "https://practice-automation.com/form-fields/" in driver.current_url:
            if "NOME" in command:
                search_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[1]/input')
                cor_desejada = "#FFD700"  # Amarelo
                driver.execute_script(f"arguments[0].style.backgroundColor = '{cor_desejada}';", search_box)
                driver.execute_script("arguments[0].style.color = 'red';", search_box)
                driver.execute_script("arguments[0].scrollIntoView()", search_box)
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    nome_user = (command.split("NOME", 1)[1]).strip()
                    search_box.send_keys(nome_user)
            if "SENHA" in command:
                search_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[2]/input')
                driver.execute_script(f"arguments[0].style.backgroundColor = '{cor_desejada}'; arguments[0].style.color = 'red';", search_box)
                driver.execute_script("arguments[0].scrollIntoView()", search_box)
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    senha_user = (command.split("SENHA", 1)[1]).strip()
                    senha_user = senha_user.replace(" ", "")
                    search_box.send_keys(senha_user)
            if "BEBIDA FAVORITA" in command:
                if "LIMPAR" in command:
                    for i in range(1,6):
                        botao_bebida = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[{i}]")
                        if botao_bebida.is_selected():
                            botao_bebida.click()
                else:
                    if 'ÁGUA' in command:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[1]")
                        #driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
                        #botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[4]")
                        botao_bebida.click()
                    if 'LEITE' in command:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[2]")
                        #driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
                        #botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[5]")
                        botao_bebida.click()
                    if 'CAFÉ' in command:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[3]")
                        #driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
                        #botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[6]")
                        botao_bebida.click()
                    if 'VINHO' in command:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[4]")
                        #driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
                        #botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[7]")
                        botao_bebida.click()
                    if 'CHÁ' in command:
                        botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[5]")
                        #driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
                        #botao_bebida = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[8]")
                        botao_bebida.click()
                    driver.execute_script("arguments[0].scrollIntoView()", botao_bebida)
            if "COR FAVORITA" in command:
                #pelo menos por hora não sei como/ tá dando pra limpar esse campo. Depois que seleciona um aí fudeu
                if 'VERMELHO' in command:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[6]")
                    driver.execute_script("arguments[0].scrollIntoView()", botao_cor)
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[10]")
                    botao_cor.click()
                if 'AZUL' in command:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[7]")
                    driver.execute_script("arguments[0].scrollIntoView()", botao_cor)
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[11]")
                    botao_cor.click()
                if 'AMARELO' in command:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[8]")
                    driver.execute_script("arguments[0].scrollIntoView()", botao_cor)
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[12]")
                    botao_cor.click()
                if 'VERDE' in command:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[9]")
                    driver.execute_script("arguments[0].scrollIntoView()", botao_cor)
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[13]")
                    botao_cor.click()
                if 'ROSA' in command:
                    botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[10]")
                    driver.execute_script("arguments[0].scrollIntoView()", botao_cor)
                    #botao_cor = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div/main/div/article/div/form/label[14]")
                    botao_cor.click()
            if "GOSTO" in command:
                botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select')
                driver.execute_script("arguments[0].scrollIntoView()", botao_caixa)
                botao_caixa.click()
                if "NÃO SEI" in command:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[4]')
                elif "NÃO GOSTO" in command:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[3]')
                else:
                    botao_caixa = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/select/option[2]')
                botao_caixa.click()
            if "E-MAIL" in command:
                email_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/input[11]')
                driver.execute_script("arguments[0].scrollIntoView()", email_box)
                if "LIMPAR" in command:
                    email_box.clear()
                else:
                    email_user = (command.split("E-MAIL", 1)[1]).strip()
                    email_user = email_user.replace("ARROBA", "@")
                    email_user = email_user.replace(" ", "")
                    email_user = email_user.lower()
                    email_box.send_keys(email_user)
            if "MENSAGEM" in command:
                message_box = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/textarea')
                driver.execute_script("arguments[0].scrollIntoView()", message_box)
                #time.sleep(2)
                if "LIMPAR" in command:
                    search_box.clear()
                else:
                    input_message = (command.split("MENSAGEM", 1)[1]).strip()
                    message_box.send_keys(input_message)
            if "ENVIAR" in command:
                botao_avanca = driver.find_element("xpath", '/html/body/div[1]/div[2]/div/div/main/div/article/div/form/button')
                time.sleep(0.5)
                driver.execute_script("arguments[0].scrollIntoView()", botao_avanca)
                time.sleep(0.5)
                #print("funcionoooou")
                #time.sleep(0.2)
                #driver.implicitly_wait(0.2)
                botao_avanca.click()
                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    #print(f"Alert text: {alert.text}")
                    alert.accept()  # Aceita o alerta
                except NoAlertPresentException:
                    pass
                    #print("No alert present")
                time.sleep(0.5)
                #thread = threading.Timer(0.2, delayed_click, [botao_avanca])
                #thread.start()

        if "https://docs.google.com/forms/d/e/1FAIpQLSc1JetQtx0i1VsrSdUNAl_wo319_bnxZOW7nJxMNWM49rryjw/viewform" in driver.current_url:
            match command:
                case cmd if "PRONTUÁRIO" in cmd:
                    senha_user = (command.split("PRONTUÁRIO", 1)[1]).strip()
                    search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                    if "LIMPAR" in command:
                        search_box.clear()
                    else:
                        search_box.send_keys(senha_user)
                case cmd if "SALA" in cmd:
                    senha_user = (command.split("SALA", 1)[1]).strip()
                    search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                    if "LIMPAR" in command:
                        search_box.clear()
                    else:
                        search_box.send_keys(senha_user)
                case cmd if (("SÍTIO" in cmd and "DEMARCADO" in cmd) or "LATERALIDADE" in cmd):
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[3]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    elif 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                        #VER LÓGICA PARA 'NÃO SE APLICA' 
                case cmd if "SEGURANÇA ANESTÉSICA" in cmd:
                    if 'MONTAGEM DA SO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if 'MATERIAL ANESTÉSICO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if not 'MONTAGEM DA SO' in cmd and not 'MATERIAL ANESTÉSICO' in cmd:
                        #botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[7]/div/div/div[2]/div[1]/div[3]/div/label/div/div[2]/div/span")
                        botao_cor.click()
                        texto_excecao = (command.split("ANESTÉSICA", 1)[1]).strip()
                        search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[7]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
                        search_box.send_keys(texto_excecao)
                case cmd if "VIA AÉREA" in cmd:#podemos utilizar aqui fácil ou desobstruida?; como fazer para "NÂO ACESSIVEL"?
                    if 'FÁCIL' in cmd or 'DESOBSTRUÍDA' in cmd or 'ACESSÍVEL' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        #botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    #if 'NÃO' in cmd:
                    #    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                    #    botao_cor.click()
                    #else:
                    #    botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                    #    botao_cor.click()
                case cmd if "PERDA SANGUÍNEA" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if 'RESERVA DE SANGUE DISPONÍVEL' in cmd or 'RESERVA DISPONÍVEL' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[9]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                case cmd if "ACESSO VENOSO" in cmd:
                    if 'NÃO' in cmd or 'INADEQUADO' in cmd :
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if 'PROVIDENCIADO NA SO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[10]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                case cmd if "REAÇÃO ALÉRGICA" in cmd:
                    if 'NÃO' in cmd or 'SEM' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                        texto_excecao = (command.split("ALÉRGICA", 1)[1]).strip()
                        search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[11]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/div[1]/span[1]/div[1]/div[1]/div[1]/input[1]')
                        search_box.send_keys(texto_excecao)
                #2. ANTES DA INCISÃO CIRÚRGICA--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                case cmd if "APRESENTAÇÃO ORAL" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[13]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[13]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "CONFIRMAÇÃO VERBAL" in cmd or "DADOS DO PACIENTE" in cmd:#precisa estar junto lá em cima, devido a muito provavelmente falar a palavra 'paciente aqui
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[14]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "ANTIBIÓTICO PROFILÁTICO" in cmd:
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[3]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    elif 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[15]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                #case cmd if "MOMENTOS CRÍTICOS" in cmd:
                case cmd if "REVISÃO DO CIRURGIÃO" in cmd or "MOMENTOS CRÍTICOS" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[16]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[16]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "REVISÃO DO ANESTESISTA" in cmd or (("PREOCUPAÇÃO" in cmd or "PREOCUPAÇÕES" in cmd and "PACIENTE" in cmd)):
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[17]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[17]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                #case cmd if "PREOCUPAÇÃO EM RELAÇÃO AO PACIENTE" in cmd:
                case cmd if "ESTERILIZAÇÃO DO MATERIAL" in cmd:#case cmd if "ESTERILIZAÇÃO DO MATERIAL CIRÚRGICO" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[18]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[18]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "PLACA DE ELETROCAUTÉRIO" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[19]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[19]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "DISPONÍVEIS E FUNCIONANTES" in cmd or "EQUIPAMENTOS DISPONÍVEIS" in cmd or "EQUIPAMENTOS FUNCIONANTES" in cmd:
                    if 'NÃO' in cmd:#^VER SE ISSO AQUI TEM UMA FORMA MAIS EFICIENTE DE ESCREVER
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[20]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[20]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "INSUMOS E INSTRUMENTAIS" in cmd:
                    if 'NÃO' in cmd or 'INDISPONÍVEIS' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[21]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[21]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "PROCEDIMENTO" in cmd and "REALIZADO" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[23]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[2]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[23]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[1]/label[1]/div[1]/div[1]/div[1]/div[3]/div[1]")
                        botao_cor.click()
                case cmd if "CONTAGEM DE COMPRESSAS" in cmd:
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor3.click()
                    elif 'NÃO' in cmd:
                        botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor3.click()
                    else:
                        botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor3.click()
                    #if not 'NÃO' in cmd and not 'HOUVE' in cmd:
                    if 'ENTREGUES' in cmd:
                        botao_cor3 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[24]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor3.click()
                        texto_excecao3 = (command.split("ENTREGUES", 1)[1]).strip()
                        search_box3 = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[2]/div[24]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input')
                        search_box3.send_keys(texto_excecao3)
                case cmd if "CONTAGEM DE INSTRUMENTOS" in cmd:
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor1.click()
                    elif 'NÃO' in cmd:
                        botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor1.click()
                    else:
                        botao_cor1 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor1.click()
                    if 'ENTREGUES' in cmd:
                        botao_cor1 = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[25]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input")
                        botao_cor1.click()
                        texto_excecao1 = (command.split("ENTREGUES", 1)[1]).strip()
                        search_box1 = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[25]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
                        search_box1.send_keys(texto_excecao1)
                case cmd if "CONTAGEM DE AGULHAS" in cmd:
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor2.click()
                    elif 'NÃO' in cmd:
                        botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor2.click()
                    else:
                        botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor2.click()
                    if 'ENTREGUES' in cmd:
                        botao_cor2 = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[26]/div[1]/div[1]/div[2]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
                        botao_cor2.click()
                        texto_excecao2 = (command.split("ENTREGUES", 1)[1]).strip()
                        search_box2 = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[2]/div[26]/div/div/div[2]/div[1]/div[4]/div/div/div/div/div[1]/input')
                        search_box2.send_keys(texto_excecao2)
                case cmd if "AMOSTRA CIRÚRGICA" in cmd or "IDENTIFICADA ADEQUADAMENTE" in cmd:
                    if 'NÃO SE APLICA' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    elif 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if 'REQUISIÇÃO COMPLETA' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[4]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                        #texto_excecao = (command.split("COMPRESSAS", 1)[1]).strip()
                        #search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[27]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/div[1]/div[4]/div[1]/span[1]/div[1]/div[1]/div[1]/input[1]')
                        #search_box.send_keys(texto_excecao)
                case cmd if "PROBLEMA COM EQUIPAMENTOS" in cmd or "PROBLEMAS COM EQUIPAMENTOS" in cmd:
                    if 'NÃO' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    else:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                    if 'COMUNICADO À ENFERMEIRA' in cmd:
                        botao_cor = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[28]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                        botao_cor.click()
                case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "CIRURGIÃO" in cmd):
                    senha_user = (command.split("CIRURGIÃO", 1)[1]).strip()
                    search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[30]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                    if "LIMPAR" in command:
                        search_box.clear()
                    else:                    
                        search_box.send_keys(senha_user)
                case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "ANESTESISTA" in cmd):
                    senha_user = (command.split("ANESTESISTA", 1)[1]).strip()
                    search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[31]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                    if "LIMPAR" in command:
                        search_box.clear()
                    else:
                        search_box.send_keys(senha_user)
                case cmd if (("RECOMENDAÇÕES" in cmd or "RECOMENDAÇÃO" in cmd) and "ENFERMAGEM" in cmd):
                    senha_user = (command.split("ENFERMAGEM", 1)[1]).strip()
                    search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[32]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                    if "LIMPAR" in command:
                        search_box.clear()
                    else:
                        search_box.send_keys(senha_user)
                case cmd if "PACIENTE" in cmd:# and ("CONFIRMOU" in cmd or "CONFIRMADO" in cmd):
                    #if "CONFIRMOU" in cmd:
                    if "CONFIRMOU" in cmd or "CONFIRMADO" in cmd:
                        if 'IDENTIDADE' in cmd:
                            #botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[1]/div[2]")
                            botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]/div[1]/div[2]/div[1]/span[1]")
                            botao_bebida.click()
                        if 'PROCEDIMENTO' in cmd:
                            botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/div[1]/div[2]/div[1]/span[1]")
                            botao_bebida.click()
                        if 'SÍTIO CIRÚRGICO' in cmd:
                            botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[3]/label[1]/div[1]/div[2]/div[1]/span[1]")
                            botao_bebida.click()
                        if 'CONSENTIMENTO' in cmd:
                            botao_bebida = driver.find_element("xpath", "/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/div[1]/div[4]/label[1]/div[1]/div[2]/div[1]/span[1]")
                            botao_bebida.click()
                    elif "NOME" in cmd:
                        nome_user = (command.split("PACIENTE", 1)[1]).strip()
                        search_box = driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/form[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/input[1]')
                        if "LIMPAR" in command:
                            search_box.clear()
                        else:                        
                            search_box.send_keys(nome_user)
                #case cmd if (("SÍTIO" in cmd and "DEMARCADO" in cmd) or "LATERALIDADE" in cmd):
                case cmd if "ENVIAR" in cmd:
                        botao_avanca = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
                        botao_avanca.click()
                case cmd if "SAIR" in cmd:
                        #botao_avanca = driver.find_element("xpath", '/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
                        #botao_avanca.click()
                        try:
                            driver.quit()
                        except:
                            pass
                        break

        if "SAIR" in command:
            driver.quit()
        if "ENCERRAR" in command:
            try:
                driver.quit()
            except:
                pass
            #speak("Até a próxima.")
            break
    else:
        pass
