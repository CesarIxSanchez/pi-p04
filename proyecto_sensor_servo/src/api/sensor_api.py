import RPi.GPIO as GPIO
import time
import sys
import os
from flask import Flask, jsonify

# --- Importaciones ---

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from hardware.potentiometer import Potentiometer
except ImportError as e:
    print("Error: No se pudo importar 'Potentiometer'.")
    print(f"Detalle: {e}")
    sys.exit(1)


# --- Configuración del Hardware ---
# Volvemos al pin original del potenciómetro
POT_PIN = 4  

# --- Inicialización de la App ---
app = Flask(__name__)

# --- Configuración de GPIO ---
try:
    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print(f"Advertencia: Modo GPIO ya configurado o error: {e}")

# --- Instancias de Hardware ---
# 1. Crear instancia del Potenciómetro
pot = Potentiometer(pin=POT_PIN)


# --- Endpoints de la API ---

@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    """
    Endpoint para obtener el valor actual del potenciómetro.
    Devuelve tanto el valor crudo como el porcentaje calibrado.

    :return: JSON con los datos del sensor o un error.
    """
    try:
        raw_value = pot.get_raw_value()
        percent_value = pot.get_percentage_from_raw(raw_value)
        
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value_percentage': round(percent_value, 2),
            'value_raw': raw_value
        }
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor potenciómetro: {str(e)}'
        }
        return jsonify(error_response), 500


# --- Punto de entrada del Servidor ---

if __name__ == '__main__':
    try:
        print("-" * 30)
        pot.calibrate() # Ejecutar la calibración física
        print("-" * 30)
        
        print(f"\nIniciando servidor Flask en http://0.0.0.0:5000")
        print(f"Controlando Potenciómetro en Pin BCM: {POT_PIN}")
        
        # Ejecutar la app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    
    finally:
        # Limpiar TODOS los pines GPIO al cerrar el servidor
        print("Limpiando pines GPIO...")
        GPIO.cleanup()
        print("¡Hasta luego!")