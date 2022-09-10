# pip install selenium
# pip install webdriver-manager

# libraries
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

def type_in_input(text, xpath, driver):
    set_email = driver.find_element(By.XPATH, xpath)
    set_email.send_keys(text)
def press_button(xpath, driver):
    click_element = driver.find_element(By.XPATH, xpath)
    click_element.click()


# Init
currency = "Dolar USA"  # Opciones: Real, Euro, Peso Argentino
email = "mail@gmail.com"
contrasenia = "passowrd"
telefono = "phone/username" # Both phone or username can go here

# Configuracion Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# INE
print("Obteniendo datos del INE...")
driver.get("https://www.ine.gub.uy/cotizacion-de-monedas")

cells = driver.find_elements(By.XPATH, "//td[@role='gridcell']")

currency_data = []
index = 0
loop = False
for data in cells:
    if data.text == currency:
        index = 0
        loop = True
    if loop and index < 4:
        if index == 1:
            fecha = data.text[0:10]
            currency_data.append(fecha)
        else:
            currency_data.append(data.text)
        index = index + 1
    else:
        loop = False

fecha_actual = datetime.today()
# fecha_actual = fecha_actual - timedelta(days=4) # DESCOMENTAR Y AJUSTAR EL days=x PARA FORZAR LA COTIZACION DE x DIAS ANTERIORES AL ACTUAL
fecha_actual = str(fecha_actual.day).zfill(2) + "/" + str(fecha_actual.month).zfill(2) + "/" + str(fecha_actual.year)

try:
    currency_data.index(fecha_actual)
except:
    print("Cotizacion del " + currency + " no disponible. Finalizado.")
    exit()

compra_actual = currency_data[2]
compra_anterior = currency_data[6]
venta_actual = currency_data[3]
venta_anterior = currency_data[7]
print("Valor compra anterior del " + currency + ": " + compra_anterior)
print("Valor compra actual del " + currency + ": " + compra_actual)

# calculamos la diferencia con el ultimo dia habil y vemos si subio o bajo
diff = float(compra_actual) - float(compra_anterior)
if diff < 0:
    direccion = "Bajando"
    percentage = str(round(100 - ((float(compra_actual) * 100) / float(compra_anterior)), 2)) + " %"
elif diff == 0:
    direccion = "Manteniendose igual"
    percentage = ""
else:
    direccion = "Subiendo"
    percentage = str(round(100 - ((float(compra_anterior) * 100) / float(compra_actual)), 2)) + " %"

compra_actual = str(round(float(compra_actual), 2))

# ------------------------------- START OF TWEET FORMATTING ------------------------
tweet = """El valor del """ + currency + """ a la fecha es de: 
""" + compra_actual + """ pesos uruguayos
""" + direccion + """ """ + percentage + """
Fuente: https://ine.gub.uy     
#bot #""" + currency + """ #pesos #uruguay #cotizacion #BCU #brou"""
# ------------------------------- END OF TWEET FORMATTING --------------------------

# TWITTER
driver.get("https://twitter.com/i/flow/login")
print("Entrando a Twitter...")
sleep(10)

type_in_input(email, "//input[@name='text']", driver)
press_button("//span[text()='Siguiente']/../../.. | //span[text()='Next']/../../..", driver)

print("Email ingresado")
sleep(10)

try:
    type_in_input(telefono, "//input[@name='text']", driver)
    press_button("//span[text()='Siguiente']/../.. | //span[text()='Next']/../..", driver)
    print("Telefono ingresado")
except:
    print("Ingreso de telefono no necesario")
finally:
    sleep(10)

    password_driver = driver.find_element(By.XPATH, "//input[@name='password']")
    type_in_input(contrasenia, "//input[@name='password']", password_driver)
    press_button("//span[text()='Iniciar sesión']/../../.. | //span[text()='Log in']/../../..", password_driver)
    print("Password ingresada")

sleep(10)
tweet_box = driver.find_element(By.XPATH, "//div[@class='public-DraftStyleDefault-block public-DraftStyleDefault-ltr']")
type_in_input(tweet, "//div[@class='public-DraftStyleDefault-block public-DraftStyleDefault-ltr']", tweet_box)


# click por javascript porque el botón está detrás de un elemento y .click() no 'lo ve'
tweet_button = driver.find_element(By.XPATH, "//div[@id='react-root']//span[text()='Twittear']/../../.. | //div[@id='react-root']//span[text()='Tweet']/../../..")
driver.execute_script("arguments[0].click();", tweet_button)
print("Tweet publicado")
sleep(5)

driver.close()
driver.quit()

