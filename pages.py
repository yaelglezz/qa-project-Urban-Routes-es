import data
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# Page Object: Encapsula todos los locators y acciones de la página de Urban Routes.
# El test nunca interactúa con Selenium directamente, solo llama a estos métodos.
class UrbanRoutesPage:
    # --- Locators: paso 1, ruta ---
    from_field = (By.ID, 'from') # Campo de dirección de origen
    to_field = (By.ID, 'to') # Campo de dirección de destino

    # --- Locators: paso 2, reserva y confirmación de teléfono ---
    button_reservar = (By.XPATH, './/button[text()="Pedir un taxi"]') # Botón para iniciar la reserva
    comfort = (By.XPATH, './/div[text()="Comfort"]') # Opción de tarifa "Comfort"
    tcard_comfort = (By.XPATH, './/div[@class="tcard-title" and text()="Comfort"]/ancestor::div[contains(@class, "tcard")]') # Para verificar si comfort está activo

    # --- Locators: paso 3, confirmación de teléfono ---
    phone_button = (By.XPATH, './/div[text()="Número de teléfono"]') # Abre el campo de teléfono
    phone_field = (By.ID, 'phone') # Input real del número de teléfono
    next_button = (By.XPATH, './/button[text()="Siguiente"]')  # Botón "Siguiente" tras ingresar el teléfono
    sms_code_field = (By.ID, 'code') # Input del código SMS recibido
    code_confirm_button = (By.XPATH, './/button[text()="Confirmar"]') # Confirma el código SMS

    # --- Locators: paso 4, método de pago ---
    button_payment_method = (By.CLASS_NAME, 'pp-text') # Abre el selector de método de pago
    pay_card = (By.XPATH, './/div[text()="Agregar tarjeta"]') # Opción "Agregar tarjeta"
    card_number = (By.ID, 'number') # Input del número de tarjeta
    card_code = (By.XPATH, './/div[@class="card-code-input"]/input') # Input del código de seguridad (CVV)
    button_add_card = (By.XPATH, './/button[text()="Agregar"]') # Confirma el alta de la tarjeta
    payment_method_rows = (By.CLASS_NAME, 'pp-row')
    button_close_pay = (By.XPATH, './/div[@class="payment-picker open"]//div[@class="section active"]//button[@class="close-button section-close"]') # Cierra el panel de pago; acotado al panel "open"/"active" para evitar ambigüedad con otros paneles

    # --- Locators: paso 5, 6, 7 y 8 extras del viaje ---
    comment_field =  (By.ID, 'comment') # Campo de comentario para el chofer
    switch_blanket_handkerchiefs= (By.XPATH, './/div[text()="Manta y pañuelos"]/following-sibling::div//span') # Switch visual de "Manta y pañuelos" (el input real de checkbox no se usa aquí, se hace clic en el slider)
    switch_blanket_handkerchiefs_active = (By.XPATH, './/div[text()="Manta y pañuelos"]/following-sibling::div//input')
    add_ice_cream_button = (By.XPATH, './/div[text()="Helado"]/following-sibling::div//div[@class="counter-plus"]') # Botón "+" del contador de Helado
    counter_ice_cream = (By.XPATH, './/div[text()="Cubeta de helado"]/following-sibling::div//div[@class="counter-value"]')
    main_button = (By.CSS_SELECTOR, 'button.smart-button') # Botón principal que confirma el pedido
    order_popup = (By.CLASS_NAME, 'order-body')

    # --- Locators: paso 9, información del conductor asignado (comprobación opcional) ---
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
       self.wait.until(EC.element_to_be_clickable(self.comfort)).click()

    def get_comfort_active(self):
        tcard = self.driver.find_element(*self.tcard_comfort)
        return "active" in tcard.get_attribute("class")

    def click_button_phone(self):
        # Abre el campo de "Número de teléfono"
        self.wait.until(EC.element_to_be_clickable(self.phone_button)).click()

    def set_phone_field(self,phone_number):
        # Espera a que el input real de teléfono sea visible (aparece tras el clic anterior) y escribe el número
        self.wait.until(EC.visibility_of_element_located(self.phone_field)).send_keys(phone_number)

    def get_phone_field(self):
        return self.driver.find_element(*self.phone_field).get_property('value')

    def click_next_button(self):
        # Avanza al siguiente paso tras ingresar el teléfono
        self.driver.find_element(*self.next_button).click()

    def confirm_phone_code(self, code):
        # Escribe el código SMS recibido y confirma
        self.driver.find_element(*self.sms_code_field).send_keys(code)
        self.driver.find_element(*self.code_confirm_button).click()


    # ----- Paso 3: método de pago -----
    def click_button_payment_method(self):
        # Abre el panel de selección de método de pago
        self.driver.find_element(*self.button_payment_method).click()

    def click_pay_card(self):
        # Espera a que la opción "Agregar tarjeta" sea visible y hace clic
        self.wait.until(EC.visibility_of_element_located(self.pay_card))
        self.driver.find_element(*self.pay_card).click()

    def set_card_number(self,card_number):
        # Escribe el número de tarjeta
        self.driver.find_element(*self.card_number).send_keys(card_number)

    def set_card_code(self, card_code):
        # Escribe el código de seguridad (CVV) y presiona Tab para simular que el usuario sale del campo
        self.driver.find_element(*self.card_code).send_keys(card_code,Keys.TAB)

    def click_button_add_card(self):
        # Confirma el alta de la tarjeta
        self.driver.find_element(*self.button_add_card).click()

    def get_payment_methods_count(self):
        # Cuenta cuántos métodos de pago (pp-row) hay listados; se usa antes/después
        # de agregar la tarjeta para confirmar que efectivamente se agregó uno nuevo
        return len(self.driver.find_elements(*self.payment_method_rows))

    def click_button_close_pay(self):
        # Cierra el panel de pago
        self.driver.find_element(*self.button_close_pay).click()


    # ----- Paso 4: extras del viaje -----
    def set_comment_field(self, message_for_driver):
        # Escribe el comentario dirigido al chofer
        self.driver.find_element(*self.comment_field).send_keys(message_for_driver)

    def get_comment_field(self):
        # Lee el valor actual del campo de comentario (para comprobar que se escribió bien)
        return self.driver.find_element(*self.comment_field).get_property('value')

    def select_switch_blanket_handkerchiefs(self):
        # Activa el switch de "Manta y pañuelos" haciendo clic en el slider visible
        self.driver.find_element(*self.switch_blanket_handkerchiefs).click()

    def get_blanket_handkerchiefs_checked(self):
        return self.driver.find_element(*self.switch_blanket_handkerchiefs_active).get_property('checked')

    def add_ice_cream(self, amount):
        # Hace clic en el botón "+" del contador de Helado, para que el contador quede en 2.
        for _ in range(amount):
            self.driver.find_element(*self.add_ice_cream_button).click()

    def get_ice_cream_count(self):
        # Lee el valor actual del contador de Helado, para comprobar que quedó en 2
        return self.driver.find_element(*self.counter_ice_cream).text

    def click_main_button(self):
        # Confirma el pedido completo, disparando la búsqueda de un conductor
        self.wait.until(EC.element_to_be_clickable(self.main_button)).click()

    def wait_order_popup(self):
        self.wait.until(EC.visibility_of_element_located(self.order_popup))

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
        image_src = routes_page.get_order_car_image_src()
        assert image_src != ''
        assert data.COMFORT_CAR_IMAGE_NAME in image_src

