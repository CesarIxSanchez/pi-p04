# main.py
# (Este archivo va en la raíz de tu proyecto)

import time
import RPi.GPIO as GPIO
import logging

# Importaciones correctas según tu estructura de archivos
from src.client.api_client import SensorAPIClient, APIClientError
from src.hardware.servo import Servo

# --- Configuración Principal ---
SERVO_PIN = 18 # !! IMPORTANTE: Cambia este pin al pin BCM de tu servo
API_BASE_URL = "http://127.0.0.1:5000" # URL de tu API
# --- Fin de la Configuración ---


def map_value(value, in_min, in_max, out_min, out_max):
    """ Mapea un valor de un rango a otro. """
    if (in_max - in_min) == 0: return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main():
    """
    Punto de entrada principal del programa actuador.
    """
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - [MainLogic] - %(levelname)s - %(message)s')
    
    logging.info("Iniciando programa de control del servo...")
    
    # 1. Inicializar el hardware (Actuador)
    # [cite: servo.py]
    servo = Servo(pin=SERVO_PIN, min_angle=0, max_angle=180)
    
    # 2. Inicializar el cliente (Sensores)
    # [cite: api_client.py]
    client = SensorAPIClient(base_url=API_BASE_URL)

    logging.info(f"Servo inicializado en pin {SERVO_PIN}.")
    logging.info(f"Cliente API configurado para {API_BASE_URL}.")
    
    logging.info("Centrando servo a 90 grados...")
    servo.set_angle(90)
    time.sleep(1)

    logging.info("Iniciando bucle de control. Presiona CTRL+C para salir.")

    try:
        while True:
            # 3. Leer datos del sensor (vía API)
            try:
                # Ahora pedimos el 'value_percentage' que definimos en la API
                pot_value = client.get_potentiometer_value()
                
                if pot_value is None:
                    logging.warning("La API devolvió 'None'. Revisar el sensor en la Pi.")
                    time.sleep(2)
                    continue

            except APIClientError as e:
                logging.error(f"Error de conexión con la API: {e}")
                logging.error("¿Está 'src/api/sensor_api.py' ejecutándose?")
                time.sleep(5)
                continue
            
            # 4. Tomar decisión y actuar (Lógica)
            
            # Mapeamos el porcentaje (0-100) al ángulo del servo (0-180)
            target_angle = map_value(pot_value, 0.0, 100.0, 0, 180)
            
            # 5. Controlar el actuador (Servo)
            servo.set_angle(target_angle)
            
            time.sleep(0.05) 

    except KeyboardInterrupt:
        logging.info("\nPrograma detenido por el usuario (CTRL+C).")
    
    finally:
        # 6. Limpieza
        logging.info("Limpiando recursos...")
        servo.cleanup()
        GPIO.cleanup()
        logging.info("¡Hasta luego!")

if __name__ == "__main__":
    main()