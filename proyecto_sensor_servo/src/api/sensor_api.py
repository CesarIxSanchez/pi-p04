# src/api/sensor_api.py

from flask import Flask, jsonify
import RPi.GPIO as GPIO


from ..hardware.potentiometer import Potentiometer
from ..hardware.ultrasonic import UltrasonicSensor # <-- AÑADE ESTA LÍNEA

app = Flask(__name__)

# --- Configuración del Hardware ---

POT_PIN = 17 
pot = Potentiometer(pin=POT_PIN)

# Sensor
ULTRA_TRIG_PIN = 23
ULTRA_ECHO_PIN = 24
# Crea una instancia del nuevo sensor
ultra_sensor = UltrasonicSensor(trig_pin=ULTRA_TRIG_PIN, echo_pin=ULTRA_ECHO_PIN) # <-- AÑADE ESTA LÍNEA


# --- Endpoints de la API ---

# Endpoint del Potenciómetro 
@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    """
    Endpoint para obtener el valor actual del potenciómetro en porcentaje.
    """
    try:
        current_value = pot.get_percentage()
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value': current_value  
        }
        return jsonify(response), 200
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor: {str(e)}'
        }
        return jsonify(error_response), 500


# Endpoint para el ultrasonido ---

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


# --- Punto de entrada 

if __name__ == '__main__':
    try:
        print(f"Iniciando servidor Flask en http://0.0.0.0:5000")
        print(f"Controlando Potenciómetro en Pin BCM: {POT_PIN}")
        

        print(f"Controlando Ultrasónico en Pins BCM: TRIG={ULTRA_TRIG_PIN}, ECHO={ULTRA_ECHO_PIN}") # <-- AÑADE ESTA LÍNEA
        
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    
    finally:
        # GPIO.cleanup() limpiará TODOS los pines que usamos.
        print("Limpiando pines GPIO...")
        GPIO.cleanup()
        print("¡Hasta luego!")
