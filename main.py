import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code

# Page Object: Encapsula todos los locators y acciones de la página de Urban Routes.
# El test nunca interactúa con Selenium directamente, solo llama a estos métodos.

class UrbanRoutesPage:
    # --- Locators: paso 1, ruta ---
    from_field = (By.ID, 'from') # Campo de dirección de origen
    to_field = (By.ID, 'to') # Campo de dirección de destino

    # --- Locators: paso 2, reserva y confirmación de teléfono ---
    button_reservar = (By.XPATH, './/button[text()="Pedir un taxi"]') # Botón para iniciar la reserva
    confort = (By.XPATH, './/div[text()="Comfort"]') # Opción de tarifa "Comfort"
    phone_button = (By.XPATH, './/div[text()="Número de teléfono"]') # Abre el campo de teléfono
    phone_field = (By.ID, 'phone') # Input real del número de teléfono
    button_sig = (By.XPATH, './/button[text()="Siguiente"]')  # Botón "Siguiente" tras ingresar el teléfono
    code_SMS_field = (By.ID, 'code') # Input del código SMS recibido
    code_confirm_button = (By.XPATH, './/button[text()="Confirmar"]') # Confirma el código SMS

    # --- Locators: paso 3, método de pago ---
    button_payment_method = (By.CLASS_NAME, 'pp-text') # Abre el selector de método de pago
    pay_card = (By.XPATH, './/div[text()="Agregar tarjeta"]') # Opción "Agregar tarjeta"
    card_number = (By.ID, 'number') # Input del número de tarjeta
    card_code = (By.XPATH, './/div[@class="card-code-input"]/input') # Input del código de seguridad (CVV)
    button_add_card = (By.XPATH, './/button[text()="Agregar"]') # Confirma el alta de la tarjeta
    button_close_pay = (By.XPATH, './/div[@class="payment-picker open"]//div[@class="section active"]//button[@class="close-button section-close"]') # Cierra el panel de pago; acotado al panel "open"/"active" para evitar ambigüedad con otros paneles

    # --- Locators: paso 4, extras del viaje ---
    comment_field =  (By.ID, 'comment') # Campo de comentario para el chofer
    switch_man_pan = (By.XPATH, ".//div[text()='Manta y pañuelos']/following-sibling::div//span[contains(@class, 'slider')]") # Switch visual de "Manta y pañuelos" (el input real de checkbox no se usa aquí, se hace clic en el slider)
    plus_helado = (By.XPATH, './/div[text()="Helado"]/following-sibling::div//div[@class="counter-plus"]') # Botón "+" del contador de Helado
    main_button = (By.CLASS_NAME, 'smart-button') # Botón principal que confirma el pedido

    # --- Locators: paso 5, información del conductor asignado (comprobación opcional) ---
    driver_name = (By.XPATH, './/div[@class="order-btn-group"]/div[not(@class)]') # Nombre del conductor (div sin clase)
    order_plate = (By.XPATH, '//div[@class="order-number"]/div[@class="number"]') # Placa del auto asignado
    order_car_image = (By.XPATH, '//div[@class="order-number"]/img') # Imagen del modelo de auto asignado




    def __init__(self, driver):
        # Guarda el driver recibido y crea un wait "por defecto" de 10s, reutilizado
        # en la mayoría de las interacciones que dependen de una carga/transición corta.
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # ----- Paso 1: ruta -----
    def set_from(self, from_address):
        # Escribe la dirección de origen en el campo correspondiente
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        # Escribe la dirección de destino en el campo correspondiente
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        # Lee el valor actual del campo de origen (para comprobar que se escribió bien)
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        # Lee el valor actual del campo de destino (para comprobar que se escribió bien)
        return self.driver.find_element(*self.to_field).get_property('value')

    def set_route(self,address_from, address_to):
        # Espera a que el campo "from" esté visible (confirma que la SPA ya renderizó el formulario)
        # antes de escribir ambas direcciones.
        self.wait.until(EC.visibility_of_element_located(self.from_field))
        self.set_from(address_from)
        self.set_to(address_to)


    # ----- Paso 2: reserva y confirmación de teléfono -----
    def click_reservar(self):
        # Espera a que el botón "Pedir un taxi" sea clickeable y hace clic
        self.wait.until(EC.element_to_be_clickable(self.button_reservar)).click()

    def select_comfort(self):
        # Espera a que aparezca la opción "Comfort" (tras cargar tarifas) y la selecciona
       self.wait.until(EC.element_to_be_clickable(self.confort)).click()

    def click_button_phone(self):
        # Abre el campo de "Número de teléfono"
        self.wait.until(EC.element_to_be_clickable(self.phone_button)).click()

    def set_phone_field(self):
        # Espera a que el input real de teléfono sea visible (aparece tras el clic anterior) y escribe el número
        self.wait.until(EC.visibility_of_element_located(self.phone_field)).send_keys(data.phone_number)

    def click_button_sig(self):
        # Avanza al siguiente paso tras ingresar el teléfono
        self.driver.find_element(*self.button_sig).click()

    def confirm_phone_code(self, code):
        # Escribe el código SMS recibido y confirma
        self.driver.find_element(*self.code_SMS_field).send_keys(code)
        self.driver.find_element(*self.code_confirm_button).click()


    # ----- Paso 3: método de pago -----
    def click_button_payment_method(self):
        # Abre el panel de selección de método de pago
        self.driver.find_element(*self.button_payment_method).click()

    def click_pay_card(self):
        # Espera a que la opción "Agregar tarjeta" sea visible y hace clic
        self.wait.until(EC.visibility_of_element_located(self.pay_card))
        self.driver.find_element(*self.pay_card).click()

    def set_card_number(self):
        # Escribe el número de tarjeta
        self.driver.find_element(*self.card_number).send_keys(data.card_number)

    def set_card_code(self):
        # Escribe el código de seguridad (CVV) y presiona Tab para simular que el usuario sale del campo
        self.driver.find_element(*self.card_code).send_keys(data.card_code,Keys.TAB)

    def click_button_add_card(self):
        # Confirma el alta de la tarjeta
        self.driver.find_element(*self.button_add_card).click()

    def get_method_pay_count(self):
        # Cuenta cuántos métodos de pago (pp-row) hay listados; se usa antes/después
        # de agregar la tarjeta para confirmar que efectivamente se agregó uno nuevo
        return len(self.driver.find_elements(By.CLASS_NAME, 'pp-row'))

    def click_button_close_pay(self):
        # Cierra el panel de pago
        self.driver.find_element(*self.button_close_pay).click()


    # ----- Paso 4: extras del viaje -----
    def set_comment_field(self):
        # Escribe el comentario dirigido al chofer
        self.driver.find_element(*self.comment_field).send_keys(data.message_for_driver)

    def get_comment_field(self):
        # Lee el valor actual del campo de comentario (para comprobar que se escribió bien)
        return self.driver.find_element(*self.comment_field).get_property('value')

    def select_switch_man_pan(self):
        # Activa el switch de "Manta y pañuelos" haciendo clic en el slider visible
        self.driver.find_element(*self.switch_man_pan).click()

    def click_plus_helado(self):
        # Hace clic dos veces en el botón "+" del contador de Helado, para que el contador quede en 2.
        self.driver.find_element(*self.plus_helado).click()
        self.driver.find_element(*self.plus_helado).click()

    def get_helado_count(self):
        # Lee el valor actual del contador de Helado, para comprobar que quedó en 2
        return self.driver.find_element(By.CLASS_NAME, 'counter-value').text

    def click_main_button(self):
        # Confirma el pedido completo, disparando la búsqueda de un conductor
        self.wait.until(EC.element_to_be_clickable(self.main_button)).click()


    # ----- Paso 5: información del conductor asignado  -----
    def wait_for_driver_info(self, timeout=40):
        # Espera activamente (con un timeout propio, más largo que el de self.wait) a que el
        # nombre del conductor deje de estar vacío. El timeout es mayor porque la búsqueda de
        # conductor tiene una duración variable/aleatoria.
        long_wait = WebDriverWait(self.driver, timeout)
        long_wait.until(lambda driver: driver.find_element(*self.driver_name).text != '')

    def get_driver_name(self):
        # Lee el nombre del conductor asignado
        return self.driver.find_element(*self.driver_name).text

    def get_order_plate(self):
        # Lee la placa del auto asignado
        long_wait = WebDriverWait(self.driver, 40)
        long_wait.until(EC.visibility_of_element_located(self.order_plate))
        return self.driver.find_element(*self.order_plate).text

    def get_order_car_image_src(self):
        # Lee la URL de la imagen del modelo de auto asignado
        return self.driver.find_element(*self.order_car_image).get_attribute('src')

