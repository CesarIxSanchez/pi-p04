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

# --- Configuración Principal ---
SERVO_PIN = 4 # Pin BCM para el servo

# Lógica del Ultrasónico
# Distancia (en cm) para el bloqueo de seguridad.
SAFETY_DISTANCE_CM = 15.0 

# --- Importaciones del Proyecto ---

# Añadir la carpeta 'src' al path de Python para encontrar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    # Cliente de API
    from client.api_client import SensorAPIClient, APIClientError
    # Control de Servo
    from hardware.servo import Servo
except ImportError as e:
    print("Error: No se pudieron importar los módulos.")
    print("Asegúrate de estar en el entorno virtual ('venv')")
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

    :param api_host: La dirección IP del servidor API (ej. '127.0.0.1' o '192.168.1.100').
    """
    # Configurar el logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - [MainLogic] - %(levelname)s - %(message)s')
    
    # Construir la URL base de la API
    api_base_url = f"http://{api_host}:5000"
    
    logging.info(f"Iniciando programa de control del servo...")
    logging.info(f"Intentando conectar a la API en: {api_base_url}")
    
    # Configurar el modo GPIO una sola vez
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
    
    # Centrar el servo al inicio
    logging.info("Centrando servo a 90 grados...")
    servo.set_angle(90)
    time.sleep(1)

    logging.info("Iniciando bucle de control. Presiona CTRL+C para salir.")
    
    # Bandera para el bloqueo de seguridad del ultrasónico
    safety_lock = False 

    try:
        # Bucle principal
        while True:
            try:
                # 3. Leer AMBOS sensores desde la API
                pot_value = client.get_potentiometer_value()
                distance = client.get_ultrasonic_distance()
                
                # Manejar si la API devuelve un error (ej. sensor desconectado)
                if pot_value is None or distance is None:
                    logging.warning("La API devolvió 'None'. Revisar los sensores en la Pi Servidor.")
                    time.sleep(1)
                    continue # Saltar esta iteración

            except APIClientError as e:
                logging.error(f"Error de conexión con la API: {e}")
                logging.error(f"¿Está la Pi Servidor en {api_base_url} ejecutándose?")
                time.sleep(3) # Esperar antes de reintentar
                continue # Saltar esta iteración
            
            # 4. LÓGICA DE DECISIÓN (Ultrasónico)
            
            if distance < SAFETY_DISTANCE_CM:
                # bjeto demasiado cerca.
                if not safety_lock:
                    # Solo imprimir el mensaje la primera vez que se activa
                    logging.warning(f"¡OBJETO DETECTADO a {distance:.1f}cm! Servo detenido.")
                    safety_lock = True
                
                # Mantener el servo en su última posición segura
                servo.hold_position() 
                
            else:
                # Es seguro moverse
                if safety_lock:
                    # Solo imprimir el mensaje la primera vez que se desactiva
                    logging.info("Zona despejada. Reactivando control del potenciómetro.")
                    safety_lock = False

                # 5. Mapear y controlar el actuador
                # Mapear el porcentaje (0-100) al ángulo del servo (0-180)
                target_angle = map_value(pot_value, 0.0, 100.0, 0, 180)
                servo.set_angle(target_angle)
            
            # Sleep muy pequeño para no saturar la CPU al 100%.
            time.sleep(0.01)

    except KeyboardInterrupt:
        logging.info("\nPrograma detenido por el usuario (CTRL+C).")
    
    finally:
        # 6. Limpieza
        logging.info("Limpiando recursos...")
        servo.cleanup()
        GPIO.cleanup() # Limpieza general de todos los pines
        logging.info("¡Hasta luego!")


# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    
    # LÓGICA DE DUAL
    
    if len(sys.argv) > 1:
        # MODO 2: REMOTO
        # El usuario proveyó una IP (ej. python main.py 192.168.1.100)
        host_ip = sys.argv[1]
    else:
        # MODO 1: LOCAL
        # El usuario no proveyó IP (ej. python main.py)
        # Se asume que el servidor corre en la misma máquina.
        host_ip = "127.0.0.1"
        
    # Llamar a la función principal con la IP correcta
    main(host_ip)