

# Esquema para una respuesta exitosa del potenciómetro
POTENTIOMETER_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Indica el resultado de la operación",
            "enum": ["success"]  # El valor solo puede ser "success"
        },
        "sensor": {
            "type": "string",
            "description": "Nombre del sensor consultado",
            "enum": ["potentiometer"]
        },
        "value": {
            "type": "number",
            "description": "Valor actual del sensor (ej. 0-1023)",
        }
    },
    "required": ["status", "sensor", "value"] # Todos estos campos son obligatorios
}


# Esquema para una respuesta de error genérica
ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Indica el resultado de la operación",
            "enum": ["error"] # El valor solo puede ser "error"
        },
        "message": {
            "type": "string",
            "description": "Mensaje descriptivo del error"
        }
    },
    "required": ["status", "message"] # Ambos campos son obligatorios
}
