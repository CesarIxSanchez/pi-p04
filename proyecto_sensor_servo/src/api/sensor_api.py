import RPi.GPIO as GPIO

from flask import Flask, jsonify
from ..hardware.potentiometer import Potentiometer

# 1. Inicializar Flask y el Hardware (el simulador por ahora)
app = Flask(__name__)
POT_PIN = 17
pot = Potentiometer() # Cuando tengas tu clase real, esto no cambia

# Calibrar cada vez que inicies el servidor
print("Calibrando potenciómetro... sigue las instrucciones.")
pot.calibrate()
print("Calibración lista. Iniciando API.")


# 2. Definir el Endpoint de la API
@app.route('/api/potentiometer', methods=['GET'])
def get_potentiometer_value():
    
   
    try:
        # Llama al método de tu clase (ya sea la real o la simulada)
        current_value = pot.get_percentage()
        
        # Prepara una respuesta JSON exitosa
        response = {
            'status': 'success',
            'sensor': 'potentiometer',
            'value': current_value
        }
        return jsonify(response), 200

    except Exception as e:
        # Manejo de errores
        error_response = {
            'status': 'error',
            'message': f'No se pudo leer el sensor: {str(e)}'
        }
        return jsonify(error_response), 500


# 3. Punto de entrada para ejecutar el servidor
if __name__ == '__main__':
    try:
            print(f"Iniciando servidor Flask en http://0.0.0.0:5000")
            print(f"Controlando Potenciómetro en Pin BCM: {POT_PIN}")
            
            # 'use_reloader=False' evita que el 'debug=True' ejecute el script dos veces,
            # lo cual es importante para no intentar configurar los pines GPIO dos veces.
            app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

    except KeyboardInterrupt:
            # Esto se activa cuando presionas Ctrl+C en la terminal
            print("\nServidor detenido por el usuario.")
        
    finally:
            # BUENA PRÁCTICA: Limpiar los pines GPIO al salir
            print("Limpiando pines GPIO...")
            GPIO.cleanup()
            print("¡Hasta luego!")
