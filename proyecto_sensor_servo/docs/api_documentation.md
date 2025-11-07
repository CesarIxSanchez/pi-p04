# Documentación de la API - Sensor/Actuador

Esta documentación describe la API RESTful expuesta por el servidor Flask (src/api/sensor_api.py) que se ejecuta en la Raspberry Pi.

URL Base: http://<IP_DE_LA_RASPI>:5000

## 1. Endpoint: Potenciómetro

Obtiene la lectura actual del potenciómetro, calibrada y en valor crudo.

- Ruta: /api/potentiometer

- Método: GET

Respuesta Exitosa (Código 200)

El sensor fue leído correctamente.

Cuerpo (JSON):

{
  "status": "success",
  "sensor": "potentiometer",
  "value_percentage": 75.38,
  "value_raw": 72010
}


Campos:

- status: "success"

- sensor: "potentiometer"

- value_percentage: (float) Valor normalizado (0.0-100.0) basado en la calibración física.

- value_raw: (int) El conteo crudo devuelto por el circuito RC.

## 2. Endpoint: Sensor Ultrasónico

Obtiene la distancia medida por el sensor HC-SR04.

- Ruta: /api/ultrasonic

- Método: GET

Respuesta Exitosa (Código 200)

El sensor midió la distancia correctamente.

Cuerpo (JSON):

{
  "status": "success",
  "sensor": "ultrasonic",
  "value": 25.12,
  "unit": "cm"
}


Campos:

- status: "success"

- sensor: "ultrasonic"

- value: (float) La distancia medida en centímetros.

- unit: "cm"

## 3. Respuestas de Error (Código 500)

Ocurre si el hardware falla o no se puede comunicar con un sensor.

Cuerpo (JSON):

{
  "status": "error",
  "message": "No se pudo leer el sensor: [descripción del error]"
}


Campos:

- status: "error"

- message: (string) Un mensaje describiendo qué salió mal.