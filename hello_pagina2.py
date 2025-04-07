import speech_recognition as sr


import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time



# Inicializa o reconhecedor de voz
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta para o ruído ambiente
        print("Diga algo...")
        #audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)  # Limita o tempo de escuta
        audio = recognizer.listen(source, phrase_time_limit=7)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
        try:
            command = recognizer.recognize_google(audio, language='pt-BR')
            if interrupcao == False:
                print(f"Você disse: {command}")
            return command
        except sr.UnknownValueError:
            if interrupcao == False:
                print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao se comunicar com o serviço de reconhecimento de voz.")
            return ""

interrupcao = False

start_time = time.time()

driver = webdriver.Edge()
driver.get("https://forms.gle/sCQpn2Z4PeQQMCJfA")

while True:
    command = listen().upper()  # string
    print('')
    if 'NOME' in command and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Nome":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div/div[1]/input")

        info = (command.split("NOME", 1)[1]).strip()
        caixa_escrita.send_keys(info)
    if 'IDADE' in command and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Idade":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (command.split("IDADE", 1)[1]).strip()
        caixa_escrita.send_keys(info)

    if 'PROFISSÃO' in command and driver.find_element(By.XPATH, "//span[@class='M7eMe']").text == "Profissão":
        caixa_escrita = driver.find_element("xpath", "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")
        info = (command.split("PROFISSÃO", 1)[1]).strip()
        caixa_escrita.send_keys(info)
            
    if 'PRÓXIMA' in command:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Próxima')]")
        botao_avanca.click()
        
    if 'VOLTAR' in command:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Voltar')]")
        botao_avanca.click()
    if 'ENVIAR' in command:
        botao_avanca = driver.find_element("xpath", "//span[contains(text(),'Enviar')]")
        botao_avanca.click()
    if 'SAIR' in command:
        driver.quit()
        break