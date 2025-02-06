from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

# Inicializa o driver do Selenium (no exemplo, estou usando o Edge)
driver = webdriver.Edge()

try:
    # Navega até a página desejada
    driver.get("https://practice-automation.com/form-fields/")

    # Preenche o formulário e submete (substitua pelos seus próprios comandos)
    # Exemplo:
    driver.find_element(By.ID, "name-input").send_keys("Seu Nome")
    driver.find_element(By.ID, "submit-btn").click()

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