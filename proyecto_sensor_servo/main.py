"""
Punto de entrada principal (Cliente)
Este script consume la API (que se ejecuta en otro proceso)
y utiliza los datos del potenciómetro para controlar un servomotor.

Debe ejecutarse en la Raspberry Pi, en una terminal SEPARADA
después de haber iniciado 'src/api/sensor_api.py'.

Ejecución: python main.py
"""
import time
import RPi.GPIO as GPIO
import logging
import sys
import os

# --- Importación ---
# Añade el directorio raíz del proyecto (proyecto_sensor_servo) al path de Python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(SCRIPT_DIR) # main.py está en la raíz
sys.path.append(PROJECT_ROOT)

from src.client.api_client import SensorAPIClient, APIClientError
from src.hardware.servo import Servo

# --- Configuración Principal ---
SERVO_PIN = 18 # Pin BCM del servo
API_BASE_URL = "http://127.0.0.1:5000" # URL del API 

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
    
    # 1. Configurar modo GPIO
    GPIO.setmode(GPIO.BCM)
    
    # 2. Inicializar el hardware (Actuador)
    servo = Servo(pin=SERVO_PIN, min_angle=0, max_angle=180)
    
    # 3. Inicializar el cliente (Sensores)
    client = SensorAPIClient(base_url=API_BASE_URL)

    logging.info(f"Servo inicializado en pin {SERVO_PIN}.")
    logging.info(f"Cliente API configurado para {API_BASE_URL}.")
    
    logging.info("Centrando servo a 90 grados...")
    servo.set_angle(90)
    time.sleep(1)

    logging.info("Iniciando bucle de control. Presiona CTRL+C para salir.")

    try:
        while True:
            # 4. Leer datos del sensor (vía API)
            try:
                # Pedimos el valor porcentual
                pot_percentage = client.get_potentiometer_percentage()
                
                if pot_percentage is None:
                    logging.warning("La API devolvió 'None'. Revisar el sensor en la Pi.")
                    time.sleep(2)
                    continue

            except APIClientError as e:
                logging.error(f"Error de conexión con la API: {e}")
                logging.error("¿Está 'src/api/sensor_api.py' ejecutándose?")
                time.sleep(5)
                continue
            
            # 5. Tomar decisión y actuar
            
            # Mapeamos el porcentaje (0-100) al ángulo del servo (0-180)
            target_angle = map_value(pot_percentage, 0.0, 100.0, 0, 180)
            
            # 6. Controlar el actuador (Servo)
            print(f"Potenciómetro: {pot_percentage:.1f}% -> Ángulo Servo: {target_angle:.1f}°")
            servo.set_angle(target_angle)
            
            # El sleep(0.5) ya está dentro de servo.set_angle()
            # por lo que el bucle se actualiza aprox. cada 0.5s

    except KeyboardInterrupt:
        logging.info("\nPrograma detenido por el usuario (CTRL+C).")
    
    finally:
        # 7. Limpieza
        logging.info("Limpiando recursos...")
        servo.cleanup()
        # Limpieza general de GPIO
        GPIO.cleanup()
        logging.info("¡Hasta luego!")

if __name__ == "__main__":
    main()