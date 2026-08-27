# Urban Routes – Test de Automatización con Selenium

Proyecto de práctica de QA Automation que cubre, de principio a fin, el flujo de pedir un taxi en la aplicación **Urban Routes**: ruta, reserva, confirmación de teléfono, pago, extras del viaje, y verificación de la información del conductor asignado.

## Stack

- **Python**
- **Selenium WebDriver**
- **pytest**
- Patrón de diseño **Page Object Model (POM)**

## Estructura del proyecto

```
├── data.py     # Datos de prueba: URL, direcciones, teléfono, tarjeta, mensaje, imagen de auto
├── helper.py   # Función auxiliar (no modificable) para recuperar el código SMS desde los logs de red
├── main.py     # Clase de test (TestUrbanRoutes), un método por paso del flujo
├── pages.py    # Page Object (UrbanRoutesPage): locators y acciones sobre la página
└── README.md
```

## Requisitos previos

- Python 3.10+
- Google Chrome instalado
- Entorno virtual activo (recomendado)

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

pip install selenium pytest
```

## Ejecución

Desde la carpeta del proyecto:

```bash
pytest -v
```

Para correr solo este test específico:

```bash
pytest main.py::TestUrbanRoutes::test_order_taxi_with_all_options -v
```

## Qué cubre el test (`test_order_taxi_with_all_options`)

El test es **end-to-end**: todos los pasos se ejecutan en un solo método porque cada uno depende del estado dejado por el anterior (no se puede, por ejemplo, probar el pago sin haber reservado antes).

| Test                                | Qué hace                                                     | Qué comprueba                                                                                      |
|-------------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| 1. test_set_routes                  | Abre la app y escribe dirección de origen y destino          | Los campos reflejan el valor escrito                                                               |
| 2. test_select_comfort_plan         | Pide el taxi y selecciona la tarifa "Comfort"                | La tarjeta de Comfort queda marcada como activa (clase active)                                     |
| 3. test_fill_phone_number           | Ingresa el teléfono, recupera y confirma el código SMS       | El campo de teléfono conserva el valor esperado                                                    |
| 4. test_fill_card                   | Agrega una tarjeta como método de pago                       | La lista de métodos de pago aumenta en 1                                                           |
| 5. test_comment_for_driver          | Escribe un comentario para el chofer                         | El comentario coincide con el escrito                                                              |
| 6. test_order_blanket_handkerchiefs | Activa el switch de "Manta y pañuelos"                       | El checkbox real queda marcado (checked)                                                           |
| 7. test_order_two_ice_creams        | 	Incrementa el contador de Helado a 2                         | El contador queda en 2                                                                             |
| 8. test_car_search_modal_appears    | 	Confirma el pedido y espera a que se asigne un conductor     | El nombre del conductor, la placa y la imagen del auto no están vacíos / coinciden con lo esperado |

## Notas de diseño

- **Waits explícitos**: se usan `WebDriverWait` + `expected_conditions` en los puntos donde un elemento aparece o se vuelve interactuable tras una acción previa (clic, transición, modal), en vez de esperas fijas (`time.sleep`), para que el test sea estable sin depender de una duración arbitraria.
- **Timeout extendido para el conductor**: `wait_for_driver_info` usa un `WebDriverWait` propio de 40s (en vez del wait por defecto de 10s), porque la asignación de conductor tiene una duración variable observada de hasta ~30 segundos.
- **Comprobaciones por presencia de contenido, no por valor fijo**: el nombre del conductor, la placa y el auto asignado pueden variar entre corridas, así que se valida que no estén vacíos en vez de comparar contra un valor hardcodeado (salvo la imagen del auto Comfort, que sí se compara contra la URL esperada en `data.py`).
- **Conteo relativo, no absoluto**: la comprobación del método de pago compara `count_after == count_before + 1`, no un número fijo, para que el test siga siendo válido aunque cambie la cantidad de métodos de pago por defecto.

## Datos de prueba (`data.py`)

Contiene la URL del entorno de pruebas y los valores usados a lo largo del flujo: direcciones, número de teléfono, datos de tarjeta, mensaje para el chofer, y la URL de imagen esperada para el auto tipo Comfort.