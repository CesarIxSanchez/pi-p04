"""
Servidor Flask (API)
Este script inicia un servidor web que expone los datos de los sensores
conectados a la Raspberry Pi (Potenciómetro y Ultrasónico).

Debe ejecutarse en la Raspberry Pi.
Ejecución: python src/api/sensor_api.py
"""

import RPi.GPIO as GPIO
from flask import Flask, jsonify
import sys
import os

# Añade el directorio raíz del proyecto (proyecto_sensor_servo) al path de Python
# Esto nos permite usar importaciones absolutas (ej. from src.hardware...)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
sys.path.append(PROJECT_ROOT)

from src.hardware.potentiometer import Potentiometer
from src.hardware.ultrasonic import UltrasonicSensor # Importa la clase que creamos

app = Flask(__name__)

# --- Configuración del Hardware ---
# Se configuran los pines BCM
POT_PIN = 17
ULTRA_TRIG_PIN = 23
ULTRA_ECHO_PIN = 24

# --- Inicialización de Hardware ---
# Establecer el modo GPIO una sola vez
GPIO.setmode(GPIO.BCM)

# Crear instancias de los sensores
pot = Potentiometer(pin=POT_PIN)
ultra_sensor = UltrasonicSensor(trig_pin=ULTRA_TRIG_PIN, echo_pin=ULTRA_ECHO_PIN)


# --- Endpoints de la API ---

@app.route('/')
def home():
    """Endpoint raíz que muestra los endpoints disponibles."""
    return jsonify({
        "mensaje": "API de Sensores y Actuadores",
        "endpoints": {
            "potenciometro": "/api/potentiometer",
            "ultrasonico": "/api/ultrasonic"
        }
    })

@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    """
    Endpoint para obtener el valor actual del potenciómetro en porcentaje.
    """
    try:
        # La lectura ahora usa los valores de calibración
        current_percentage = pot.get_percentage()
        raw_value = pot.get_raw_value()
        
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value_percentage': current_percentage,
            'value_raw': raw_value
        }
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor: {str(e)}'
        }
        return jsonify(error_response), 500


@app.route('/api/ultrasonic', methods=['GET'])
def get_ultrasonic_distance():
    """
    Endpoint para obtener la distancia del sensor ultrasónico en cm.
    """
    try:
        distance = ultra_sensor.get_distance()
        
        response = {
            'status': 'success',
            'sensor': 'ultrasonic',
            'value': distance,
            'unit': 'cm'
        }
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor: {str(e)}'
        }
        return jsonify(error_response), 500

# --- Punto de entrada ---

if __name__ == '__main__':
    try:
        print("Iniciando calibración del potenciómetro...")
        pot.calibrate()
        print("Calibración finalizada.")

        print(f"\nIniciando servidor Flask en http://0.0.0.0:5000")
        print(f"Controlando Potenciómetro en Pin BCM: {POT_PIN}")
        print(f"Controlando Ultrasónico en Pins BCM: TRIG={ULTRA_TRIG_PIN}, ECHO={ULTRA_ECHO_PIN}")
        
        # use_reloader=False es importante para evitar que Flask reinicie
        # y cause conflictos con los pines GPIO.
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    
    finally:
        # GPIO.cleanup() limpiará TODOS los pines que usamos.
        print("Limpiando pines GPIO...")
        GPIO.cleanup()
        print("¡Hasta luego!")