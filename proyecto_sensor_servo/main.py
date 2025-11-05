# src/api/sensor_api.py


from flask import Flask, jsonify
import RPi.GPIO as GPIO
import threading
import time
from datetime import datetime
import logging

# Importamos las clases de hardware modulares
from ..hardware.potentiometer import Potentiometer
from ..hardware.ultrasonic import UltrasonicSensor

# --- Configuración del Hardware ---
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - [APIServer] - %(levelname)s - %(message)s')

POT_PIN = 17         # Pin BCM para el Potenciómetro
ULTRA_TRIG_PIN = 23  # Pin BCM para el Ultrasónico (Trig)
ULTRA_ECHO_PIN = 24  # Pin BCM para el Ultrasónico (Echo)

# --- Variables Globales y Cierre (Lock) ---
# Usamos un diccionario para guardar los datos de los sensores
# El hilo del potenciómetro escribirá aquí, y Flask leerá de aquí.
sensor_data = {
    "potentiometer": {
        "raw_value": 0,
        "percentage": 0.0,
        "last_update": None
    },
    "ultrasonic": {
        "distance_cm": 0.0,
        "last_update": None
    }
}
# El Lock es crucial para evitar problemas al acceder a sensor_data
# desde dos hilos (Flask y el hilo del sensor)
data_lock = threading.Lock()

# --- Instancias de Hardware y Flask ---
app = Flask(__name__)

# Inicializamos los objetos de hardware
# (GPIO.setmode se llamará una vez en main)
pot = Potentiometer(pin=POT_PIN)
ultra_sensor = UltrasonicSensor(trig_pin=ULTRA_TRIG_PIN, echo_pin=ULTRA_ECHO_PIN)

# --- Hilo de Lectura del Potenciómetro ---
# (Tomado de tu lógica de main.py para no bloquear Flask)

def potentiometer_update_loop():
    """
    Este hilo se ejecuta en segundo plano para leer el potenciómetro
    continuamente y actualizar la variable global sensor_data.
    """
    global pot, sensor_data, data_lock
    logging.info("Hilo del potenciómetro iniciado. Iniciando calibración...")
    
    # Ejecutamos la calibración del módulo Potentiometer
    # [cite: potentiometer.py]
    pot.calibrate()
    
    logging.info("Calibración del potenciómetro completada.")
    
    while True:
        try:
            # Leemos los valores usando los métodos de nuestra clase
            raw = pot.get_raw_value()
            perc = pot.get_percentage()

            # Bloqueamos el acceso para escribir los datos de forma segura
            with data_lock:
                sensor_data["potentiometer"]["raw_value"] = raw
                sensor_data["potentiometer"]["percentage"] = round(perc, 2)
                sensor_data["potentiometer"]["last_update"] = datetime.now().isoformat()
            
            # Imprimir en consola local (como en tu main anterior)
            logging.debug(f"Pot: {raw:4d} -> {perc:5.1f}%")
            
            time.sleep(0.1) # Tasa de sondeo

        except Exception as e:
            logging.error(f"Error en el hilo del potenciómetro: {e}")
            time.sleep(2)

# --- Endpoints de la API ---

@app.route('/')
def home():
    return jsonify({
        "mensaje": "API de Sensores y Actuadores (Modular)",
        "endpoints": ["/api/potentiometer", "/api/ultrasonic"]
    })

@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    """
    Endpoint para obtener el valor actual del potenciómetro.
    Lee los datos del hilo de fondo, por lo que es muy rápido.
    """
    try:
        # Leemos los datos de forma segura
        with data_lock:
            data_copy = sensor_data["potentiometer"].copy()
            
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value_raw': data_copy["raw_value"],
            'value_percentage': data_copy["percentage"],
            'last_update': data_copy["last_update"]
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ultrasonic', methods=['GET'])
def get_ultrasonic_distance():
    """
    Endpoint para el ultrasónico.
    Este sensor es rápido, lo leemos directamente.
    """
    global sensor_data, data_lock, ultra_sensor
    try:
        # [cite: ultrasonic.py]
        distance = ultra_sensor.get_distance()
        
        # Actualizamos la variable global también
        with data_lock:
            sensor_data["ultrasonic"]["distance_cm"] = distance
            sensor_data["ultrasonic"]["last_update"] = datetime.now().isoformat()
            
        response = {
            'status': 'success',
            'sensor': 'ultrasonic',
            'value': distance,
            'unit': 'cm',
            'last_update': sensor_data["ultrasonic"]["last_update"]
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'No se pudo leer el sensor: {str(e)}'}), 500

# --- Punto de Entrada del Servidor ---
if __name__ == '__main__':
    try:
        # Configuración global de GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Iniciar el hilo de fondo para el potenciómetro
        logging.info("Iniciando hilo de lectura del potenciómetro...")
        sensor_thread = threading.Thread(target=potentiometer_update_loop, daemon=True)
        sensor_thread.start()

        # Iniciar el servidor Flask
        logging.info(f"Iniciando servidor Flask en http://0.0.0.0:5000")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        logging.info("\nServidor detenido por el usuario.")
    
    finally:
        logging.info("Limpiando pines GPIO...")
        GPIO.cleanup()
        logging.info("¡Hasta luego!")