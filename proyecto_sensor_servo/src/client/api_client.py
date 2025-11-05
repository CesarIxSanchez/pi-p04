import requests
import time
import logging

# Configurar logging para este módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [APIClient] - %(levelname)s - %(message)s'
)

class APIClientError(Exception):
    """Excepción personalizada para errores del cliente de API."""
    pass

class SensorAPIClient:
    """
    Cliente para consumir la API de sensores de la Raspberry Pi.

    Cumple con la Tarea 3:
    - Maneja errores de conexión.
    - Implementa reintentos.
    """

    def __init__(self, base_url="http://127.0.0.1:5000", retries=3, delay=2, timeout=5):
        """
        Inicializa el cliente.

        :param base_url: La URL base del servidor Flask (ej. "http://<ip_raspi>:5000").
        :param retries: Número de reintentos en caso de fallo de conexión. [Cite: Tarea 3]
        :param delay: Tiempo (segundos) de espera entre reintentos.
        :param timeout: Tiempo (segundos) de espera para una respuesta.
        """
        # Asegurarse de que la URL no tenga una barra al final
        self.base_url = base_url.rstrip('/')
        self.retries = retries
        self.delay = delay
        self.timeout = timeout
        logging.info(f"Cliente API inicializado. URL base: {self.base_url}, Reintentos: {self.retries}")

    def _make_request(self, endpoint):
        """
        Método privado para realizar solicitudes GET con reintentos.
        Esto cumple con el requisito de "Implementar reintentos". [Cite: Tarea 3]

        :param endpoint: El endpoint de la API (ej. "/api/potentiometer").
        :return: El diccionario JSON de la respuesta.
        :raises APIClientError: Si la solicitud falla después de todos los reintentos.
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                
                # Comprobar si la solicitud fue exitosa (200-299)
                response.raise_for_status() 
                
                # Si fue exitosa, devolver el JSON
                data = response.json()
                logging.debug(f"Solicitud exitosa a {url}. Datos: {data}")
                return data

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Manejo de errores de conexión y timeout [Cite: Tarea 3]
                logging.warning(f"Error de conexión/timeout en {url} (Intento {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    print(f"Intento {attempt + 1} fallido. Reintentando en {self.delay}s...")
                    time.sleep(self.delay) # Esperar antes del siguiente intento
                else:
                    logging.error(f"Fallaron todos los reintentos para {url}")
                    raise APIClientError(f"No se pudo conectar a {url} después de {self.retries} intentos.") from e

            except requests.exceptions.HTTPError as e:
                # Error del servidor (ej. 500, 404)
                logging.error(f"Error HTTP en {url}: {e.response.status_code} {e.response.text}")
                raise APIClientError(f"Error del servidor en {url}: {e.response.status_code}") from e
            
            except requests.exceptions.RequestException as e:
                # Otro error genérico de requests
                logging.error(f"Error inesperado de 'requests' en {url}: {e}")
                raise APIClientError(f"Error inesperado en la solicitud: {e}") from e
        
        # Si el bucle termina sin una excepción o retorno
        raise APIClientError(f"Fallo desconocido al contactar {url}")

    def get_potentiometer_value(self):
        """
        Obtiene el valor del potenciómetro desde la API.

        :return: El valor (float) o None si la API devuelve un error de lógica.
        :raises APIClientError: Si la conexión falla.
        """
        try:
            data = self._make_request("/api/potentiometer")
            
            # Validar la respuesta (basado en schemas.py)
            if data.get('status') == 'success' and data.get('sensor') == 'potentiometer':
                return data.get('value')
            else:
                message = data.get('message', 'Respuesta inválida desde la API')
                logging.error(f"API devolvió un error (potenciómetro): {message}")
                return None # El servidor devolvió un error, pero la conexión fue exitosa.

        except APIClientError as e:
            logging.error(f"No se pudo obtener el valor del potenciómetro: {e}")
            raise # Relanzar la excepción para que el llamador (main.py) la maneje

    def get_ultrasonic_distance(self):
        """
        Obtiene la distancia del sensor ultrasónico desde la API.

        :return: El valor (float) o None si la API devuelve un error de lógica.
        :raises APIClientError: Si la conexión falla.
        """
        try:
            data = self._make_request("/api/ultrasonic")
            
            # Validar la respuesta (basado en sensor_api.py)
            if data.get('status') == 'success' and data.get('sensor') == 'ultrasonic':
                return data.get('value')
            else:
                message = data.get('message', 'Respuesta inválida desde la API')
                logging.error(f"API devolvió un error (ultrasónico): {message}")
                return None # El servidor devolvió un error, pero la conexión fue exitosa.

        except APIClientError as e:
            logging.error(f"No se pudo obtener la distancia ultrasónica: {e}")
            raise # Relanzar la excepción