# Clase de test (pytest la detecta automáticamente por empezar con "Test")
class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=options)

    def test_order_taxi_with_all_options(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        # Paso 1: ruta
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

        # Paso 2: reservar y confirmar teléfono
        routes_page.click_reservar()
        routes_page.select_comfort()
        routes_page.click_button_phone()
        routes_page.set_phone_field()
        routes_page.click_button_sig()
        code = retrieve_phone_code(driver=self.driver) # obtiene el código real desde los logs de red
        routes_page.confirm_phone_code(code)

        # Paso 3: pago
        routes_page.click_button_payment_method()
        count_before = routes_page.get_method_pay_count()
        routes_page.click_pay_card()
        routes_page.set_card_number()
        routes_page.set_card_code()
        routes_page.click_button_add_card()
        count_after = routes_page.get_method_pay_count()

        assert count_after == count_before + 1

        routes_page.click_button_close_pay()

        # Paso 4: extras (comentario, switch de manta y pañuelos, contador de helado)
        routes_page.set_comment_field()
        assert routes_page.get_comment_field() == data.message_for_driver

        routes_page.select_switch_man_pan()
        routes_page.click_plus_helado()
        assert routes_page.get_helado_count() == '2'

        routes_page.click_main_button()

        # Paso 5 (opcional): esperar a que se asigne un conductor y comprobar su información.
        routes_page.wait_for_driver_info()
        assert routes_page.get_driver_name() != ''
        assert routes_page.get_order_plate() != ''
        assert routes_page.get_order_car_image_src() == data.comfort_car


    @classmethod
    def teardown_class(cls):
        # Se ejecuta una sola vez, al finalizar todos los tests de la clase, pase o falle el test
        cls.driver.quit()
