# (Punto de entrada principal del proyecto - Cliente)
import time
import RPi.GPIO as GPIO
import logging
import sys
import os

# --- Configuración Principal ---
SERVO_PIN = 18 # Pin BCM para el servo

# --- Importaciones del Proyecto ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from client.api_client import SensorAPIClient, APIClientError
    from hardware.servo import Servo
except ImportError as e:
    print("Error: No se pudieron importar los módulos.")
    print(f"Detalle: {e}")
    sys.exit(1)


def map_value(value, in_min, in_max, out_min, out_max):
    """
    Función de utilidad para mapear un valor de un rango a otro.

    :param value: El valor a mapear.
    :param in_min: Mínimo del rango de entrada.
    :param in_max: Máximo del rango de entrada.
    :param out_min: Mínimo del rango de salida.
    :param out_max: Máximo del rango de salida.
    :return: El valor mapeado.
    """
    if (in_max - in_min) == 0: return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main(api_host):
    """
    Función principal del programa actuador (Cliente).

    :param api_host: La dirección IP del servidor API.
    """
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - [MainLogic] - %(levelname)s - %(message)s')
    
    api_base_url = f"http://{api_host}:5000"
    
    logging.info(f"Iniciando programa de control del servo...")
    logging.info(f"Intentando conectar a la API en: {api_base_url}")
    
    try:
        GPIO.setmode(GPIO.BCM)
    except Exception as e:
        logging.warning(f"Modo GPIO ya configurado o error: {e}")

    # 1. Inicializar el hardware (Actuador)
    servo = Servo(pin=SERVO_PIN, min_angle=0, max_angle=180)
    
    # 2. Inicializar el cliente (Sensores)
    client = SensorAPIClient(base_url=api_base_url)

    logging.info(f"Servo inicializado en pin {SERVO_PIN}.")
    logging.info(f"Cliente API configurado para {api_base_url}.")
    
    logging.info("Centrando servo a 90 grados...")
    servo.set_angle(90)
    time.sleep(1)

    logging.info("Iniciando bucle de control. Presiona CTRL+C para salir.")
    

    try:
        while True:
            try:
                # 3. Leer SOLAMENTE el potenciómetro
                pot_value = client.get_potentiometer_value()
                
                if pot_value is None:
                    logging.warning("La API devolvió 'None'. Revisar el sensor en la Pi Servidor.")
                    time.sleep(1)
                    continue 

            except APIClientError as e:
                logging.error(f"Error de conexión con la API: {e}")
                logging.error(f"¿Está la Pi Servidor en {api_base_url} ejecutándose?")
                time.sleep(3) 
                continue 
            

            
            # 5. Mapear y controlar el actuador
            target_angle = map_value(pot_value, 0.0, 100.0, 0, 180)
            servo.set_angle(target_angle)
            
            # Sleep muy pequeño para respuesta rápida
            time.sleep(0.01)

    except KeyboardInterrupt:
        logging.info("\nPrograma detenido por el usuario (CTRL+C).")
    
    finally:
        # 6. Limpieza
        logging.info("Limpiando recursos...")
        servo.cleanup()
        GPIO.cleanup()
        logging.info("¡Hasta luego!")


# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    
    # Lógica de Modo Dual (Pi-Cliente y Pi-Servidor)
    
    if len(sys.argv) > 1:

        host_ip = sys.argv[1]
    else:

        host_ip = "127.0.0.1"
        
    main(host_ip)