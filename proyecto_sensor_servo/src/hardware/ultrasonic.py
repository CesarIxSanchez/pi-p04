"""
Módulo para la clase UltrasonicSensor (HC-SR04).
Encapsula la lógica para medir distancias.
"""
import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    """
    Clase para gestionar la lectura de un sensor de distancia
    ultrasónico HC-SR04.
    """

    def __init__(self, trig_pin, echo_pin):
        """
        Inicializa el sensor.

        :param trig_pin: El pin GPIO (BCM) de Trigger.
        :param echo_pin: El pin GPIO (BCM) de Echo.
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        """
        Realiza una medición de distancia.

        :return: La distancia medida en centímetros.
        :rtype: float
        """
        # Asegurar que el Trigger esté bajo
        GPIO.output(self.trig_pin, False)
        time.sleep(0.2) # Pausa para estabilizar

        # Enviar un pulso de 10us al Trigger
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001) # 10 microsegundos
        GPIO.output(self.trig_pin, False)

        pulse_start_time = time.time()
        pulse_end_time = time.time()

        # Grabar el último tiempo LOW ANTES de que el pulso ECHO comience
        while GPIO.input(self.echo_pin) == 0:
            pulse_start_time = time.time()
            # Romper si el pulso nunca inicia (sensor desconectado)
            if pulse_start_time - pulse_end_time > 0.1:
                raise TimeoutError("Timeout esperando inicio de pulso ECHO")

        # Grabar el tiempo cuando el pulso ECHO termina
        while GPIO.input(self.echo_pin) == 1:
            pulse_end_time = time.time()
            # Romper si el pulso nunca termina
            if pulse_end_time - pulse_start_time > 0.1:
                raise TimeoutError("Timeout esperando fin de pulso ECHO")

        # Calcular la duración del pulso
        pulse_duration = pulse_end_time - pulse_start_time
        
        # Calcular distancia:
        # Distancia = (Tiempo * VelocidadDelSonido) / 2
        # Velocidad del sonido = 34300 cm/s
        distance = (pulse_duration * 34300) / 2
        
        return round(distance, 2) # Redondear a 2 decimales