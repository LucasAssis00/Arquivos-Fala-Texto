from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
import time

# Inicializa o driver do Selenium (no exemplo, estou usando o Edge)
driver = webdriver.Firefox()

try:
    # Navega até a página desejada
    driver.get("https://practice-automation.com/form-fields/")
    time.sleep(3)

    # Preenche o formulário e submete (substitua pelos seus próprios comandos)
    # Exemplo:
    #driver.find_element(By.ID, "name-input").send_keys("Seu Nome")
    driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/main[1]/div[1]/article[1]/div[1]/form[1]/label[1]/input[1]').send_keys("Seu Nome")

    time.sleep(5)
    #driver.find_element(By.ID, "submit-btn").click()
    driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/main[1]/div[1]/article[1]/div[1]/form[1]/button[1]').click()
    time.sleep(1)

    # Aguarda o alerta aparecer
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert text: {alert.text}")
        alert.accept()  # Aceita o alerta
    except NoAlertPresentException:
        print("No alert present")

    # Continua com a execução do código
    if "https://practice-automation.com/form-fields/" in driver.current_url:
        print("Estamos na página correta!")
    else:
        print("Não estamos na página correta.")

except UnexpectedAlertPresentException as e:
    print(f"Erro: {e}")
finally:
    # Fecha o navegador
    driver.quit()