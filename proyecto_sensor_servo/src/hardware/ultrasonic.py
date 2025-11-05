# src/hardware/ultrasonic.py

import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    """
    Clase para gestionar un sensor ultrasónico HC-SR04 en una Raspberry Pi.
    """

    def __init__(self, trig_pin, echo_pin):
        """
        Inicializa el sensor.

        :param trig_pin: El pin GPIO (BCM) para el Trigger (salida).
        :param echo_pin: El pin GPIO (BCM) para el Echo (entrada).
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        # Configurar pines
        # (Asumimos que GPIO.setmode(GPIO.BCM) se llamó en otro lugar,
        # como en el __init__ del Potenciometro o en el main de la API)
        try:
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
        except Exception as e:
            print(f"Advertencia: Problema al configurar pines de ultrasonido: {e}")
            print("Asegúrate de que GPIO.setmode(GPIO.BCM) se haya llamado.")

        # Asegurar que el trigger esté bajo al inicio
        GPIO.output(self.trig_pin, False)
        print("Sensor Ultrasónico: Esperando 1 segundo para estabilizar...")
        time.sleep(1) # Pequeña pausa para que el sensor se estabilice

    def get_distance(self):
        """
        Mide la distancia actual en centímetros.

        :return: La distancia medida en cm.
        :rtype: float
        """
        
        # 1. Enviar un pulso de 10us al pin Trigger
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001) # Pulso de 10 microsegundos
        GPIO.output(self.trig_pin, False)

        # 2. Medir el tiempo que el pin Echo está en ALTO (HIGH)
        
        # Guardar el tiempo de inicio cuando Echo es BAJO
        start_time = time.time()
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
            # (Podríamos añadir un timeout de seguridad aquí)

        # Guardar el tiempo final cuando Echo vuelve a ser BAJO
        stop_time = time.time()
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()
            # (Podríamos añadir un timeout de seguridad aquí)

        # 3. Calcular la duración del pulso
        time_elapsed = stop_time - start_time
        
        # 4. Calcular la distancia
        # La velocidad del sonido es ~34300 cm/s
        # La distancia es (Tiempo * VelocidadSonido) / 2 (porque es ida y vuelta)
        distance = (time_elapsed * 34300) / 2

        return round(distance, 2) # Devolver con 2 decimales