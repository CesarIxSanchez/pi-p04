"""
Módulo para la clase Servo.
Encapsula la lógica para controlar un servomotor (ej. SG90) usando PWM.
"""
import RPi.GPIO as GPIO
import time
import logging

# Configurar el logging básico para este módulo
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [Servo] - %(levelname)s - %(message)s'
)

class Servo:
    """
    Clase para controlar un servomotor usando PWM en la Raspberry Pi.
    """

    def __init__(self, pin, min_angle=0, max_angle=180, min_duty=2, max_duty=12):
        """
        Inicializa el servomotor.

        :param pin: El pin GPIO (BCM) al que está conectado el servo.
        :param min_angle: El ángulo mínimo (límite de seguridad).
        :param max_angle: El ángulo máximo (límite de seguridad).
        :param min_duty: El ciclo de trabajo PWM para el ángulo mínimo (default: 2).
        :param max_duty: El ciclo de trabajo PWM para el ángulo máximo (default: 12).
        """
        self.pin = pin
        
        # Límites de seguridad
        self.min_angle = min_angle
        self.max_angle = max_angle
        
        # Rango de PWM (Duty Cycle)
        self.min_duty = min_duty
        self.max_duty = max_duty
        
        GPIO.setup(self.pin, GPIO.OUT)
        
        # Inicializar PWM a 50Hz (estándar para servos)
        self.pwm = GPIO.PWM(self.pin, 50) 
        self.pwm.start(0) # Iniciar el PWM pero sin enviar señal (ciclo 0)
        logging.info(f"Servo inicializado en pin {self.pin} (Rango: {min_angle}°-{max_angle}°)")

    def _angle_to_duty_cycle(self, angle):
        """
        Convierte un ángulo (0-180) a un ciclo de trabajo PWM.
        
        :param angle: El ángulo deseado.
        :return: El ciclo de trabajo (duty cycle) correspondiente.
        :rtype: float
        """
        # Mapeo lineal del ángulo al ciclo de trabajo
        duty_range = self.max_duty - self.min_duty
        angle_range = self.max_angle - self.min_angle
        
        if angle_range == 0:
            return self.min_duty
            
        duty = (((angle - self.min_angle) * duty_range) / angle_range) + self.min_duty
        return duty

    def set_angle(self, angle):
        """
        Mueve el servo a un ángulo específico, respetando los límites.
        
        :param angle: El ángulo al que se debe mover el servo.
        :type angle: float
        """
        # --- Mecanismo de seguridad ---
        clamped_angle = max(self.min_angle, min(self.max_angle, angle))
        
        if clamped_angle != angle:
            logging.warning(f"Ángulo solicitado ({angle}°) fuera de límites. Ajustando a {clamped_angle}°")
        
        angle_to_set = clamped_angle
        duty_cycle = self._angle_to_duty_cycle(angle_to_set)
        
        # Enviar el pulso
        self.pwm.ChangeDutyCycle(duty_cycle)
        
        # --- Logging del movimiento ---
        logging.info(f"Moviendo a {angle_to_set:.1f}° (Duty Cycle: {duty_cycle:.2f})")
        
        # Pausa para que el servo llegue a la posición
        time.sleep(0.5) 
        
        # Apagar el pulso para evitar "jitter" (temblor)
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        """
        Detiene el PWM y libera el pin del servo.
        No llama a GPIO.cleanup() general, para no afectar a otros módulos.
        """
        self.pwm.stop()
        logging.info(f"Señal PWM detenida para el servo en pin {self.pin}.")