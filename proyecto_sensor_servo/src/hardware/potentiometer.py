"""
Módulo para la clase Potentiometer.
Encapsula la lógica para leer un potenciómetro usando un circuito RC
en una Raspberry Pi.
"""
import RPi.GPIO as GPIO
import time

class Potentiometer:
    """
    Clase para gestionar la lectura de un potenciómetro en una Raspberry Pi
    mediante un método de carga/descarga de condensador (circuito RC).
    """

    def __init__(self, pin):
        """
        Inicializa el potenciómetro.

        :param pin: El número de pin GPIO (en modo BCM) al que está conectado.
        """
        self.pin = pin
        self.min_value = 0  # Valor crudo mínimo después de la calibración
        self.max_value = 100 # Valor crudo máximo (default hasta calibrar)
        self._last_raw_value = 0 # Almacena la última lectura cruda

    def _read_raw_value(self):
        """
        Realiza la lectura del circuito RC y devuelve el conteo crudo.
        Actualiza el valor interno _last_raw_value.

        :return: Un entero (conteo) que es proporcional a la resistencia.
        :rtype: int
        """
        count = 0
        
        # Descargar el condensador
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)
        time.sleep(0.01) # Reducido para lecturas más rápidas
        
        # Poner el pin en modo entrada para leer la carga
        GPIO.setup(self.pin, GPIO.IN)
        
        # Contar el tiempo que tarda en cargarse (pasar a HIGH)
        while GPIO.input(self.pin) == GPIO.LOW:
            count += 1
            if count > 100000: # Timeout de seguridad (para 10k pot)
                print("Advertencia: Timeout en la lectura del potenciómetro.")
                # Si hay timeout, usar el valor de timeout,
                # probablemente es el máximo.
                break
        
        self._last_raw_value = count
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
            print("Usando valores por defecto. Reintenta la calibración.")
            self.min_value = 0
            self.max_value = self.min_value + 100 # Un rango pequeño por defecto
        
        print(f"\nCalibración completada: Rango [{self.min_value}, {self.max_value}]")

    def get_percentage(self):
        """
        Obtiene el valor actual del potenciómetro como un porcentaje (0.0 a 100.0).
        Utiliza los valores de calibración para normalizar el dato crudo.

        :return: El valor normalizado en porcentaje.
        :rtype: float
        """
        value = self._read_raw_value()
        
        # Evitar división por cero si la calibración fue mala
        range_span = self.max_value - self.min_value
        if range_span <= 0:
            return 0.0

        # Normalizar el valor
        normalized = (value - self.min_value) / range_span * 100.0
        
        # Asegurar que el valor esté siempre entre 0 y 100
        normalized = max(0.0, min(100.0, normalized))
        
        return round(normalized, 2) # Redondear a 2 decimales

    def get_raw_value(self):
        """
        Obtiene el valor crudo de la última lectura del sensor.
        No ejecuta una nueva lectura, usa el valor almacenado por
        get_percentage() o _read_raw_value().
        
        :return: El último conteo crudo.
        :rtype: int
        """
        return self._last_raw_value