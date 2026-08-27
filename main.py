import data
from selenium import webdriver

from helpers import retrieve_phone_code
from pages import UrbanRoutesPage


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


        # Paso 1: ruta
    def test_set_routes(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.ADDRESS_FROM, data.ADDRESS_TO)
        assert routes_page.get_from() == data.ADDRESS_FROM
        assert routes_page.get_to() == data.ADDRESS_TO

        # Paso 2: reservar
    def test_select_comfort_plan(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_reservar()
        routes_page.select_comfort()
        assert routes_page.get_comfort_active()

        # Paso 3: confirmar telefono
    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_button_phone()
        routes_page.set_phone_field()
        routes_page.click_button_sig()
        code = retrieve_phone_code(driver=self.driver) # obtiene el código real desde los logs de red
        routes_page.confirm_phone_code(code)
        assert routes_page.get_phone_field() == data.PHONE_NUMBER

        # Paso 4: pago
    def test_fill_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_button_payment_method()
        count_before = routes_page.get_method_pay_count()
        routes_page.click_pay_card()
        routes_page.set_card_number()
        routes_page.set_card_code()
        routes_page.click_button_add_card()
        count_after = routes_page.get_method_pay_count()
        assert count_after == count_before + 1
        routes_page.click_button_close_pay()

        # Paso 5: comentario
    def test_comment_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_comment_field()
        assert routes_page.get_comment_field() == data.MESSAGE_FOR_DRIVER

        # Paso 6: switch manta y pañuelos
    def test_order_blanket_handkerchiefs(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.select_switch_blanket_handkerchiefs()
        assert routes_page.get_blanket_handkerchiefs_checked()

        # Paso 7: helados
    def test_order_two_ice_creams(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_ice_cream()
        assert routes_page.get_ice_cream_count() == '2'

        # Paso 8: espera del conductor
    def test_car_search_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_main_button()
        routes_page.wait_order_popup()

        # Paso 5 (opcional): esperar a que se asigne un conductor y comprobar su información.
        routes_page.wait_for_driver_info()
        assert routes_page.get_driver_name() != ''
        assert routes_page.get_order_plate() != ''
        assert routes_page.get_order_car_image_src() == data.COMFORT_CAR


    @classmethod
    def teardown_class(cls):
        # Se ejecuta una sola vez, al finalizar todos los tests de la clase, pase o falle el test
        cls.driver.quit()
