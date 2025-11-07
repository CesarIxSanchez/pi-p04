import RPi.GPIO as GPIO
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

class Potentiometer:
    """
    Clase para gestionar la lectura de un potenciómetro en una Raspberry Pi
    """

    def __init__(self, pin):
        """
        Inicializa el potenciómetro.

        """
        self.pin = pin
        self.min_value = 0   # Valor crudo mínimo después de la calibración
        self.max_value = 100 # Valor crudo máximo después de la calibración
        

    def _read_raw_value(self):
        """
        Realiza la lectura del circuito RC y devuelve el conteo crudo.
        """
        count = 0
        
        # Descargar el condensador
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)
        time.sleep(0.1)  
        
        # Poner el pin en modo entrada para leer la carga
        GPIO.setup(self.pin, GPIO.IN)
        
        # Contar el tiempo que tarda en cargarse (pasar a HIGH)
        while GPIO.input(self.pin) == GPIO.LOW:
            count += 1
            if count > 100000: # Timeout de seguridad
                logging.warning("Timeout en la lectura del potenciómetro.")
                break
        return count

    def calibrate(self):
        """
        Inicia el proceso de calibración guiado por el usuario para
        establecer los valores mínimos y máximos de resistencia.
        """
        print("Iniciando calibración...")
        print("Gira el potenciómetro al MÍNIMO (izquierda) y espera 3 segundos...")
        time.sleep(3)
        self.min_value = self._read_raw_value()
        print(f"Valor mínimo registrado: {self.min_value}")
        
        print("\nGira el potenciómetro al MÁXIMO (derecha) y espera 3 segundos...")
        time.sleep(3)
        self.max_value = self._read_raw_value()
        print(f"Valor máximo registrado: {self.max_value}")

        # Comprobación de seguridad para evitar división por cero
        if self.max_value <= self.min_value:
            print("¡Error de calibración! El valor máximo no es mayor que el mínimo.")
            print("Usando valores por defecto (0-100). Reintenta la calibración.")
            self.min_value = 0
            self.max_value = 100
        
        print(f"\nCalibración completada: Rango [{self.min_value}, {self.max_value}]")

    def get_percentage_from_raw(self, raw_value):
        """
        Calcula el porcentaje (0.0-100.0) basado en un valor crudo ya leído.
        

        """
        # Evitar división por cero si la calibración fue mala
        range_span = self.max_value - self.min_value
        if range_span <= 0:
            return 0.0

        # Normalizar el valor
        normalized = (raw_value - self.min_value) / range_span * 100.0
        
        # Asegurar que el valor esté siempre entre 0 y 100
        normalized = max(0.0, min(100.0, normalized))
        
        return normalized

    def get_percentage(self):
        """
        Obtiene el valor actual del potenciómetro como un porcentaje (0.0 a 100.0).
        Realiza una nueva lectura de sensor.

        """
        value = self._read_raw_value()
        return self.get_percentage_from_raw(value)

    def get_raw_value(self):
        """
        Obtiene el valor crudo actual del sensor.
        Realiza una nueva lectura de sensor.

        """
        return self._read_raw_value()