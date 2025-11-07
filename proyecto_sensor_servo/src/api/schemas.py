"""
Define los esquemas JSON esperados para las respuestas de la API.
"""

# Esquema para una respuesta exitosa del potenciómetro
POTENTIOMETER_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Indica el resultado de la operación",
            "enum": ["success"]
        },
        "sensor": {
            "type": "string",
            "description": "Nombre del sensor consultado",
            "enum": ["potentiometer"]
        },
        "value_percentage": {
            "type": "number",
            "description": "Valor normalizado (0.0-100.0) basado en calibración",
        },
        "value_raw": {
            "type": "integer",
            "description": "Conteo crudo de la lectura del sensor",
        }
    },
    "required": ["status", "sensor", "value_percentage", "value_raw"]
}

# --- Esquema para el sensor ultrasónico ---
ULTRASONIC_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Indica el resultado de la operación",
            "enum": ["success"]
        },
        "sensor": {
            "type": "string",
            "description": "Nombre del sensor consultado",
            "enum": ["ultrasonic"]
        },
        "value": {
            "type": "number",
            "description": "Distancia medida por el sensor",
        },
        "unit": {
            "type": "string",
            "description": "Unidad de medida",
            "enum": ["cm"]
        }
    },
    "required": ["status", "sensor", "value", "unit"]
}

# Esquema para una respuesta de error genérica
ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Indica el resultado de la operación",
            "enum": ["error"]
        },
        "message": {
            "type": "string",
            "description": "Mensaje descriptivo del error"
        }
    },
    "required": ["status", "message"]
}