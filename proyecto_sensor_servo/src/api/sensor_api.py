"""
Servidor Flask (API)
Este script inicia un servidor web que expone los datos de los sensores
conectados a la Raspberry Pi (Potenciómetro y Ultrasónico).

Debe ejecutarse en la Raspberry Pi.
Ejecución: python src/api/sensor_api.py
"""
import RPi.GPIO as GPIO
import time
import sys
import os
from flask import Flask, jsonify

# --- Importaciones del Proyecto ---
# Añadir la carpeta 'src' al path de Python para encontrar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from hardware.potentiometer import Potentiometer
    from hardware.ultrasonic import UltrasonicSensor
except ImportError as e:
    print("Error: No se pudieron importar los módulos de hardware.")
    print(f"Detalle: {e}")
    sys.exit(1)


# --- Configuración del Hardware ---
POT_PIN = 4

# Pines del Sensor Ultrasónico
ULTRA_TRIG_PIN = 23
ULTRA_ECHO_PIN = 24

# --- Inicialización de la App ---
app = Flask(__name__)

# --- Configuración de GPIO ---
# Se configura el modo BCM una sola vez aquí
try:
    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print(f"Advertencia: Modo GPIO ya configurado o error: {e}")

# --- Instancias de Hardware ---
# 1. Crear instancia del Potenciómetro
pot = Potentiometer(pin=POT_PIN)

# 2. Crear instancia del Sensor Ultrasónico
ultra_sensor = UltrasonicSensor(trig_pin=ULTRA_TRIG_PIN, echo_pin=ULTRA_ECHO_PIN)


# --- Endpoints de la API ---

@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    """
    Endpoint para obtener el valor actual del potenciómetro.
    Devuelve tanto el valor crudo como el porcentaje calibrado.

    :return: JSON con los datos del sensor o un error.
    """
    try:
        # Obtener valores de la clase Potentiometer
        raw_value = pot.get_raw_value()
        percent_value = pot.get_percentage_from_raw(raw_value) # Usar el valor crudo ya leído
        
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value_percentage': round(percent_value, 2), # Redondear a 2 decimales
            'value_raw': raw_value
        }
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor potenciómetro: {str(e)}'
        }
        return jsonify(error_response), 500


@app.route('/api/ultrasonic', methods=['GET'])
def get_ultrasonic_distance():
    """
    Endpoint para obtener la distancia del sensor ultrasónico en cm.

    :return: JSON con los datos del sensor o un error.
    """
    try:
        # Obtener distancia de la clase UltrasonicSensor
        distance = ultra_sensor.get_distance()
        
        response = {
            'status': 'success',
            'sensor': 'ultrasonic',
            'value': round(distance, 2), # Redondear a 2 decimales
            'unit': 'cm'
        }
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor ultrasónico: {str(e)}'
        }
        return jsonify(error_response), 500


# --- Punto de entrada del Servidor ---

if __name__ == '__main__':
    try:
        # --- CALIBRACIÓN ---
        # El servidor debe calibrar el potenciómetro antes de empezar a servir.
        print("-" * 30)
        pot.calibrate() # Ejecutar la calibración física
        print("-" * 30)
        
        print(f"\nIniciando servidor Flask en http://0.0.0.0:5000")
        print(f"Controlando Potenciómetro en Pin BCM: {POT_PIN}")
        print(f"Controlando Ultrasónico en Pins BCM: TRIG={ULTRA_TRIG_PIN}, ECHO={ULTRA_ECHO_PIN}")
        
        # Ejecutar la app
        # debug=False es importante para producción y para evitar que el calibrado se ejecute dos veces
        # use_reloader=False es vital para que RPi.GPIO no de errores de "canal en uso"
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    
    finally:
        # Limpiar TODOS los pines GPIO al cerrar el servidor
        print("Limpiando pines GPIO...")
        GPIO.cleanup()
        print("¡Hasta luego!")