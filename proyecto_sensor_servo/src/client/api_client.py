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

    """

    def __init__(self, base_url="http://127.0.0.1:5000", retries=3, delay=2, timeout=5):
        """
        Inicializa el cliente.

        """
        self.base_url = base_url.rstrip('/')
        self.retries = retries
        self.delay = delay
        self.timeout = timeout
        logging.info(f"Cliente API inicializado. URL base: {self.base_url}, Reintentos: {self.retries}")

    def _make_request(self, endpoint):
        """
        Método privado para realizar solicitudes GET con reintentos.

        :param endpoint: El endpoint de la API (ej. "/api/potentiometer").
        :return: El diccionario JSON de la respuesta.
        :raises APIClientError: Si la solicitud falla después de todos los reintentos.
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status() 
                data = response.json()
                logging.debug(f"Solicitud exitosa a {url}. Datos: {data}")
                return data

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logging.warning(f"Error de conexión/timeout en {url} (Intento {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    print(f"Intento {attempt + 1} fallido. Reintentando en {self.delay}s...")
                    time.sleep(self.delay)
                else:
                    logging.error(f"Fallaron todos los reintentos para {url}")
                    raise APIClientError(f"No se pudo conectar a {url} después de {self.retries} intentos.") from e

            except requests.exceptions.HTTPError as e:
                logging.error(f"Error HTTP en {url}: {e.response.status_code} {e.response.text}")
                raise APIClientError(f"Error del servidor en {url}: {e.response.status_code}") from e
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Error inesperado de 'requests' en {url}: {e}")
                raise APIClientError(f"Error inesperado en la solicitud: {e}") from e
        
        raise APIClientError(f"Fallo desconocido al contactar {url}")

    def get_potentiometer_value(self):
        """
        Obtiene el valor del potenciómetro desde la API.
        """
        try:
            data = self._make_request("/api/potentiometer")
            
            if data.get('status') == 'success' and data.get('sensor') == 'potentiometer':
                # Devolver el valor de porcentaje
                return data.get('value_percentage')
            else:
                message = data.get('message', 'Respuesta inválida desde la API')
                logging.error(f"API devolvió un error (potenciómetro): {message}")
                return None

        except APIClientError as e:
            logging.error(f"No se pudo obtener el valor del potenciómetro: {e}")
            raise 

